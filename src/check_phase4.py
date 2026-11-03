"""Verify numerical forecasts, timing, and missing-data behavior."""
from pathlib import Path
import numpy as np
import pandas as pd
from phase4 import forecast_series
ROOT=Path(__file__).resolve().parents[1]
x=pd.Series(np.linspace(-.02,.03,80),index=pd.bdate_range('2020-01-01',periods=80))
f=forecast_series(x)
assert f.moving_window_variance.iloc[:21].isna().all()
np.testing.assert_allclose(f.moving_window_variance.iloc[21],sum(v*v for v in x.iloc[:21])/21)
np.testing.assert_allclose(f.ewma_variance.iloc[21],f.moving_window_variance.iloc[21])
np.testing.assert_allclose(f.ewma_variance.iloc[22],.94*f.ewma_variance.iloc[21]+.06*x.iloc[21]**2)
y=x.copy();y.iloc[40:]=99
pd.testing.assert_frame_equal(f.iloc[:41],forecast_series(y).iloc[:41])
pd.testing.assert_frame_equal(f.iloc[:40],forecast_series(x.iloc[:40]))
y=x.copy();y.iloc[30]=np.nan;g=forecast_series(y)
assert pd.notna(g.moving_window_variance.iloc[30])
assert g.moving_window_variance.iloc[31:52].isna().all()
np.testing.assert_allclose(g.ewma_variance.iloc[52],np.mean(y.iloc[31:52]**2))
checks=[]
for key in ['sp500','cac40','ftse100']:
 d=pd.read_csv(ROOT/f'data/processed/{key}_phase2.csv',index_col='date',parse_dates=True).log_return
 saved=pd.read_csv(ROOT/f'data/forecasts/{key}_forecasts.csv',index_col='target_date',parse_dates=['target_date','forecast_origin'])
 expected_full=forecast_series(d)
 np.testing.assert_allclose(saved[['moving_window_variance','ewma_variance']],expected_full[['moving_window_variance','ewma_variance']],equal_nan=True,atol=1e-15)
 for i in [100,500,1600]:
  expected=sum(float(v)**2 for v in d.iloc[i-21:i])/21
  expected_ew=.94*saved.ewma_variance.iloc[i-1]+.06*d.iloc[i-1]**2
  np.testing.assert_allclose(saved.moving_window_variance.iloc[i],expected,atol=1e-15)
  np.testing.assert_allclose(saved.ewma_variance.iloc[i],expected_ew,atol=1e-15)
  checks.append({'index':key,'target_date':str(d.index[i].date()),'last_input_date':str(d.index[i-1].date()),'manual_moving_window':expected,'saved_moving_window':saved.moving_window_variance.iloc[i],'manual_ewma':expected_ew,'saved_ewma':saved.ewma_variance.iloc[i]})
 valid=saved.dropna(subset=['moving_window_variance','ewma_variance'])
 assert (valid.forecast_origin<valid.index).all()
 assert (valid[['moving_window_variance','ewma_variance']]>=0).all().all()
pd.DataFrame(checks).to_csv(ROOT/'reports/phase4_manual_checks.csv',index=False)
print('PASS: manual forecasts, seed/recursion, future-data perturbation, prefix invariance, missing-session reset, saved values, and target-date ordering.')
