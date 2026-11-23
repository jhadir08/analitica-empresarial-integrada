"""Plan de retención, abastecimiento y vigilancia de entregas."""
import math
import numpy as np
import pandas as pd
import pulp as lp
from sklearn.ensemble import IsolationForest
from analysis import DECISION, SEED, binary


def optimize(data, projection, portfolio, threshold):
    resources = data["recursos"]
    inventory = resources.query("recurso == 'inventario'").set_index("linea")
    config = resources.loc[resources.linea.eq("todas")].set_index("recurso")
    zones = sorted(projection.zona.unique())
    families = list(inventory.index)
    top = config.limite
    coeff = config.consumo_unitario
    weight = inventory.consumo_unitario
    hour = coeff.horas_por_pedido / coeff.unidades_por_pedido + weight * coeff.horas_por_kg
    reserves = resources.query("recurso == 'reserva_capacidad_zona'").set_index("linea").consumo_unitario
    need = projection.groupby(["zona","familia"]).unidades.sum().to_dict()
    demand = data["demanda"].assign(semana=lambda f: pd.to_datetime(f.semana))
    last = sorted(demand.semana.unique())[-4:]
    historic = demand.loc[demand.semana.isin(last)].groupby(["sede","linea"]).solicitado.sum()
    baseline_buy = historic.groupby(level=1).sum()
    spending = float((baseline_buy * inventory.coste).sum())
    actual_buy = (baseline_buy * min(1, top.presupuesto_compra / spending)).astype(int)
    old_n = int(data["politica_actual"].query("alcance == 'contactos'").cantidades.iloc[0])
    old_raw = portfolio.sort_values(["facturacion","id_cliente"], ascending=[False,True]).head(old_n)
    allowed = portfolio.query("consentimiento_contacto == 1").copy()
    incumbent = old_raw.query("consentimiento_contacto == 1").copy()
    cost = float(config.loc["contacto_comercial","coste"]+config.loc["incentivo","coste"]*.30)
    rows, buys, roster = [], [], []

    for cap in (1.0, 1.0-float(coeff.reduccion_capacidad_logistica)):
        kg_limit, hours_limit = float(top.carga*cap), float(top.horas_reparto*cap)
        for policy in ("Actual ajustada", "Propuesta"):
            problem = lp.LpProblem("abastecimiento",lp.LpMaximize)
            buy = {f:lp.LpVariable(f"c_{i}",0,cat="Integer") for i,f in enumerate(families)}
            dispatch = {(z,f):lp.LpVariable(f"d_{i}_{j}",0,int(need[z,f]),cat="Integer")
                        for i,z in enumerate(zones) for j,f in enumerate(families)}
            procurement = lp.lpSum(inventory.loc[f,"coste"]*buy[f] for f in families)
            margin = lp.lpSum(inventory.loc[f,"margen"]*dispatch[z,f] for z,f in dispatch)
            problem += margin
            problem += procurement <= top.presupuesto_compra
            for f in families:
                problem += lp.lpSum(dispatch[z,f] for z in zones) <= inventory.loc[f,"disponibilidad"]+buy[f]
                if policy == "Actual ajustada":
                    problem += buy[f] == int(actual_buy[f])
            zone_kg = {z:lp.lpSum(weight[f]*dispatch[z,f] for f in families) for z in zones}
            zone_h = {z:lp.lpSum(hour[f]*dispatch[z,f] for f in families) for z in zones}
            problem += lp.lpSum(zone_kg.values()) <= kg_limit
            problem += lp.lpSum(zone_h.values()) <= hours_limit
            for z in zones:
                other = sum(reserves[o] for o in zones if o != z)
                problem += zone_kg[z] <= kg_limit*(1-other)
                problem += zone_h[z] <= hours_limit*(1-other)
            solver = lp.PULP_CBC_CMD(msg=False, threads=1)
            status = lp.LpStatus[problem.solve(solver)]
            assert status == "Optimal", status
            optimum = lp.value(margin)
            problem += margin >= optimum - 1e-7
            problem.sense = lp.LpMinimize
            problem.setObjective(procurement)
            assert lp.LpStatus[problem.solve(solver)] == "Optimal"
            assert all(c.valid(1e-5) for c in problem.constraints.values())
            for f in families:
                for z in zones:
                    buys.append(dict(capacidad=cap, politica=policy, zona=z, familia=f, solicitado=need[z,f],
                                     despacho=int(round(lp.value(dispatch[z,f]))),
                                     compra_familia=int(round(lp.value(buy[f])))))
            for effect in sorted(resources.query("recurso == 'efecto_incremental'").disponibilidad):
                if policy == "Propuesta":
                    candidates = allowed.assign(valor=allowed.p*effect*allowed.clv-cost)
                    candidates = candidates.loc[candidates.p.ge(threshold) & candidates.valor.gt(0)]
                    campaign = lp.LpProblem("retencion",lp.LpMaximize)
                    contact = {i:lp.LpVariable(f"x_{j}",cat="Binary") for j,i in enumerate(candidates.index)}
                    campaign += lp.lpSum(candidates.loc[i,"valor"]*x for i,x in contact.items())
                    campaign += lp.lpSum(contact.values()) <= top.contacto_comercial
                    campaign += cost*lp.lpSum(contact.values()) <= top.presupuesto_retencion
                    assert lp.LpStatus[campaign.solve(solver)] == "Optimal"
                    assert all(c.valid(1e-6) for c in campaign.constraints.values())
                    chosen = candidates.loc[[i for i,x in contact.items() if lp.value(x) > .5]]
                else:
                    chosen = incumbent.assign(valor=incumbent.p*effect*incumbent.clv-cost)
                if cap == 1 and abs(effect-.04)<1e-8:
                    for v in chosen.itertuples():
                        roster.append(dict(politica=policy,cuenta=v.id_cliente,zona=v.zona,riesgo=v.p,valor=v.valor))
                rows.append(dict(capacidad=cap, efecto=effect, politica=policy, solver=status,
                                 contactos=len(chosen), gasto_contactos=len(chosen)*cost,
                                 retencion_6m=float(chosen.valor.sum()), margen_4s=lp.value(margin),
                                 compra=lp.value(procurement), kg=sum(lp.value(v) for v in zone_kg.values()),
                                 horas=sum(lp.value(v) for v in zone_h.values()), max_kg=kg_limit,max_horas=hours_limit,
                                 kg_cusco=lp.value(zone_kg["Cusco ciudad"]), kg_valle=lp.value(zone_kg["Valle Sagrado"])))
    baseline = dict(contactos_reconstruidos=len(old_raw), excluidos_consentimiento=len(old_raw)-len(incumbent),
                    compra_bruta=float((baseline_buy*inventory.coste).sum()),
                    compra_bruta_unidades=int(baseline_buy.sum()))
    return pd.DataFrame(rows), pd.DataFrame(buys), pd.DataFrame(roster), baseline


