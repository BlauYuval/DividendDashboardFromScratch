import os
import redis
import pandas as pd
from Portfilio import Portfolio
from PortfolioReturns import PortfolioReturns
from data_loader import DataLoader
# from secrets import redis_password
from dotenv import load_dotenv

load_dotenv()

# Initialize Redis connection
redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASS')  # Replace with the password from the image

r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

data_loader = DataLoader()
transaction_data, sectors_data, daily_prices = data_loader.run()

portfolio_returns = PortfolioReturns(transaction_data.rename(columns={'signed_shares':'shares'}), daily_prices)
total_amounts = portfolio_returns.run()
portfolio_to_plot = portfolio_returns.plot_portfolio(total_amounts, transaction_data['date'].min(), portfolio_returns.today)
portfolio_to_plot = portfolio_to_plot.reset_index()
portfolio_to_plot.columns = ['Date', 'Return']

portfolio = Portfolio(transaction_data, sectors_data)
portfolio.run()      
portfolio_table = portfolio.plot_portoflio_tbl()

# Save data to Redis
r.set('portfolio_to_plot', portfolio_to_plot.to_json())
r.set('portfolio_table', portfolio_table.to_json())
