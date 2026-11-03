"""Focused exploratory analysis using training-period returns only."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
INDICES={'sp500':'S&P 500','cac40':'CAC 40','ftse100':'FTSE 100'}
EDA_END='2022-12-31'

def main():
    (ROOT/'reports/figures').mkdir(parents=True,exist_ok=True)
    summary=[];monthly=[];lags=[]
    fig,axes=plt.subplots(3,1,figsize=(10,9),constrained_layout=True)
    acfig,acaxes=plt.subplots(3,1,figsize=(10,9),constrained_layout=True)
    combined={}
    for (key,label),ax,acax in zip(INDICES.items(),axes,acaxes):
        frame=pd.read_csv(ROOT/f'data/processed/{key}_phase2.csv',index_col='date',parse_dates=True).loc[:EDA_END]
        r=frame.log_return
        valid=r.dropna()
        combined[label]=r
        summary.append({'index':label,'valid_returns':len(valid),'mean_daily_return':valid.mean(),'daily_std':valid.std(ddof=1),'skewness':valid.skew(),'excess_kurtosis':valid.kurt(),'minimum':valid.min(),'maximum':valid.max()})
        ax.hist(valid*100,bins=np.linspace(-14,12,66),density=True,color='#176B87',alpha=.8)
        ax.set(title=label,xlabel='Daily log return (%)',ylabel='Density',xlim=(-14,12))
        ax.grid(alpha=.15)
        # Keep missing-session rows in place so a lag means trading sessions.
        for lag in range(1,21):
            lags.append({'index':label,'lag_sessions':lag,'return_autocorrelation':r.autocorr(lag),'squared_return_autocorrelation':r.pow(2).autocorr(lag)})
        d=pd.DataFrame(lags).query('index == @label')
        acax.plot(d.lag_sessions,d.return_autocorrelation,marker='o',label='Returns')
        acax.plot(d.lag_sessions,d.squared_return_autocorrelation,marker='s',label='Squared returns')
        acax.axhline(0,color='gray',linewidth=.7);acax.set(title=label,xlabel='Lag (trading sessions)',ylabel='Autocorrelation',ylim=(-.3,1));acax.legend();acax.grid(alpha=.15)
        for month,g in r.groupby(r.index.to_period('M')):
            # Exclude partial boundary months and any month containing missing returns.
            if month==r.index.min().to_period('M') or g.isna().any() or g.count()<15:continue
            monthly.append({'index':label,'month':str(month),'valid_returns':g.count(),'annualized_volatility':g.std(ddof=1)*np.sqrt(252)})
    pd.DataFrame(summary).to_csv(ROOT/'reports/phase3_summary.csv',index=False)
    pd.DataFrame(lags).to_csv(ROOT/'reports/phase3_autocorrelation.csv',index=False)
    months=pd.DataFrame(monthly);months.to_csv(ROOT/'reports/phase3_monthly_volatility.csv',index=False)
    extremes=[]
    for label,g in months.groupby('index',sort=False):
        for kind,idx in [('calm',g.annualized_volatility.idxmin()),('turbulent',g.annualized_volatility.idxmax())]:
            extremes.append({'index':label,'classification':kind,**g.loc[idx].drop('index').to_dict()})
    pd.DataFrame(extremes).to_csv(ROOT/'reports/phase3_period_examples.csv',index=False)
    # Correlations use only dates with valid observations in all three markets.
    common=pd.DataFrame(combined).dropna()
    common.corr().to_csv(ROOT/'reports/phase3_common_date_correlations.csv')
    cfig,cax=plt.subplots(figsize=(6,5),constrained_layout=True)
    corr=common.corr();im=cax.imshow(corr,vmin=-1,vmax=1,cmap='RdBu_r')
    cax.set(xticks=range(3),yticks=range(3),xticklabels=corr.columns,yticklabels=corr.index,title=f'Return correlations | {len(common)} common dates')
    for i in range(3):
        for j in range(3):cax.text(j,i,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',color='white' if abs(corr.iloc[i,j])>.65 else 'black')
    cfig.colorbar(im,ax=cax)
    mfig,maxis=plt.subplots(figsize=(11,4),constrained_layout=True)
    for label,g in months.groupby('index',sort=False):maxis.plot(pd.to_datetime(g.month),g.annualized_volatility*100,label=label)
    maxis.set(title='Monthly historical volatility | EDA period',ylabel='Annualized volatility (%)',xlabel='Month');maxis.legend();maxis.grid(alpha=.2)
    for f,name in [(fig,'distributions'),(acfig,'autocorrelation'),(cfig,'correlations'),(mfig,'monthly_volatility')]:
        for ext in ['png','svg']:f.savefig(ROOT/f'reports/figures/phase3_{name}.{ext}',dpi=180)
        plt.close(f)
    print(pd.DataFrame(summary).to_string(index=False))
    print(pd.DataFrame(extremes).to_string(index=False))
    print('Common valid dates:',len(common))
if __name__=='__main__':main()
