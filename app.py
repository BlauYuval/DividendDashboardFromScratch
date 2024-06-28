import os
import json
from flask import Flask, render_template
from flask_basicauth import BasicAuth
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for Matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from Portfilio import Portfolio
from PortfolioReturns import PortfolioReturns
from data_loader import DataLoader

app = Flask(__name__)

# Basic Auth Configuration
app.config['BASIC_AUTH_USERNAME'] = 'yourusername'
app.config['BASIC_AUTH_PASSWORD'] = 'yourpassword'
basic_auth = BasicAuth(app)

@app.route('/')
@basic_auth.required
def index():

    data_loader = DataLoader()
    transaction_data, sectors_data, daily_prices = data_loader.run()
    
    portfolio = Portfolio(transaction_data, sectors_data)
    portfolio.run()  
    portfolio_returns = PortfolioReturns(transaction_data.rename(columns={'signed_shares':'shares'}), daily_prices)
    total_amounts = portfolio_returns.run()
    portfolio_to_plot = portfolio_returns.plot_portfolio(total_amounts, transaction_data['date'].min(), portfolio_returns.today)
    portfolio_to_plot = portfolio_to_plot.reset_index()
    portfolio_to_plot.columns = ['Date', 'Return']
    plt.figure(figsize=(10,6), facecolor='none')
    sns.set(style="darkgrid")
    ax = sns.lineplot(data=portfolio_to_plot.reset_index(), y='Return', x='Date', color="white")
    ax.set_facecolor('none')  # Set the plot background to be transparent
    ax.grid(False)  # Remove the grid
    plt.xticks(color='white')  # Set x-axis labels to white
    plt.yticks(color='white')  # Set y-axis labels to white
    plt.xlabel('Date', color='white')  # Set x-axis title to white
    plt.ylabel('Return', color='white')  # Set y-axis title to white
    plt.title('Portfolio Returns', color='white')  # Set plot title to white
    plt.savefig('static/plot.png')
    plt.close()
    
    
    portfolio_table = portfolio.plot_portoflio_tbl()
    table_html = portfolio_table.to_html(classes='dataframe', border=2)

    return render_template('index.html', table=table_html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
