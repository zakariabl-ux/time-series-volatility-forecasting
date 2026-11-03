"""Check numerical formulas and missing-session handling."""
from pathlib import Path
import numpy as np
import pandas as pd
from phase2 import calculate_series

# Independent small example: log returns and sample standard deviation.
dates=pd.bdate_range('2020-01-01',periods=70)
returns=np.array([0.01 if i%2 else -0.02 for i in range(69)])
prices=np.r_[100.,100*np.exp(np.cumsum(returns))]
frame=pd.DataFrame({'date':dates,'close':prices})
result=calculate_series(frame,dates)
np.testing.assert_allclose(result.log_return.iloc[1:],returns,atol=1e-14)
expected=np.sqrt(sum((returns[:21]-returns[:21].mean())**2)/20)
np.testing.assert_allclose(result.vol_21d_daily.iloc[21],expected)
np.testing.assert_allclose(result.vol_21d_annualized.iloc[21],expected*np.sqrt(252))
assert result.vol_21d_daily.iloc[:21].isna().all()
# A missing observation invalidates both adjacent daily returns and full windows.
gap=calculate_series(frame.drop(index=25),dates)
assert gap.log_return.iloc[25:27].isna().all()
assert gap.vol_21d_daily.iloc[25:47].isna().all()
assert pd.notna(gap.vol_21d_daily.iloc[47])
# Check the actual FTSE gap and ensure Phase 1 prices were not filled.
root=Path(__file__).resolve().parents[1]
ftse=pd.read_csv(root/'data/processed/ftse100_phase2.csv',index_col='date',parse_dates=True)
assert pd.isna(ftse.loc['2020-12-22','close'])
assert ftse.loc['2020-12-22':'2020-12-23','log_return'].isna().all()
assert ftse.log_return.notna().sum()==2523
print('Formula, annualization, full-window, and FTSE gap checks passed.')
