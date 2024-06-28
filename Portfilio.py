# In this script, we will create the portfolio data from the transaction data and sectors data.
# We will just present the stocks in the portfolio and the sectors they belong to.
# It will contain the following:
# - The stocks in the portfolio
# - The sectors they belong to
# - The total amount invested in each sector
# - The total amount invested in the portfolio

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from utils import _get_close_price

class Portfolio:
    
    def __init__(self, transaction_data, sectors_data):
        self.transaction_data = transaction_data
        self.sectors_data = sectors_data
        self.portfolio_data = None
        self.portfolio_by_sectors_data = None
        
    def get_current_holdings(self):
        """
        Get the current holdings from the transaction data
        """
        current_tickers = self.transaction_data.groupby('ticker').agg({'signed_shares':'sum'})
        current_tickers = current_tickers[current_tickers.signed_shares > 0].index.to_list()

        self.transaction_data['Amount Paid'] = self.transaction_data['signed_shares']*self.transaction_data['stock_price']
        self.transaction_data['Current Amount'] = (
            self.transaction_data.apply(lambda x: _get_close_price(x['ticker']), axis=1)*self.transaction_data['signed_shares']
        )
        self.balance = self.transaction_data['Current Amount'].sum()
        self.total_invested = self.transaction_data['Amount Paid'].sum()
        self.total_return = 100*((self.balance - self.total_invested) / self.total_invested)
        
        self.portfolio_data = self.transaction_data.groupby('ticker').agg({'Amount Paid':'sum', 'Current Amount':'sum'})
        self.portfolio_data['Return'] = (self.portfolio_data['Current Amount'] - self.portfolio_data['Amount Paid'])/self.portfolio_data['Amount Paid']
        self.portfolio_data['Return'] = (100*self.portfolio_data['Return']).apply(lambda x: f"{round(x, 2)}%")
        self.portfolio_data.reset_index(inplace=True)
        self.portfolio_data = self.portfolio_data[self.portfolio_data.ticker.isin(current_tickers)]


    def get_sectors(self):
        """
        Get the sectors from the sectors data
        """
        self.portfolio_data = self.portfolio_data.merge(self.sectors_data, how='left', on='ticker')
        
    def get_sector_investments(self):
        """
        Get the sector investments from the portfolio data
        """
        self.portfolio_by_sectors_data = self.portfolio_data.groupby('sector').agg({'Amount Paid':'sum'})
        self.portfolio_by_sectors_data.reset_index(inplace=True)

    def plot_portoflio_tbl(self):
        """
        Process and plot the holding table
        """
        table_for_plot = self.portfolio_data.set_index('ticker').copy()
        table_for_plot['Amount Paid'] = table_for_plot['Amount Paid'].apply(lambda x: f'{int(x):,}$')
        table_for_plot['Current Amount'] = table_for_plot['Current Amount'].apply(lambda x: f'{int(x):,}$')
        table_for_plot = table_for_plot.rename(columns={'sector':'Sector', 'industry':'Industry'})
        table_for_plot = table_for_plot.sort_values('Current Amount', ascending=False)
        
        return table_for_plot
        
    def plot_pie_by_sectors(self):
        """
        Plot the bar chart by sectors
        """
        df_for_plot = self.portfolio_by_sectors_data.copy()
        df_for_plot['Amount Paid'] = df_for_plot['Amount Paid'].apply(lambda x: round(x, 2))
        df_for_plot['percent'] = (df_for_plot['Amount Paid']/df_for_plot['Amount Paid'].sum()).apply(lambda x: round(x, 2))*100     
        df_for_plot = df_for_plot.sort_values('percent', ascending=True)
        
        st.bar_chart(data=df_for_plot, x='sector', y='percent', height=500)

        
        
    def run(self):
        """
        Run the portfolio
        """
        self.get_current_holdings()
        self.get_sectors()
        self.get_sector_investments()
        
        