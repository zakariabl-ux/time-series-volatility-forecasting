from pathlib import Path
import numpy as np
import pandas as pd
from phase6 import drawdown_series,describe
ROOT=Path(__file__).resolve().parents[1]
dates=pd.date_range('2020-01-01',periods=5)
d=drawdown_series(pd.Series([100,120,90,110,120],index=dates))
np.testing.assert_allclose(d.drawdown,[0,0,-.25,-1/12,0],atol=1e-14)
s=describe(d);assert s['peak_date']==dates[1] and s['trough_date']==dates[2] and s['recovery_date']==dates[4]
assert pd.isna(describe(d.iloc[:4])['recovery_date'])
summary=pd.read_csv(ROOT/'reports/phase6_drawdown_summary.csv').set_index('index')
for key,label in [('sp500','S&P 500'),('cac40','CAC 40'),('ftse100','FTSE 100')]:
 p=pd.read_csv(ROOT/f'data/processed/{key}_prices.csv',index_col='date',parse_dates=True).close
 saved=pd.read_csv(ROOT/f'data/risk/{key}_drawdowns.csv',index_col='date',parse_dates=True)
 # Independent running-peak computation, not the pandas cummax implementation.
 high=float('-inf');expected=[]
 for value in p:high=max(high,value);expected.append(value/high-1)
 np.testing.assert_allclose(expected,saved.drawdown,atol=1e-14)
 np.testing.assert_allclose(min(expected),summary.loc[label,'maximum_drawdown'])
 assert (saved.drawdown<=1e-14).all() and (saved.drawdown>-1).all()
 row=summary.loc[label];peak=pd.Timestamp(row.peak_date);trough=pd.Timestamp(row.trough_date);recovery=pd.Timestamp(row.recovery_date)
 assert peak<=trough<recovery and p.loc[recovery]>=p.loc[peak]
 assert (p.loc[(p.index>trough)&(p.index<recovery)]<p.loc[peak]).all()
print('PASS: known drawdown example, unrecovered case, all actual paths, maximum losses, date ordering, and first recovery dates.')
