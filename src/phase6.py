"""Historical drawdown from observed Yahoo closing index levels."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
INDICES={'sp500':'S&P 500','cac40':'CAC 40','ftse100':'FTSE 100'}

def drawdown_series(prices):
    if prices.empty or not prices.index.is_unique or not prices.index.is_monotonic_increasing:raise ValueError('Need unique sorted prices')
    if not (np.isfinite(prices)&(prices>0)).all():raise ValueError('Prices must be positive and finite')
    peak=prices.cummax()
    return pd.DataFrame({'close':prices,'running_peak':peak,'drawdown':prices/peak-1})

def describe(drawdowns):
    trough=drawdowns.drawdown.idxmin();peak_value=drawdowns.loc[trough,'running_peak']
    # Last observation at the preceding peak; first deepest trough on ties.
    peak_date=drawdowns.loc[:trough].index[drawdowns.loc[:trough,'close']==peak_value][-1]
    recovered=drawdowns.loc[drawdowns.index>trough]
    recovered=recovered.loc[recovered.close>=peak_value]
    recovery=recovered.index[0] if not recovered.empty else pd.NaT
    return {'peak_date':peak_date,'trough_date':trough,'recovery_date':recovery,'peak_level':peak_value,'trough_level':drawdowns.loc[trough,'close'],'maximum_drawdown':drawdowns.loc[trough,'drawdown'],'peak_to_trough_calendar_days':(trough-peak_date).days,'peak_to_recovery_calendar_days':(recovery-peak_date).days if pd.notna(recovery) else np.nan}

def main():
    (ROOT/'data/risk').mkdir(parents=True,exist_ok=True);(ROOT/'reports/figures').mkdir(parents=True,exist_ok=True)
    inputs={key:pd.read_csv(ROOT/f'data/processed/{key}_prices.csv',index_col='date',parse_dates=True).close for key in INDICES}
    start=max(x.index.min() for x in inputs.values());end=min(x.index.max() for x in inputs.values())
    fig,axes=plt.subplots(3,1,figsize=(11,9),sharey=True,constrained_layout=True);rows=[]
    for (key,label),ax in zip(INDICES.items(),axes):
        d=drawdown_series(inputs[key].loc[start:end]);d.to_csv(ROOT/f'data/risk/{key}_drawdowns.csv')
        stats=describe(d);rows.append({'index':label,'comparison_start':start,'comparison_end':end,'observations':len(d),**stats})
        ax.fill_between(d.index,d.drawdown*100,0,color='#176B87',alpha=.23);ax.plot(d.index,d.drawdown*100,color='#176B87',linewidth=.8)
        ax.scatter(stats['trough_date'],stats['maximum_drawdown']*100,color='#C26538',zorder=3)
        ax.set(title=label,ylabel='Drawdown (%)',xlabel='Date',ylim=(-45,2));ax.grid(alpha=.2)
    pd.DataFrame(rows).to_csv(ROOT/'reports/phase6_drawdown_summary.csv',index=False)
    for ext in ['png','svg']:fig.savefig(ROOT/f'reports/figures/phase6_drawdowns.{ext}',dpi=180)
    plt.close(fig)
    print(pd.DataFrame(rows).to_string(index=False))
if __name__=='__main__':main()
