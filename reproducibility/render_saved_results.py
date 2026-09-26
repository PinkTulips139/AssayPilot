"""FIGURE-ONLY reproduction: read saved aggregates/intervals, never run a policy."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'assaypilot-frozen','savefig.facecolor':'white'})
METHODS=['random','greedy','uncertainty','diversity','coverage-only']
LABELS={'random':'Random','greedy':'Greedy','uncertainty':'Uncertainty-only','diversity':'Diversity-only','coverage-only':'Coverage-only'}
COLORS={'random':'#89949e','greedy':'#7a5e9b','uncertainty':'#247ba0','diversity':'#2d8774','coverage-only':'#d66b28'}
CAPTIONS={
1:'Figure 1. Offline budgeted evaluation, not automated wet-lab execution. All 300 screening observations are paid inputs. Twelve initial confirmations plus twelve rounds of four queries give 60 confirmations; 96 reference-control costs are recorded separately. Unpurchased confirmation and independent H remain outside the policy view. All trajectories are sealed before hidden evaluation. The framework can reject the development-selected policy claim.',
2:'Figure 2. Development-only mean Coverage-AUC, with seed standard deviations (not confidence intervals). Coverage-only leads at 0.91806. QACS-full and two single-term ablations are exploratory development evidence, not confirmation runs. The later constrained and lexicographic variants remain in the negative-results supplement.',
3:'Figure 3. The same five policies across development and the two frozen confirmation campaigns. Coverage-only changes from rank 1 to rank 4 in both T1 and T2. Diversity-only leads T1 and Uncertainty-only leads T2. Lines connect dataset summaries, not longitudinal observations. AUC uses its full 0-1 scale. The campaigns share plates and a previously seen batch environment.',
4:'Figure 4. Coverage-only minus each strong comparator, paired by seed. Points are the 20 saved differences; diamonds and bars are the saved paired means and percentile bootstrap 95% intervals (10,000 resamples, RNG seed 1600). Intervals describe initial-seed uncertainty conditional on fixed entities and plates, not population or biological uncertainty. The T2 versus Diversity interval includes zero.',
5:'Figure 5. Separate constructs, not a composite score. Saved means over 20 seeds per campaign show higher conditional Repeatability for coverage-only, alongside lower final coverage and weaker external-batch agreement/cosine than strong baselines. Repeatability conditions on online-positive selections; its denominators are included in Table 5. Secondary outcomes do not replace Coverage-AUC.',
6:'Figure 6. Identity and claim hierarchy inherited from Phase16A. Each confirmation campaign uses registered entities and physical plates absent from development, but T1 and T2 share eight physical plates and all use a previously seen batch environment. Chemical/scaffold independence is unknown. External-study validation is not part of this design (N/A). PASS concerns the stated operational level only.'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def md_table(df):
 def fmt(v):
  if pd.isna(v):return 'NA'
  return f'{v:.5f}' if isinstance(v,(float,np.floating)) else str(v)
 return '| '+' | '.join(map(str,df.columns))+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+''.join('| '+' | '.join(fmt(v) for v in row)+' |\n' for row in df.itertuples(index=False,name=None))
def savefig(fig,i,paths,fields,claims,derived):
 out=ROOT/'figures';out.mkdir(exist_ok=True)
 fig.savefig(out/f'figure_{i}.png',dpi=180,bbox_inches='tight',metadata={'Software':'AssayPilot saved-result renderer'})
 fig.savefig(out/f'figure_{i}.svg',bbox_inches='tight',metadata={'Date':None});plt.close(fig)
 (out/f'figure_{i}_caption.md').write_text(CAPTIONS[i]+'\n',encoding='utf-8')
 provenance=dict(inputs=[dict(path=p,sha256=sha(ROOT/p)) for p in paths],fields=fields,statistics='saved estimates/SD/CI; no new bootstrap',performance_recomputed=False,formatting_only=True,display_derivations=derived,claims=claims,renderer_sha256=sha(Path(__file__)))
 (out/f'figure_{i}_sources.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
def main():
 agg=pd.read_csv(ROOT/'results/confirmation/summary_metrics.csv');dev=pd.read_csv(ROOT/'results/development/comparison_aggregate.csv',header=[0,1],index_col=0).dropna(how='all')
 ci=pd.read_csv(ROOT/'results/confirmation/bootstrap_ci.csv');pairs=pd.read_csv(ROOT/'results/confirmation/paired_differences.csv')
 def mean(c,m,metric='coverage_auc'):return float(agg[(agg.campaign==c)&(agg.method==m)&(agg.metric==metric)]['mean'].item())
 def dv(m,stat='mean'):return float(dev.loc['QACS-coverage-only' if m=='coverage-only' else m,('coverage_auc',stat)])
 groups=['Development','T1','T2'];values={c:{m:(dv(m) if c=='Development' else mean(c,m)) for m in METHODS} for c in groups}
 # 1: readable conceptual boundary; no model or assay execution is represented.
 fig,ax=plt.subplots(figsize=(12,6));ax.set(xlim=(0,12),ylim=(0,6));ax.axis('off')
 ax.text(.2,5.6,'AssayPilot | frozen evaluation, not a winner algorithm',fontsize=19,weight='bold')
 boxes=[(.3,3.55,'Observed history\n+ paid screening'),(4.35,3.55,'Frozen policy\n+ budget constraints'),(8.4,3.55,'Sequential query\n12 initial + 12 x 4'),(8.4,1.2,'Seal all receipts\n200 planned runs'),(4.35,1.2,'Hidden confirmation\n+ frozen evaluator'),(.3,1.2,'Scientific adjudication\nretain negative findings')]
 for x,y,t in boxes:
  ax.add_patch(FancyBboxPatch((x,y),3.25,1.05,boxstyle='round,pad=.12',facecolor='#eef3f7',edgecolor='#29465b'))
  ax.text(x+1.625,y+.525,t,ha='center',va='center',fontsize=12)
 for x1,y1,x2,y2 in [(3.7,4.07,4.2,4.07),(7.75,4.07,8.25,4.07),(10.03,3.35,10.03,2.45),(8.2,1.72,7.78,1.72),(4.15,1.72,3.7,1.72)]:ax.annotate('',(x2,y2),(x1,y1),arrowprops={'arrowstyle':'->','lw':2,'color':'#29465b'})
 ax.plot([.1,11.8],[2.85,2.85],ls='--',color='#a24a2b');ax.text(.25,3.0,'DECISION VIEW: no future outcomes or H',color='#a24a2b',fontsize=10)
 ax.text(.25,.4,'Offline costs: 300 screening + 60 confirmation + 96 reference = 456; historical evaluation measured separately.',fontsize=10)
 savefig(fig,1,['results/confirmation/run_manifest.json','results/confirmation/all_trajectories_locked.json'],['initial','rounds','budget','reference_cost','planned'],['C10','C11'],[])
 # 2: development evidence including negative QACS controls.
 names=METHODS+['QACS-full','QACS-no-repeatability','QACS-no-batch'];means=[dv(m) if m in METHODS else float(dev.loc[m,('coverage_auc','mean')]) for m in names];sd=[dv(m,'std') if m in METHODS else float(dev.loc[m,('coverage_auc','std')]) for m in names]
 fig,ax=plt.subplots(figsize=(10,6));y=np.arange(len(names));ax.barh(y,means,xerr=sd,color=[COLORS.get(m,'#b5b8bb') for m in names],capsize=3)
 ax.set(yticks=y,yticklabels=[LABELS.get(m,m) for m in names],xlim=(0,1.06),xlabel='Coverage-AUC (mean +/- seed SD)',title='Development: candidate selection, not confirmation');ax.invert_yaxis()
 for yy,v in zip(y,means):ax.text(.02,yy,f'{v:.5f}',va='center',color='white',weight='bold')
 fig.tight_layout();savefig(fig,2,['results/development/comparison_aggregate.csv'],['coverage_auc mean/std/count'],['C01','C07'],[])
 # 3: primary hero plot, full AUC scale and explicit ordinal ranks.
 fig,(ax,bx)=plt.subplots(1,2,figsize=(12,5.8),gridspec_kw={'width_ratios':[1.5,1]})
 for m in METHODS:
  vals=[values[c][m] for c in groups];ranks=[sorted(values[c],key=lambda k:-values[c][k]).index(m)+1 for c in groups]
  ax.plot(range(3),vals,'o-',color=COLORS[m],label=LABELS[m],lw=3 if m=='coverage-only' else 1.8)
  bx.plot(range(3),ranks,'o-',color=COLORS[m],lw=3 if m=='coverage-only' else 1.8)
  if m=='coverage-only':
   for j,(v,r) in enumerate(zip(vals,ranks)):
    ax.annotate(f'{v:.5f}',(j,v),xytext=(0,-22),textcoords='offset points',ha='center',color=COLORS[m],weight='bold')
    bx.annotate(f'#{r}',(j,r),xytext=(0,10),textcoords='offset points',ha='center',color=COLORS[m],weight='bold')
 ax.set(xticks=range(3),xticklabels=groups,ylim=(0,1),ylabel='Mean Coverage-AUC',title='Frozen confirmation changes the conclusion')
 bx.set(xticks=range(3),xticklabels=groups,ylim=(5.45,.5),yticks=range(1,6),ylabel='Rank among the same five policies',title='Coverage-only: 1st -> 4th -> 4th')
 fig.legend(*ax.get_legend_handles_labels(),loc='lower center',ncol=3,frameon=False);fig.tight_layout(rect=(0,.13,1,1))
 savefig(fig,3,['results/development/comparison_aggregate.csv','results/confirmation/summary_metrics.csv'],['coverage_auc mean'],['C01','C02','C03'],['descending rank of saved means within each dataset'])
 # 4: original differences and original intervals; fixed jitter is visual only.
 fig,ax=plt.subplots(figsize=(10.5,5.8));labels=[]
 for i,row in enumerate(ci.itertuples()):
  a=pairs[(pairs.campaign==row.campaign)&(pairs.comparator==row.comparator)&pairs.metric.eq('coverage_auc')].sort_values('seed').difference.to_numpy()
  ax.scatter(a,i+np.linspace(-.13,.13,len(a)),s=24,alpha=.5,color='#71879a')
  ax.plot([row.ci_low,row.ci_high],[i,i],lw=3,color='#d66b28');ax.plot(row.mean,i,'D',color='#9d4116',ms=8)
  labels.append(row.campaign+' - '+LABELS[row.comparator]);ax.text(.98,i+.25,f'{row.mean:+.5f} [{row.ci_low:+.5f}, {row.ci_high:+.5f}]',transform=ax.get_yaxis_transform(),ha='right',fontsize=9)
 ax.axvline(0,color='#263746',ls='--');ax.set(yticks=range(4),yticklabels=labels,xlabel='Coverage-only minus comparator: Coverage-AUC',title='Paired differences | fixed-entity, fixed-plate uncertainty',ylim=(3.65,-.5),xlim=(-.35,.16));fig.tight_layout()
 savefig(fig,4,['results/confirmation/paired_differences.csv','results/confirmation/bootstrap_ci.csv'],['difference','mean','ci_low','ci_high','valid_pairs'],['C09'],['fixed vertical jitter only'])
 # 5: each construct gets its own axis, no composite utility.
 metrics=[('coverage_auc','Coverage-AUC'),('final_coverage','Final Coverage'),('diversity','Diversity'),('repeatability','Repeatability (conditional)'),('cross_batch_agreement','External-batch agreement'),('cross_batch_median_cosine','External-batch median cosine')]
 fig,axes=plt.subplots(2,3,figsize=(13,8))
 for ax,(metric,title) in zip(axes.flat,metrics):
  for c,offset,marker,color in [('T1',-.12,'o','#247ba0'),('T2',.12,'s','#b95c30')]:ax.plot(np.arange(5)+offset,[mean(c,m,metric) for m in METHODS],marker=marker,ls='none',label=c,color=color,ms=7)
  ax.set(title=title,xticks=range(5),xticklabels=['Rnd','Grd','Unc','Div','Cov'],ylim=(-1,1) if metric.endswith('cosine') else (0,1.05));ax.grid(axis='y',alpha=.15)
 axes[0,0].legend(frameon=False);fig.suptitle('Separate endpoints: higher repeatability does not reverse primary failure',fontsize=16);fig.tight_layout(rect=(0,0,1,.95))
 savefig(fig,5,['results/confirmation/summary_metrics.csv','results/confirmation/summary_by_seed.csv'],[m for m,_ in metrics]+['online_positive','repeat_confirmed'],['C08'],[])
 # 6: sourced operational claim status, not inferred from effect sizes.
 status=[['PASS']*3,['PASS']*3,['PASS','PASS','FAIL'],['FAIL']*3,['N/A']*3,['UNKNOWN']*3]
 rows=['Record / measurement','Registered entity','Physical plate','Unseen batch','External study','Chemical / scaffold']
 fig,ax=plt.subplots(figsize=(11,6));ax.set(xlim=(-.5,2.5),ylim=(5.5,-.5),xticks=range(3),xticklabels=['Development vs T1','Development vs T2','T1 vs T2'],yticks=range(6),yticklabels=rows,title='Independence is claim-specific');ax.xaxis.tick_top();ax.tick_params(length=0)
 palette={'PASS':'#d5ece6','FAIL':'#f1d9cf','UNKNOWN':'#f3e9bd','N/A':'#e3e7eb'}
 for i,row in enumerate(status):
  for j,v in enumerate(row):ax.add_patch(plt.Rectangle((j-.48,i-.45),.96,.9,facecolor=palette[v],edgecolor='white'));ax.text(j,i,v,ha='center',va='center',weight='bold')
 for sp in ax.spines.values():sp.set_visible(False)
 fig.tight_layout();savefig(fig,6,['results/audit/overlap_matrix.csv','results/audit/adjudication.json'],['identity','intersection','claim statuses'],['C04','C05','C06'],['layout of inherited claim statuses; no outcome inference'])
 # Five main tables plus unabridged supplementary metrics.
 tables={}
 tables[1]=pd.DataFrame([dict(Method=LABELS.get(m,m),AUC=v,Seed_SD=e,Seeds=20) for m,v,e in zip(names,means,sd)])
 tables[2]=agg[agg.metric.eq('coverage_auc')][['campaign','method','mean','median','std','valid_seeds','failed_seeds','na_seeds']].copy()
 tables[3]=ci.copy()
 tables[4]=pd.DataFrame({'Identity level':rows,'Development vs T1':[r[0] for r in status],'Development vs T2':[r[1] for r in status],'T1 vs T2':[r[2] for r in status]})
 by=pd.read_csv(ROOT/'results/confirmation/summary_by_seed.csv');records=[]
 for c in ['T1','T2']:
  for m in METHODS:
   g=by[(by.campaign==c)&(by.method==m)]
   records.append(dict(Campaign=c,Method=LABELS[m],Final_Coverage=mean(c,m,'final_coverage'),Diversity=mean(c,m,'diversity'),Repeatability=mean(c,m,'repeatability'),Batch_agreement=mean(c,m,'cross_batch_agreement'),Batch_cosine=mean(c,m,'cross_batch_median_cosine'),Online_positive_mean=g.online_positive.mean(),Repeated_positive_mean=g.repeat_confirmed.mean()))
 tables[5]=pd.DataFrame(records)
 (ROOT/'tables').mkdir(exist_ok=True)
 for i,df in tables.items():df.to_csv(ROOT/f'tables/table_{i}.csv',index=False);(ROOT/f'tables/table_{i}.md').write_text(md_table(df),encoding='utf-8')
 agg.to_csv(ROOT/'tables/supplement_full_metrics.csv',index=False)
 (ROOT/'tables/supplement_full_metrics.md').write_text(md_table(agg),encoding='utf-8')
 (ROOT/'tables/table_sources.json').write_text(json.dumps({'inputs':[{ 'path':p,'sha256':sha(ROOT/p)} for p in ['results/development/comparison_aggregate.csv','results/confirmation/summary_metrics.csv','results/confirmation/summary_by_seed.csv','results/confirmation/bootstrap_ci.csv','results/audit/adjudication.json']],'policy_or_metric_recomputed':False,'derived':'Table5 count means only, from existing per-seed counters; no policy execution'},indent=2),encoding='utf-8')
 print('FIGURES 6/6; TABLES 5/5; saved-result formatting only')
if __name__=='__main__':main()
