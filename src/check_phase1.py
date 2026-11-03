"""Optional completeness and integrity review: python src/check_phase1.py."""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import exchange_calendars as xcals

ROOT = Path(__file__).resolve().parents[1]
rows=[]
for key, calendar in [('sp500','XNYS'),('cac40','XPAR'),('ftse100','XLON')]:
    data=pd.read_csv(ROOT/'data/processed'/f'{key}_prices.csv',parse_dates=['date'])
    assert data.date.is_unique and data.date.is_monotonic_increasing
    assert data.notna().all().all() and np.isfinite(data.close).all() and (data.close>0).all()
    raw=ROOT/'data/raw'/f'{key}.json'
    meta=json.loads((ROOT/'data/raw'/f'{key}_metadata.json').read_text())
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==meta['sha256']
    cal=xcals.get_calendar(calendar,start='2016-09-06',end='2026-09-10')
    expected=cal.sessions_in_range('2016-09-06','2026-09-05').tz_localize(None)
    observed=pd.DatetimeIndex(data.date)
    missing=expected.difference(observed)
    extra=observed.difference(expected)
    known_missing = pd.DatetimeIndex(['2020-12-22']) if key == 'ftse100' else pd.DatetimeIndex([])
    assert missing.equals(known_missing), f'Unexpected missing sessions: {key}: {missing}'
    assert len(extra) == 0
    # Mark intervals that cross a missing session for Phase 2.
    next_is_gap = [(expected.get_loc(observed[i]) - expected.get_loc(observed[i-1])) > 1 if i else False for i in range(len(observed))]
    pd.DataFrame({'date': observed, 'crosses_missing_session': next_is_gap}).to_csv(ROOT/'data/processed'/f'{key}_return_interval_flags.csv', index=False)
    rows.append({'index_key':key,'calendar':calendar,'expected_sessions':len(expected),'observations':len(data),'missing_sessions':len(missing),'unexpected_dates':len(extra)})
    pd.DataFrame({'date':missing}).to_csv(ROOT/'reports'/f'{key}_missing_sessions.csv',index=False)
    pd.DataFrame({'date':extra}).to_csv(ROOT/'reports'/f'{key}_unexpected_dates.csv',index=False)
result=pd.DataFrame(rows)
result.to_csv(ROOT/'reports/calendar_checks.csv',index=False)
print(result.to_string(index=False))
assert result['missing_sessions'].sum() == 1, 'Known Yahoo gap should remain visible.'
print('Integrity checks passed; one documented Yahoo missing session remains in FTSE 100.')
