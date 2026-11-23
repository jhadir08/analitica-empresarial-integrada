"""Análisis reproducible del caso Suministros Sur."""
import math
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import average_precision_score, confusion_matrix
from statsmodels.tsa.holtwinters import ExponentialSmoothing

SEED = 20261101
DECISION = pd.Timestamp("2026-11-01")
PLAN = pd.date_range("2026-11-02", periods=4, freq="7D")
FEATURES = ["recencia", "frecuencia", "ingreso180", "margen180", "retraso180", "creditos180"]


def customer_panel(data):
    events = data["actividad"].copy()
    events["fecha_entrega"] = pd.to_datetime(events.fecha_entrega)
    events["fecha_evento"] = pd.to_datetime(events.fecha_evento)
    orders = events.query("tipo_evento == 'pedido' and estado == 'entregado'").copy()
    orders["margen"] = orders.ingreso - orders.coste_variable
    orders["tarde"] = orders.dias_entrega > orders.plazo_prometido_dias
    credits = events.query("tipo_evento == 'nota_credito'").copy()
    cohort = data["cohortes"].assign(
        fecha_corte=lambda f: pd.to_datetime(f.fecha_corte),
        seguimiento_fin=lambda f: pd.to_datetime(f.seguimiento_fin),
    )
    cohort = cohort.query("elegible == 1").merge(data["clientes"], on="id_cliente", validate="many_to_one")
    frames = []
    for cut, rows in cohort.groupby("fecha_corte"):
        past = orders.loc[orders.fecha_entrega.lt(cut)]
        recent = past.loc[past.fecha_entrega.ge(cut - pd.Timedelta(days=180))]
        group = recent.groupby("id_cliente")
        features = group.agg(
            ultima=("fecha_entrega", "max"),
            frecuencia=("id_pedido", "nunique"),
            ingreso180=("ingreso", "sum"),
            margen180=("margen", "sum"),
            retraso180=("tarde", "mean"),
        )
        features["recencia"] = (cut - features.pop("ultima")).dt.days
        credit_window = credits.loc[credits.fecha_evento.ge(cut - pd.Timedelta(days=180)) & credits.fecha_evento.lt(cut)]
        features["creditos180"] = credit_window.groupby("id_cliente").id_evento.count()
        features["clv"] = (features.margen180 + credit_window.groupby("id_cliente").ingreso.sum().reindex(features.index, fill_value=0)).clip(lower=0)
        features["facturacion"] = past.groupby("id_cliente").ingreso.sum()
        qualifying = past.loc[past.fecha_entrega.ge(cut - pd.Timedelta(days=120))].groupby("id_cliente").id_pedido.nunique()
        features["pedidos120"] = qualifying
        # La elegibilidad oficial y la comprobación con pedidos distintos deben coincidir para entrar.
        merged = rows.merge(features, on="id_cliente", how="left")
        merged["creditos180"] = merged.creditos180.fillna(0)
        frames.append(merged)
    panel = pd.concat(frames, ignore_index=True)
    return panel, int(panel.pedidos120.fillna(0).lt(2).sum())


def binary(y, scores, threshold):
    tn, fp, fn, tp = confusion_matrix(y, scores >= threshold, labels=[0, 1]).ravel()
    return dict(tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp),
                precision=tp / (tp + fp) if tp + fp else 0,
                recall=tp / (tp + fn) if tp + fn else None,
                fpr=fp / (fp + tn) if fp + tn else None)


