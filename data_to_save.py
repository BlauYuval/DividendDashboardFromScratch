import os
import json
import redis
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

# Save data to Redis
r.set('transaction_data', transaction_data.to_json())
r.set('portfolio_to_plot', portfolio_to_plot.to_json())
r.set('portfolio_table', portfolio_table.to_json())
if len(dividends_data) > 0:
    r.set('dividends_data', dividends_data.reset_index().to_json())
    r.set('income_dict', income_dict)
    r.set('growth_table', growth_df.to_json())
