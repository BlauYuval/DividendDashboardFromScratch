import pandas as pd
import yfinance as yf
import streamlit as st

class PortfolioReturns:
    
    def __init__(self, portfolio_df, daily_price):
        self.portfolio_df = portfolio_df
        self.daily_price = daily_price
        self.today = pd.to_datetime('today').strftime('%Y-%m-%d')
        self.shares_per_date_dict = {}
        self.other_ticker = None
        
    def _convert_daily_data_to_df(self):
        """
        convert daily price dict to df
        :return: 
        """
        price_data_df = pd.DataFrame()
        for t in self.daily_price:
            ticker_df = pd.DataFrame.from_dict(self.daily_price[t], orient='index').reset_index()
            ticker_df['ticker'] = t
            ticker_df.columns = ['date', 'close', 'ticker']
            price_data_df = pd.concat([price_data_df, ticker_df])
        price_data_df['date'] = pd.to_datetime(price_data_df['date'])
        
        return price_data_df
    
    def get_portfolio_returns(self):
        """
        get portfolio returns by calculating the daily returns of each stock and summing them up.
        Then compare it to the amount paid for the stocks, to get relative returns, so we can compare it to the market.
        :return: 
        """
        price_data_df = self._convert_daily_data_to_df()
        for ticker in self.portfolio_df.ticker.unique():
            ticker_df = self.portfolio_df[self.portfolio_df.ticker == ticker].sort_values('date').copy()
            daily_ticker = pd.DataFrame(index=pd.date_range(ticker_df['date'].min(), self.today))
            daily_ticker['shares'] = 0.0
            daily_ticker['amount_paid'] = 0.0
            daily_ticker['current_price'] = 0.0
            for row in ticker_df.iterrows():
                daily_ticker.loc[row[1]['date']:, 'shares'] = daily_ticker.loc[row[1]['date']:, 'shares'] + row[1]['shares']
                daily_ticker.loc[row[1]['date']:, 'amount_paid'] = daily_ticker.loc[row[1]['date']:, 'amount_paid'] + (row[1]['shares']*row[1]['stock_price'])
                daily_ticker.loc[row[1]['date']:, 'current_price'] = price_data_df[price_data_df.ticker==ticker].set_index('date').loc[row[1]['date']:,'close']
            daily_ticker.fillna(method='ffill',inplace=True)
            daily_ticker['current_amount'] = daily_ticker['shares']*daily_ticker['current_price']
            self.shares_per_date_dict[ticker] = daily_ticker
            
    def get_total_amounts(self):
        """
        get the amount paid and the current amount for each stock
        :return: 
        """
        amount_paid = pd.concat([self.shares_per_date_dict[t]['amount_paid'] for t in self.shares_per_date_dict], axis=1)
        current_amount = pd.concat([self.shares_per_date_dict[t]['current_amount'] for t in self.shares_per_date_dict], axis=1) 
        total_amounts = pd.DataFrame({'amount_paid':amount_paid.sum(axis=1), 'current_amount':current_amount.sum(axis=1)})
        
        return total_amounts
    
    def _add_comparison_ticker(self):
        """
        add comparison ticker to the portfolio
        :param ticker: 
        :return: 
        """
        ticker = st.text_input('Valid Uppercase Ticker:', 'SCHD')
        try:
            prices = yf.Ticker(ticker).history(start=self.portfolio_df['date'].min(), auto_adjust=False)
            prices.index = pd.to_datetime(prices.index.strftime('%Y-%m-%d'))
            prices.Close = prices.Close.apply(lambda x: round(x, 2))
            other_ticker_prices = pd.DataFrame(prices.Close).rename(columns={'Close':ticker})
            dates = pd.DataFrame(index=pd.date_range(self.portfolio_df['date'].min(), self.today))
            other_ticker_prices = pd.concat([dates, other_ticker_prices], axis=1).fillna(method='ffill') 
            self.other_ticker = ticker  
        except:
            st.write(f"Could not find {ticker} in Stock Market. Please try again (maybe upper case ticker?)")
            other_ticker_prices = pd.DataFrame()
        
        return other_ticker_prices
    
    def plot_portfolio(self, portfolio_total_amounts, start, end):
        """
        Plot the portfolio returns and the comparison ticker if exists
        """
        # other_ticker_prices = self._add_comparison_ticker()
        portfolio_total_amounts = pd.concat([portfolio_total_amounts, pd.DataFrame()], axis=1)
        df_dates = portfolio_total_amounts.loc[start:end].copy()
        df_dates['Portfolio Returns'] = ((df_dates.current_amount-df_dates.amount_paid)  / (df_dates.amount_paid))
        df_dates.drop(['amount_paid', 'current_amount'], axis=1, inplace=True)
        # if not other_ticker_prices.empty:
        #     df_dates[self.other_ticker] = (df_dates[self.other_ticker] - df_dates[self.other_ticker].iloc[0]) / df_dates[self.other_ticker].iloc[0]
        #     df_dates.rename(columns={self.other_ticker:f'{self.other_ticker} Returns'}, inplace=True)
        
        # st.line_chart(df_dates)
        return df_dates
        
    def run(self):
        
        self.get_portfolio_returns()
        total_amounts = self.get_total_amounts()

        return total_amounts
