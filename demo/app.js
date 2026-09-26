'use strict';
const D=window.ASSAY_DATA;
const el=id=>document.getElementById(id);
const names={random:'Random',greedy:'Greedy',uncertainty:'Uncertainty-only',diversity:'Diversity-only','coverage-only':'Coverage-only'};
let timer=null,sealedView=false;
function fill(id,values){el(id).replaceChildren(...values.map(([value,label])=>{const o=document.createElement('option');o.value=value;o.textContent=label;return o;}));}
fill('policy',D.methods.map(m=>[m,names[m]]));el('policy').value='coverage-only';fill('seed',Array.from({length:20},(_,i)=>[i,String(i)]));
function key(){return `${el('campaign').value}|${el('policy').value}|${el('seed').value}`;}
function stop(){if(timer!==null)clearInterval(timer);timer=null;el('play').textContent='Play recorded trace';}
function reset(){stop();sealedView=false;el('round').value=0;render();}
function render(){
 const round=Number(el('round').value),record=D.traces[key()],rows=D.rounds[key()];
 el('roundLabel').textContent=`${round} / 12`;el('budget').textContent=`${12+4*round} / 60 confirmation queries used; total online cost ${300+96+12+4*round}.`;
 el('selected').replaceChildren(...record.trace.filter(t=>t.round<=round).map(t=>{const tr=document.createElement('tr');for(const value of [t.round,t.condition]){const td=document.createElement('td');td.textContent=value;tr.append(td);}return tr;}));
 el('hash').textContent=record.sha256;el('evaluate').disabled=round!==12&&!sealedView;
 el('locked').hidden=sealedView;el('evaluation').hidden=!sealedView;
 if(sealedView){
  const pts=rows.map(r=>`${45+(r.confirmation_cost-12)/48*425},${220-r.coverage*180}`).join(' ');
  el('curve').innerHTML=`<path d="M45 35 V220 H480" fill="none" stroke="#657887"/><line x1="45" x2="480" y1="40" y2="40" stroke="#d8e2e8"/><text x="17" y="45">1</text><text x="17" y="225">0</text><text x="42" y="243">12</text><text x="455" y="243">60</text><text x="170" y="263">Confirmation budget</text><text x="48" y="22">Saved H coverage</text><polyline points="${pts}" fill="none" stroke="#c65d25" stroke-width="3"/>`;
  const r=rows.find(r=>r.round===round);el('roundMetric').textContent=`Round ${round}: H coverage ${r.coverage.toFixed(5)}; repeatability ${r.repeatability===null?'NA':r.repeatability.toFixed(5)}. This is retrospective.`;
 }
}
function ranking(){const group=el('summaryGroup').value,rows=[...D.primary[group]].sort((a,b)=>a.rank-b.rank);el('ranking').replaceChildren(...rows.map(r=>{const tr=document.createElement('tr');if(r.method==='coverage-only')tr.className='highlight';for(const value of [names[r.method],r.auc.toFixed(5),String(r.rank)]){const td=document.createElement('td');td.textContent=value;tr.append(td);}return tr;}));el('winner').textContent=`${group} leader: ${names[rows[0].method]}. ${group==='Development'?'Exploratory development evidence.':'Frozen confirmation evidence, not new-batch validation.'}`;}
for(const id of ['campaign','policy','seed'])el(id).addEventListener('change',reset);
el('round').addEventListener('input',()=>{stop();render();});el('reset').addEventListener('click',reset);
el('evaluate').addEventListener('click',()=>{sealedView=true;render();});
el('play').addEventListener('click',()=>{if(timer!==null){stop();return;}if(Number(el('round').value)===12)reset();el('play').textContent='Pause';timer=setInterval(()=>{el('round').value=Math.min(12,Number(el('round').value)+1);render();if(Number(el('round').value)===12)stop();},650);});
el('summaryGroup').addEventListener('change',ranking);
el('cis').replaceChildren(...D.ci.map(r=>{const tr=document.createElement('tr');for(const v of [`${r.campaign} / ${names[r.comparator]}`,r.mean.toFixed(5),`[${r.ci_low.toFixed(5)}, ${r.ci_high.toFixed(5)}]`]){const td=document.createElement('td');td.textContent=v;tr.append(td);}return tr;}));
render();ranking();
