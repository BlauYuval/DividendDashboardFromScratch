import os
import json
import redis
import numpy as np
import pandas as pd
from income import Income
from Portfilio import Portfolio
from growth import DividendGrowth
from data_loader import DataLoader
from PortfolioReturns import PortfolioReturns

# from secrets import redis_password
from dotenv import load_dotenv

load_dotenv()

# Initialize Redis connection
redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')  # Replace with the password from the image

r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

data_loader = DataLoader()
transaction_data, sectors_data, daily_prices, dividends_data = data_loader.run()

## PORTFOLIO
portfolio_returns = PortfolioReturns(transaction_data.rename(columns={'signed_shares':'shares'}), daily_prices)
total_amounts = portfolio_returns.run()
tickers_returns_list = [portfolio_returns.shares_per_date_dict[ticker]['current_amount'] for ticker in portfolio_returns.shares_per_date_dict]
portfolio_cumsum_returns = pd.concat(tickers_returns_list, axis=1).sum(axis=1)
portfolio_to_plot = portfolio_returns.plot_portfolio(total_amounts, transaction_data['date'].min(), portfolio_returns.today)
portfolio_to_plot = portfolio_to_plot.reset_index()
portfolio_to_plot.columns = ['Date', 'Return']

portfolio = Portfolio(transaction_data, sectors_data)
portfolio.run()      
portfolio_table = portfolio.plot_portoflio_tbl()

if len(dividends_data) > 0:
    ## INCOME
    income = Income(transaction_data, dividends_data)
    monthly_income, yearly_income = income.run()
    income_dict = json.dumps({'monthly':monthly_income, 'yearly':yearly_income})

    ## GROWTH
    tickers = portfolio.portfolio_data.ticker.to_list()
    growth = DividendGrowth(income.transaction_data[['ticker','start_payment_date']], dividends_data, tickers)
    growth_df = growth.run()
    
    ## HISTORICAL YIELD ON COST
    tickers_freq = dividends_data.groupby(['ticker','frequency'])['payment_date'].max().reset_index().set_index('ticker')['frequency']
    dividend_daily_data = income.dividend_daily_data[tickers].copy()
    for ticker in tickers:
        dividend_daily_data[ticker] = dividend_daily_data[ticker] * tickers_freq.loc[ticker]
        dividend_daily_data[ticker] = dividend_daily_data[ticker].replace(0, np.nan)
        dividend_daily_data[ticker] = dividend_daily_data[ticker].fillna(method='ffill')
    valid_index_tickeres = (dividend_daily_data.tail(1).isnull() == False).T
    valid_tickers = (valid_index_tickeres[valid_index_tickeres].dropna().index)
    dividend_daily_data['SUM'] = dividend_daily_data.sum(axis=1)
    dividend_daily_data['NET'] = dividend_daily_data['SUM'] * (1 - income.tax_rate)
    tickers_amount_paid_list = [portfolio_returns.shares_per_date_dict[ticker]['amount_paid'] for ticker in valid_tickers]
    portfolio_cumsum_amount_paid = pd.concat(tickers_amount_paid_list, axis=1).sum(axis=1)
    portfolio_cumsum_amount_paid = portfolio_cumsum_amount_paid.reset_index()
    portfolio_cumsum_amount_paid.columns = ['Date', 'Amount_Paid']
    hist_yield_on_cost = portfolio_cumsum_amount_paid.set_index('Date')
    hist_yield_on_cost = hist_yield_on_cost.merge(dividend_daily_data[['SUM', 'NET']], left_index=True, right_index=True, how='left')
    hist_yield_on_cost['yield_on_cost'] = 100*(hist_yield_on_cost['NET'] / hist_yield_on_cost['Amount_Paid'])
    
# Save data to Redis
r.set('transaction_data', transaction_data.to_json())
r.set('portfolio_to_plot', portfolio_to_plot.to_json())
r.set('portfolio_table', portfolio_table.to_json())
r.set('portfolio_cumsum_returns', portfolio_cumsum_returns.to_json())
if len(dividends_data) > 0:
    r.set('dividends_data', dividends_data.reset_index().to_json())
    r.set('income_dict', income_dict)
    r.set('growth_table', growth_df.to_json())
    r.set('hist_yield_on_cost', hist_yield_on_cost[['yield_on_cost']].to_json())