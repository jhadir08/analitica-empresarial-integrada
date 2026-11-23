const el = id => document.getElementById(id);
const node = (tag, text) => Object.assign(document.createElement(tag), {textContent:text ?? ''});
const fmt = (n, digits=0) => Number(n).toLocaleString('es-PE',{maximumFractionDigits:digits});
const money = n => 'S/ '+fmt(n,2);
const percent = n => n == null ? '—' : fmt(n*100,1)+' %';
let data;
async function api(path, options) {
  const response = await fetch('/api/'+path, options);
  if (!response.ok) {
    const failure=await response.json().catch(()=>({}));
    throw Error(typeof failure.detail==='string'?failure.detail:'El servicio no respondió. Intenta nuevamente.');
  }
  return response.json();
}
function table(id, columns, rows) {
  const wrap = node('div'); wrap.className='scroll';
  const table = node('table');
  const heading = table.createTHead().insertRow();
  for (const [label] of columns) heading.append(node('th',label));
  const body=table.createTBody();
  for (const record of rows) {
    const row=body.insertRow();
    for (const [,value] of columns) row.insertCell().textContent=value(record);
  }
  wrap.append(table); el(id).replaceChildren(wrap);
}
function barChart(id, entries) {
  const largest = Math.max(1,...entries.map(([,v])=>v));
  el(id).replaceChildren(...entries.map(([label,value])=>{
    const bar=node('div'); bar.className='bar';
    const height=node('em'); height.style.height=(100*value/largest)+'px';
    bar.append(node('b',fmt(value)),height,node('span',label)); return bar;
  }));
}
function demand() {
  const zone=el('zona').value;
  const rows=data.pronostico.filter(r=>zone==='Todas'||r.zona===zone);
  const weekly=new Map();
  for (const r of rows) weekly.set(r.semana,(weekly.get(r.semana)||0)+r.unidades);
  barChart('grafico',[...weekly].sort().map(([week,v])=>[week.slice(8)+' nov.',v]));
  const lines=new Map();
  for (const r of rows) {
    const key=r.zona+' / '+r.familia;
    lines.set(key,{zona:r.zona,familia:r.familia,unidades:(lines.get(key)?.unidades||0)+r.unidades});
  }
  table('tabla-demanda',[['Zona',r=>r.zona],['Familia',r=>r.familia],['Unidades en 4 semanas',r=>fmt(r.unidades)]],lines.values());
}
function optimization() {
  const scale=Number(el('capacidad').value), effect=Number(el('efecto').value);
  const rows=data.escenarios.filter(r=>r.capacidad===scale&&r.efecto===effect);
  table('tabla-optim',[
    ['Política',r=>r.politica],['Contactos',r=>fmt(r.contactos)],['Valor retención',r=>money(r.retencion_6m)],
    ['Margen operativo',r=>money(r.margen_4s)],['Compra',r=>money(r.compra)],['Carga',r=>fmt(r.kg,1)+' / '+fmt(r.max_kg)+' kg'],
    ['Reparto',r=>fmt(r.horas,1)+' / '+fmt(r.max_horas)+' h']],rows);
  table('tabla-despachos',[['Zona',r=>r.zona],['Familia',r=>r.familia],['Solicitado',r=>fmt(r.solicitado)],['Despacho propuesto',r=>fmt(r.despacho)]],
    data.despachos.filter(r=>r.capacidad===scale&&r.politica==='Propuesta'));
}
function chartControl(zone, rows) {
  const section=node('div'); section.style.flex='1'; section.style.minWidth='145px';
  section.append(node('h3',zone));
  const ns='http://www.w3.org/2000/svg';
  const svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox','0 0 480 166');
  svg.setAttribute('role','img');
  svg.setAttribute('aria-label','Media semanal y límites de control de '+zone);
  const hi=Math.max(...rows.map(r=>Math.max(r.media,r.lcs)))+2;
  const low=Math.max(0,Math.min(...rows.map(r=>Math.min(r.media,r.lci)))-2);
  const x=i=>20+i*440/Math.max(1,rows.length-1), y=v=>145-126*(v-low)/(hi-low);
  for (const [key,color] of [['lci','#b46a4c'],['lcs','#b46a4c'],['centro','#899994'],['media','#26563f']]) {
    const line=document.createElementNS(ns,'polyline');
    line.setAttribute('points',rows.map((r,i)=>x(i)+','+y(r[key])).join(' '));
    line.setAttribute('fill','none'); line.setAttribute('stroke',color);
    line.setAttribute('stroke-width',key==='media'?'2.5':'1.2');
    if(key==='lci'||key==='lcs')line.setAttribute('stroke-dasharray','5 4');
    svg.append(line);
  }
  rows.forEach((r,i)=>{
    if(!r.senal)return;
    const point=document.createElementNS(ns,'circle');
    for(const [k,v] of Object.entries({cx:x(i),cy:y(r.media),r:3,fill:'#a83e2b'}))point.setAttribute(k,v);
    const title=document.createElementNS(ns,'title');title.textContent=r.semana.slice(0,10)+' · '+fmt(r.media,1)+' h';point.append(title);
    svg.append(point);
  });
  section.append(svg,node('p','Enero–octubre 2026 · '+rows.filter(r=>r.senal).length+' señales'));
  return section;
}
function render() {
  const proposed=data.escenarios.find(r=>r.capacidad===1&&r.efecto===.04&&r.politica==='Propuesta');
  const cards=[
    ['Margen operativo',money(proposed.margen_4s),'Horizonte de cuatro semanas'],
    ['Retención esperada',money(proposed.retencion_6m),'Efecto supuesto de 4 %'],
    ['Cuentas por contactar',fmt(proposed.contactos),'Consentimiento verificado'],
    ['Unidades solicitadas',fmt(data.pronostico.reduce((s,r)=>s+r.unidades,0)),'Demanda pronosticada']
  ];
  el('kpis').replaceChildren(...cards.map(([label,value,note])=>{
    const card=node('div'); card.append(node('span',label),node('strong',value),node('small',note)); return card;
  }));
  el('modelo').textContent='Churn en la prueba · PR-AUC '+fmt(data.metricas.pr_auc,3)+' · Umbral económico '+fmt(data.metricas.umbral,2)+' · '+fmt(data.metricas.cuentas_riesgo)+' cuentas sobre el umbral';
  demand(); optimization();
  const unstable=data.carta_control.some(r=>!r.base_estable);
  el('nota-control').textContent=unstable?'Límites preliminares. La base histórica presenta señales y requiere revisión antes de automatizar alertas.':'Medias semanales y límites de control por zona.';
  el('carta').replaceChildren(...['Cusco ciudad','Valle Sagrado'].map(z=>chartControl(z,data.carta_control.filter(r=>r.sede===z&&!r.base))));
  table('tabla-alertas',[['Zona',r=>r.sede],['Proceso',r=>r.tipo.replaceAll('_',' ')],['Alertas',r=>fmt(r.alertas)]],data.anomalias);
  table('tabla-auditoria',[['Dimensión',r=>r.dimension.replaceAll('_',' ')],['Grupo',r=>r.subgrupo],
    ['n',r=>r.n],['Positivos',r=>r.positivos],['Negativos',r=>r.negativos],['Recall',r=>percent(r.recall)],
    ['Falsos positivos',r=>percent(r.fpr)],['Cobertura',r=>percent(r.cobertura)],['Muestra pequeña',r=>r.muestra_pequena?'Sí':'—']],data.auditoria);
  table('tabla-shap',[['Variable',r=>r.variable],['SHAP medio absoluto',r=>fmt(r.impacto_abs,3)],
    ['Dirección del modelo',r=>r.coeficiente_log_odds>0?'Aumenta el riesgo':'Reduce el riesgo']],data.shap);
  const tests=data.evaluacion_asistente;
  const select=el('casos-luna');
  for(const record of tests.filter(r=>r.motor==='gpt-6-luna')){
    const item=node('option',record.pregunta); item.value=record.pregunta; select.append(item);
  }
  el('selector-pregunta').hidden=false;
  el('acceso-luna').hidden=!data.luna_en_vivo;
  const engines=[...new Set(tests.map(r=>r.motor))];
  el('indicadores').textContent=engines.map(m=>{
    const rows=tests.filter(r=>r.motor===m);
    return m+' · '+rows.filter(r=>r.acierto).length+'/'+rows.length+' aciertos, '+rows.filter(r=>r.sin_sustento).length+' sin sustento';
  }).join(' | ');
  table('tabla-pruebas',[['Motor',r=>r.motor],['N.º',r=>r.id],['Pregunta',r=>r.pregunta],['Esperado',r=>r.esperado],
    ['Respuesta observada',r=>r.observado],['Fuente',r=>r.fuentes||'—'],['Resultado',r=>r.acierto?'Correcto':r.defecto]],tests);
}
async function loadAssistantEvidence() {
  const response = await fetch('/evidencia-asistente.json');
  if (!response.ok) throw Error('No se pudo cargar la evidencia de las preguntas nuevas.');
  const {evaluacion_externa_asistente: tests, registro_defectos: defects} = await response.json();
  const engines = ['gpt-6-luna', 'Determinista'];
  el('indicadores-externos').textContent = engines.map(engine => {
    const rows = tests.filter(r => r.motor === engine);
    const label = engine === 'gpt-6-luna' ? 'GPT-6 Luna' : 'Recuperación determinista';
    return label + ' · ' + rows.filter(r => r.acierto).length + '/' + rows.length + ' aciertos';
  }).join(' | ');
  table('tabla-pruebas-externas', [
    ['Caso', r => r.id], ['Motor', r => r.motor], ['Pregunta', r => r.pregunta],
    ['Esperado', r => r.esperado], ['Respuesta observada', r => r.observado],
    ['Fuente citada', r => r.fuentes || '—'], ['Resultado', r => r.acierto ? 'Correcto' : r.defecto]
  ], tests);
  table('tabla-defectos', [
    ['Caso', r => r.id], ['Tipo', r => r.tipo], ['Hallazgo', r => r.hallazgo],
    ['Evidencia', r => r.evidencia], ['Estado', r => r.estado]
  ], defects);
}
el('zona').addEventListener('change',()=>{if(data)demand()});
for(const id of ['capacidad','efecto'])el(id).addEventListener('change',()=>{if(data)optimization()});
document.querySelector('nav').addEventListener('click',event=>{
  if(event.target.tagName==='A') {
    document.querySelector('nav .activo')?.classList.remove('activo'); event.target.classList.add('activo');
  }
});
el('casos-luna').addEventListener('change',()=>{
  const value=el('casos-luna').value;
  if(!value)return;
  el('pregunta').value=value;
  if(!el('preguntar').hidden){el('preguntar').requestSubmit();return;}
  const saved=data.evaluacion_asistente.find(r=>r.motor==='gpt-6-luna'&&r.pregunta===value);
  el('respuesta').replaceChildren(node('p',saved.observado),node('p',saved.fuentes||'Abstención de la evaluación'));
});
el('preguntar').addEventListener('submit',async event=>{
  event.preventDefault();
  const button=event.currentTarget.querySelector('button');
  button.disabled=true;
  el('respuesta').textContent='Consultando políticas…';
  try {
    const ans=await api('asistente',{method:'POST',headers:{'Content-Type':'application/json','X-PMD2-Access':el('token-luna').value},body:JSON.stringify({pregunta:el('pregunta').value})});
    el('respuesta').replaceChildren(node('p',ans.texto),...ans.fuentes.map(s=>node('p',s.id+' v'+s.version+' · '+s.title)));
  } catch(error) { el('respuesta').textContent=error.message; }
  finally {button.disabled=false}
});
async function loadDashboard() {
  let live = true;
  try {
    data=await api('tablero');
  } catch {
    live=false;
    const snapshot=await fetch('/tablero.json');
    if (!snapshot.ok) throw Error('No se pudieron cargar los resultados del checkpoint.');
    data=await snapshot.json();
  }
  render();
  el('estado').hidden=live;
  if (!live) {
    el('estado').textContent='Vista de resultados del checkpoint. La consulta en vivo se habilita al conectar la API.';
    el('preguntar').hidden=true;
  }
}
loadDashboard().catch(error=>{el('estado').textContent=error.message;el('estado').className='status'});

loadAssistantEvidence().catch(() => {
  el('indicadores-externos').textContent = 'No se pudo cargar la evidencia de las preguntas nuevas.';
});
