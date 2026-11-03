"""Download public daily index prices, preserve raw responses, and check data.

Run from any directory: python src/phase1.py
Existing raw downloads are reused so reruns reproduce the same inputs.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import platform
import urllib.request
import urllib.parse

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
START = '2016-09-06'
END = '2026-09-06'  # Exclusive end; fixed for reproducibility.
INDICES = {'sp500': ('^GSPC', 'S&P 500'), 'cac40': ('^FCHI', 'CAC 40'), 'ftse100': ('^FTSE', 'FTSE 100')}


def clean_prices(frame):
    """Reject ambiguous records; retain genuine extreme market movements."""
    data = frame.copy()
    data['date'] = pd.to_datetime(data['date'], errors='coerce')
    data['close'] = pd.to_numeric(data['close'], errors='coerce')
    invalid = data['date'].isna() | ~np.isfinite(data['close']) | (data['close'] <= 0)
    rejected = data.loc[invalid].copy()
    data = data.loc[~invalid].copy()
    duplicates = int(data.duplicated().sum())
    data = data.drop_duplicates()
    if data['date'].duplicated().any():
        raise ValueError('Conflicting prices for a date: inspect the raw data.')
    data = data.sort_values('date').reset_index(drop=True)
    if data.empty:
        raise ValueError('No valid prices returned.')
    return data, rejected, duplicates


def main():
    for folder in ['data/raw', 'data/processed', 'reports/figures']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    summaries = []
    fig, axes = plt.subplots(len(INDICES), 1, figsize=(11, 3.5 * len(INDICES)), constrained_layout=True)
    for ax, (name, (symbol, label)) in zip(axes, INDICES.items()):
        raw_path = ROOT / 'data/raw' / f'{name}.json'
        metadata_path = ROOT / 'data/raw' / f'{name}_metadata.json'
        if not raw_path.exists():
            params = urllib.parse.urlencode({
                'period1': int(pd.Timestamp(START, tz='UTC').timestamp()),
                'period2': int(pd.Timestamp(END, tz='UTC').timestamp()),
                'interval': '1d',
            })
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol, safe="")}?{params}'
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = response.read()
            parsed = json.loads(payload)
            if parsed['chart']['error'] or not parsed['chart']['result']:
                raise ValueError(f'Download failed for {symbol}')
            raw_path.write_bytes(payload)
            metadata_path.write_text(json.dumps({
                'source': 'Yahoo Finance chart endpoint', 'url': url,
                'downloaded_at_utc': datetime.now(timezone.utc).isoformat(),
                'symbol': symbol, 'requested_start': START, 'requested_end_exclusive': END,
                'sha256': hashlib.sha256(payload).hexdigest(),
                'series': 'Price index closing level, not a total-return series',
            }, indent=2))
        result = json.loads(raw_path.read_text())['chart']['result'][0]
        dates = pd.to_datetime(result['timestamp'], unit='s', utc=True)
        dates = dates.tz_convert(result['meta']['exchangeTimezoneName']).strftime('%Y-%m-%d')
        frame = pd.DataFrame({'date': dates, 'close': result['indicators']['quote'][0]['close']})
        clean, rejected, duplicates = clean_prices(frame)
        clean.to_csv(ROOT / 'data/processed' / f'{name}_prices.csv', index=False)
        rejected.to_csv(ROOT / 'data/processed' / f'{name}_rejected.csv', index=False)
        # Flags are for review, not automatic deletion; this is not Phase 2 analysis.
        changes = clean['close'].pct_change(fill_method=None)
        flagged = clean.loc[changes.abs() > 0.10].copy()
        flagged['daily_change_fraction'] = changes.loc[flagged.index]
        flagged.to_csv(ROOT / 'data/processed' / f'{name}_review_flags.csv', index=False)
        weekdays = pd.bdate_range(clean['date'].min(), clean['date'].max())
        absent = weekdays.difference(pd.DatetimeIndex(clean['date']))
        pd.DataFrame({'date': absent}).to_csv(ROOT / 'data/processed' / f'{name}_absent_weekdays.csv', index=False)
        summaries.append({
            'index': label, 'raw_rows': len(frame), 'clean_rows': len(clean),
            'start': str(clean['date'].min().date()), 'end': str(clean['date'].max().date()),
            'rejected_rows': len(rejected), 'exact_duplicates_removed': duplicates,
            'moves_over_10_percent_for_review': len(flagged),
            'absent_weekdays_including_holidays': len(absent),
        })
        ax.plot(clean['date'], clean['close'], linewidth=0.8)
        ax.set(title=label, ylabel='Index points', xlabel='Date')
        ax.grid(alpha=0.2)
    fig.savefig(ROOT / 'reports/figures/phase1_prices.png', dpi=150)
    plt.close(fig)
    table = pd.DataFrame(summaries)
    table.to_csv(ROOT / 'reports/phase1_quality_summary.csv', index=False)
    versions = f'Python {platform.python_version()}\npandas=={pd.__version__}\nnumpy=={np.__version__}\nmatplotlib=={matplotlib.__version__}\n'
    (ROOT / 'reports/environment.txt').write_text(versions)
    print(table.to_string(index=False))


if __name__ == '__main__':
    main()