def churn(data):
    panel, excluded = customer_panel(data)
    panel = panel.loc[panel.pedidos120.ge(2)].copy()
    labeled = panel.loc[panel.seguimiento_fin.le(DECISION) & panel.churn.notna()].copy()
    ids = np.random.default_rng(SEED).permutation(sorted(data["clientes"].id_cliente.unique()))
    tr, va, te = np.split(ids, [int(.55*len(ids)), int(.77*len(ids))])
    train = labeled.loc[labeled.id_cliente.isin(tr) & labeled.fecha_corte.lt("2026-05-01")]
    valid = labeled.loc[labeled.id_cliente.isin(va) & labeled.fecha_corte.dt.to_period("M").eq("2026-05")]
    test = labeled.loc[labeled.id_cliente.isin(te) & labeled.fecha_corte.dt.to_period("M").eq("2026-06")].copy()
    cost = 12 + 35 * .30  # uso del incentivo supuesto
    model = make_pipeline(StandardScaler(), LogisticRegression(random_state=SEED))
    model.fit(train[FEATURES], train.churn)
    vp = model.predict_proba(valid[FEATURES])[:, 1]
    ev = vp * .04 * valid.clv - cost
    grid = []
    for t in [*np.linspace(0, 1, 21), 1.01]:
        mask = (vp >= t) & valid.consentimiento_contacto.eq(1) & ev.gt(0)
        ranked = ev[mask].nlargest(min(280, math.floor(6000/cost)))
        grid.append(dict(umbral=float(t), contactos=len(ranked), valor=float(ranked.sum()),
                         recall=binary(valid.churn, vp, t)["recall"]))
    grid = pd.DataFrame(grid)
    winner = grid.sort_values(["valor", "recall", "umbral"], ascending=[False, False, False]).iloc[0]
    threshold = float(winner.umbral)
    test["p"] = model.predict_proba(test[FEATURES])[:, 1]
    test["intervenir"] = test.p.ge(threshold) & test.consentimiento_contacto.eq(1) & (test.p*.04*test.clv > cost)
    portfolio = panel.loc[panel.fecha_corte.eq(DECISION)].copy()
    portfolio["p"] = model.predict_proba(portfolio[FEATURES])[:, 1]
    portfolio["riesgo"] = portfolio.p.ge(threshold)
    metrics = binary(test.churn, test.p, threshold)
    metrics.update(pr_auc=average_precision_score(test.churn, test.p),
                   pr_auc_recencia=average_precision_score(test.churn, test.recencia),
                   prevalencia=float(test.churn.mean()), umbral=threshold,
                   desajustes_elegibilidad=excluded, cuentas_cartera=len(portfolio),
                   cuentas_riesgo=int(portfolio.riesgo.sum()))
    splits = pd.DataFrame([dict(particion=k, filas=len(v), cuentas=v.id_cliente.nunique(),
                                positivos=int(v.churn.sum()), desde=v.fecha_corte.min().date(),
                                hasta=v.fecha_corte.max().date())
                           for k,v in zip(["Entrenamiento","Validación","Prueba"], [train,valid,test])])
    assert not (set(train.id_cliente) & set(valid.id_cliente) or set(train.id_cliente) & set(test.id_cliente) or set(valid.id_cliente) & set(test.id_cliente))
    return model, train, test, portfolio, grid, metrics, splits


def predict(series, method):
    if method == "Ingenuo reciente":
        return np.repeat(series.iloc[-1], 4)
    if method == "Ingenuo anual":
        return series.iloc[-52:-48].to_numpy()
    fit = ExponentialSmoothing(series.to_numpy(), trend="add", damped_trend=True,
                               seasonal="add", seasonal_periods=52).fit()
    return np.maximum(0, fit.forecast(4))


def forecast(demand):
    methods = ["Ingenuo reciente", "Ingenuo anual", "Holt-Winters"]
    history = demand.assign(semana=pd.to_datetime(demand.semana))
    errors, projections, selected, test_detail = [], [], [], []
    for (zone, family), rows in history.groupby(["sede", "linea"]):
        series = rows.set_index("semana").solicitado.sort_index().asfreq("W-MON")
        assert series.notna().all() and series.index[-1] + pd.Timedelta(days=7) == PLAN[0]
        validation = {}
        for method in methods:
            parts = []
            for fold in (16, 12, 8):
                actual = series.iloc[-fold:len(series)-fold+4]
                fit = predict(series.iloc[:-fold], method)
                residual = abs(actual.to_numpy()-fit)
                parts.extend(residual)
                errors.append([zone, family, method, f"Validación {actual.index[0].date()}",
                               residual.mean(), residual.sum()/actual.sum() if actual.sum() else None])
            validation[method] = np.mean(parts)
        best = min(validation, key=validation.get)
        selected.append([zone, family, best, validation[best]])
        actual = series.iloc[-4:]
        for method in methods:
            estimation = predict(series.iloc[:-4], method)
            residual = abs(actual.to_numpy()-estimation)
            errors.append([zone, family, method, "Prueba", residual.mean(), residual.sum()/actual.sum() if actual.sum() else None])
            test_detail.extend([zone, family, method, week.date().isoformat(), int(y), float(f), method==best]
                               for week,y,f in zip(actual.index,actual,estimation))
        projections.extend([zone, family, week.date().isoformat(), best, int(round(y))]
                           for week,y in zip(PLAN,predict(series,best)))
    return (pd.DataFrame(errors, columns=["zona","familia","modelo","periodo","mae","wape"]),
            pd.DataFrame(projections, columns=["zona","familia","semana","modelo","unidades"]),
            pd.DataFrame(selected, columns=["zona","familia","modelo","mae_validacion"]),
            pd.DataFrame(test_detail, columns=["zona","familia","modelo","semana","real","predicho","seleccionado"]))