def monitor(operations):
    frame = operations.assign(fecha=pd.to_datetime(operations.fecha_hora))
    frame["semana"] = frame.fecha.dt.to_period("W-SUN").dt.start_time
    baseline_end = pd.Timestamp("2026-01-05")
    alerts, limits = [], []
    for (zone, kind), group in frame.groupby(["sede","tipo"]):
        base = group.loc[group.semana.lt(baseline_end)]
        follow = group.loc[group.semana.ge(baseline_end)].copy()
        detector = IsolationForest(contamination=.025, random_state=SEED).fit(base[["valor"]])
        follow["score"] = -detector.decision_function(follow[["valor"]])
        follow = follow.loc[follow.score.gt(0)]
        alerts.append(follow[["id_operacion","sede","tipo","semana","valor","unidad","score"]])
        if kind != "tiempo_entrega_h":
            continue
        weeks = group.groupby("semana").valor.agg(media="mean",n="count",sd="std")
        model = weeks.loc[weeks.index < baseline_end]
        pooled = np.sqrt(((model.n-1)*model.sd.pow(2)).sum()/(model.n-1).sum())
        center = np.average(model.media,weights=model.n)
        distance = 3*pooled/np.sqrt(weeks.n)
        weeks = weeks.assign(sede=zone,base=weeks.index < baseline_end,centro=center,
                             lci=(center-distance).clip(lower=0), lcs=center+distance)
        weeks["senal"] = weeks.media.lt(weeks.lci) | weeks.media.gt(weeks.lcs)
        weeks["base_estable"] = len(model)>30 and not weeks.loc[weeks.base,"senal"].any()
        limits.append(weeks.reset_index().drop(columns="sd"))
    return pd.concat(alerts,ignore_index=True), pd.concat(limits,ignore_index=True)


def audit(test, threshold):
    rows=[]
    for dimension in ["zona","tamano_negocio","canal","segmento"]:
        for group, sample in test.groupby(dimension):
            record=binary(sample.churn,sample.p,threshold)
            rows.append(dict(dimension=dimension,subgrupo=group,n=len(sample),**record,
                             positivos=int(sample.churn.sum()), negativos=int(sample.churn.eq(0).sum()),
                             cobertura=float(sample.intervenir.mean()),
                             muestra_pequena=min(int(sample.churn.sum()),int(sample.churn.eq(0).sum()))<20))
    return pd.DataFrame(rows)
