"""Fixed-setting next-session variance forecasts from Phase 2 Yahoo returns."""
from pathlib import Path
from collections import deque
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
INDICES={'sp500':'S&P 500','cac40':'CAC 40','ftse100':'FTSE 100'}
WINDOW=21
DECAY=.94

def forecast_series(returns,window=WINDOW,decay=DECAY):
    """Target row t uses returns through t-1. Preserve missing session rows.

    Seed EWMA with a full window of squared returns. Reset after a missing
    return and require a fresh full window; never replace missing data by zero.
    """
    if window<1 or not 0<decay<1:raise ValueError('Invalid settings')
    if not returns.index.is_unique or not returns.index.is_monotonic_increasing:raise ValueError('Dates must be unique and sorted')
    history=deque(maxlen=window);state=None;rows=[]
    for i,target in enumerate(returns.index):
        origin=returns.index[i-1] if i else pd.NaT
        if i:
            previous=returns.iloc[i-1]
            if not np.isfinite(previous):history.clear();state=None
            else:
                squared=float(previous)**2;history.append(squared)
                if state is not None:state=decay*state+(1-decay)*squared
                elif len(history)==window:state=float(np.mean(history))
        rows.append({'target_date':target,'forecast_origin':origin,
                     'moving_window_variance':float(np.mean(history)) if len(history)==window else np.nan,
                     'ewma_variance':state if state is not None else np.nan})
    return pd.DataFrame(rows).set_index('target_date')

def main():
    (ROOT/'data/forecasts').mkdir(parents=True,exist_ok=True)
    (ROOT/'reports/figures').mkdir(parents=True,exist_ok=True)
    summaries=[]
    fig,axes=plt.subplots(3,1,figsize=(11,9),constrained_layout=True)
    for (key,label),ax in zip(INDICES.items(),axes):
        data=pd.read_csv(ROOT/f'data/processed/{key}_phase2.csv',index_col='date',parse_dates=True)
        out=forecast_series(data.log_return)
        out['period']=np.where(out.index<'2023-01-01','training',np.where(out.index<'2025-01-01','validation','test'))
        out.to_csv(ROOT/f'data/forecasts/{key}_forecasts.csv')
        for period,g in out.groupby('period',sort=False):
            summaries.append({'index':label,'period':period,'target_rows':len(g),'available_moving_window':g.moving_window_variance.notna().sum(),'available_ewma':g.ewma_variance.notna().sum()})
        v=out.loc['2023-01-01':'2024-12-31']
        for col,name,color in [('moving_window_variance','21-session moving window','#176B87'),('ewma_variance','EWMA (decay 0.94)','#C26538')]:
            ax.plot(v.index,np.sqrt(v[col])*np.sqrt(252)*100,label=name,color=color,linewidth=1)
        ax.set(title=label,xlabel='Target trading date',ylabel='Forecast annualized vol. (%)');ax.legend();ax.grid(alpha=.2)
    for ext in ['png','svg']:fig.savefig(ROOT/f'reports/figures/phase4_validation_forecasts.{ext}',dpi=180)
    plt.close(fig)
    pd.DataFrame(summaries).to_csv(ROOT/'reports/phase4_forecast_coverage.csv',index=False)
    config={'window_sessions':WINDOW,'ewma_decay':DECAY,'selection':'Fixed educational choices; not optimized using validation or test losses','target':'Next trading-session variance under a zero conditional-mean approximation','training_end':'2022-12-31','validation_start':'2023-01-01','validation_end':'2024-12-31','test_start':'2025-01-01','test_end':'2026-09-04','missing_policy':'Reset on missing return; wait for 21 consecutive valid returns','ewma_seed':'Mean of first 21 consecutive squared returns after start/reset','units':'Squared decimal log returns','supervisor_agreement':'Not recorded; proposed protocol implemented at user request','prior_inspection':'Full-history charts/statistics viewed in earlier phases; later period is not wholly unseen'}
    (ROOT/'reports/phase4_model_config.json').write_text(json.dumps(config,indent=2))
    print(pd.DataFrame(summaries).to_string(index=False))
if __name__=='__main__':main()
