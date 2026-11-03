"""Calculate daily log returns and historical/rolling volatility.

Run: python src/phase2.py
Inputs are the Yahoo-only cleaned price tables from Phase 1.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import exchange_calendars as xcals
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INDICES = {'sp500': ('S&P 500', 'XNYS'), 'cac40': ('CAC 40', 'XPAR'), 'ftse100': ('FTSE 100', 'XLON')}
ANNUAL_SESSIONS = 252


def calculate_series(prices, sessions):
    """Align to trading sessions; never fill prices or skip over missing sessions."""
    prices = prices.copy()
    prices['date'] = pd.to_datetime(prices['date'])
    if prices.date.duplicated().any() or not (np.isfinite(prices.close) & (prices.close > 0)).all():
        raise ValueError('Input prices must have unique dates and positive finite closes.')
    result = prices.set_index('date')[['close']].reindex(sessions)
    result.index.name = 'date'
    result['missing_price'] = result.close.isna()
    result['log_return'] = np.log(result.close / result.close.shift(1))
    result['valid_daily_return'] = result.log_return.notna()
    for window in (21, 63):
        # Require a complete window: missing-session effects stay visible.
        daily = result.log_return.rolling(window, min_periods=window).std(ddof=1)
        result[f'vol_{window}d_daily'] = daily
        result[f'vol_{window}d_annualized'] = daily * np.sqrt(ANNUAL_SESSIONS)
    return result


def main():
    (ROOT/'reports/figures').mkdir(parents=True, exist_ok=True)
    summaries = []
    return_fig, return_axes = plt.subplots(3, 1, figsize=(11, 9), constrained_layout=True)
    vol_fig, vol_axes = plt.subplots(3, 1, figsize=(11, 9), constrained_layout=True)
    for (key, (label, calendar)), rax, vax in zip(INDICES.items(), return_axes, vol_axes):
        prices = pd.read_csv(ROOT/f'data/processed/{key}_prices.csv', parse_dates=['date'])
        cal = xcals.get_calendar(calendar, start='2016-09-06', end='2026-09-10')
        sessions = cal.sessions_in_range('2016-09-06', '2026-09-04').tz_localize(None)
        result = calculate_series(prices, sessions)
        result.to_csv(ROOT/f'data/processed/{key}_phase2.csv')
        daily = result.log_return.std(ddof=1)
        summaries.append({
            'index': label, 'sessions': len(result), 'observed_prices': int(result.close.notna().sum()),
            'valid_daily_returns': int(result.valid_daily_return.sum()),
            'missing_prices': int(result.missing_price.sum()),
            'mean_daily_log_return': result.log_return.mean(),
            'historical_daily_volatility': daily,
            'historical_annualized_volatility': daily*np.sqrt(ANNUAL_SESSIONS),
            'valid_21d_windows': int(result.vol_21d_daily.notna().sum()),
            'valid_63d_windows': int(result.vol_63d_daily.notna().sum()),
        })
        rax.plot(result.index, result.log_return*100, linewidth=.6, color='#176B87')
        rax.set(title=label, ylabel='Daily log return (%)', xlabel='Date')
        rax.grid(alpha=.2)
        for window, color in [(21, '#176B87'), (63, '#C26538')]:
            vax.plot(result.index, result[f'vol_{window}d_annualized']*100, label=f'{window} trading sessions', linewidth=1, color=color)
        vax.set(title=label, ylabel='Annualized volatility (%)', xlabel='Date')
        vax.legend(frameon=False)
        vax.grid(alpha=.2)
    for fig, filename in [(return_fig, 'phase2_daily_returns'), (vol_fig, 'phase2_rolling_volatility')]:
        fig.savefig(ROOT/f'reports/figures/{filename}.png', dpi=180)
        fig.savefig(ROOT/f'reports/figures/{filename}.svg')
        plt.close(fig)
    table = pd.DataFrame(summaries)
    table.to_csv(ROOT/'reports/phase2_summary.csv', index=False)
    print(table.to_string(index=False))


if __name__ == '__main__':
    main()
