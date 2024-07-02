import pandas as pd
import numpy as np

class DividendGrowth:
    """
    In this class we will calculate the dividend growth rate for each stock in the portfolio.
    We will calculate the past growth rate, and the cuurent growth rate since the payment starts.
    """
    def __init__(self, transaction_data, dividends_data, current_holdings_tickers):
        self.transaction_data = transaction_data
        self.dividends_data = dividends_data
        self.current_holdings_tickers = current_holdings_tickers
        
    def get_first_and_last_payment_date_and_amount(self, ticker, start_payment_date):
        """
        Calculate the first and last payment date and amount for a given ticker since buying date.
        """
        payments = self.dividends_data[
            (self.dividends_data.ticker == ticker) & (pd.to_datetime(self.dividends_data.payment_date) > start_payment_date)
            ].sort_values(by='payment_date')
        if len(payments) == 0:
            first_date,first_amount, last_date, last_amount, num_payments = None, None, None, None, None
        else:
            first_date, last_date = payments.payment_date.iloc[0], payments.payment_date.iloc[-1]
            first_amount, last_amount = payments.value.iloc[0], payments.value.iloc[-1]
            num_payments = len(payments)
        
        return first_date,first_amount, last_date, last_amount, num_payments
 
    def _calc_years_of_growth_since_buying(self, frequency, num_of_payments, first_amount, last_amount):
        """
        Calculate the number of years of growth for a given stock.
        """
        years_of_growth = None
        if num_of_payments is not None:
            num_payments_div_freq = num_of_payments/frequency
            if num_payments_div_freq <= 1:
                if last_amount > first_amount:
                    years_of_growth = 1
                else:
                    years_of_growth = 0
            else:
                years_of_growth = np.floor(num_payments_div_freq)
                    
        
        return years_of_growth

    def _calc_cagr(self, first_amount, last_amount, years_of_growth):
        """
        Calculate the CAGR for a given stock.
        """
        cagr = None
        if (years_of_growth > 0) and (years_of_growth== years_of_growth) and (first_amount == first_amount):
            cagr = (last_amount/first_amount)**(1/years_of_growth)-1
        
        return round(cagr*100, 2) if cagr is not None else None   
    
    def get_forward_payments_cagr(self, tickers_df, dividends_data):
        """
        Calculate the forward payments CAGR for each stock in the portfolio.
        """
        tickers_df = tickers_df.copy()
        tickers_df['data'] = tickers_df.apply(lambda row: self.get_first_and_last_payment_date_and_amount(row.ticker, row.start_payment_date), axis=1)
        tickers_df[['first_payment_date','first_amount', 'last_payment_date', 'last_amount', 'num_payments']] = pd.DataFrame(tickers_df.data.tolist(), index= tickers_df.index)
        tickers_df.drop(columns=['data'], inplace=True)
        tickers_df['years_of_growth_since_holding'] = tickers_df.apply(lambda row: self._calc_years_of_growth_since_buying(row.frequency, row.num_payments, row.first_amount, row.last_amount), axis=1)
        tickers_df['CAGR Since Holding'] =  tickers_df.apply(lambda row: self._calc_cagr(row.first_amount, row.last_amount, row.years_of_growth_since_holding), axis=1)
        # tickers_df = tickers_df[['ticker','first_payment_date','years_of_growth_since_holding','CAGR Since Holding']].sort_values('first_payment_date').drop_duplicates(subset=['ticker'], keep='first').reset_index(drop=True)  
        tickers_df = tickers_df[['ticker','first_payment_date','years_of_growth_since_holding','CAGR Since Holding']].reset_index(drop=True)     
        return tickers_df  

    def _get_annaul_previous_payments(self, ticker, start_payment_date):
        
        ticker_df = self.dividends_data[self.dividends_data.ticker == ticker].copy()
        ticker_df['payment_date'] = pd.to_datetime(ticker_df.payment_date)
        ticker_df['ex_date'] = pd.to_datetime(ticker_df.ex_date)
        payments_before_start_date = ticker_df[ticker_df.ex_date <= start_payment_date].copy()
        payments_before_start_date = payments_before_start_date.sort_values(by='payment_date', ascending=False)
        freq = payments_before_start_date.iloc[0]['frequency']
        
        return payments_before_start_date.iloc[::freq][:11]
    
    def _calc_historical_years_of_growth(self, payment_list):
            
        years_of_growth = 0
        for i in range(len(payment_list)-1):
            if payment_list[i] > payment_list[i+1]:
                years_of_growth += 1
            else:
                break
        return years_of_growth

    def previous_payments_cagr(self, tickers_df,  dividends_data):

        prev_cagr = {}
        for i in range(len(tickers_df)):
            
            ticker = tickers_df.iloc[i]['ticker']
            start_payment_date = tickers_df.iloc[i]['start_payment_date']
            annual_prev_payments = self._get_annaul_previous_payments(ticker, start_payment_date)
            years_of_growth = self._calc_historical_years_of_growth(annual_prev_payments.value.to_list())
            annual_prev_payments = annual_prev_payments[:years_of_growth+1]
            cagr_10y = self._calc_cagr(annual_prev_payments.iloc[min(years_of_growth,10)]['value'], annual_prev_payments.iloc[0]['value'], min(years_of_growth,10))
            cagr_5y = self._calc_cagr(annual_prev_payments.iloc[min(years_of_growth,5)]['value'], annual_prev_payments.iloc[0]['value'], min(years_of_growth,5))
            cagr_3y = self._calc_cagr(annual_prev_payments.iloc[min(years_of_growth,3)]['value'], annual_prev_payments.iloc[0]['value'], min(years_of_growth,3))
            cagr_1y = self._calc_cagr(annual_prev_payments.iloc[min(years_of_growth,1)]['value'], annual_prev_payments.iloc[0]['value'], min(years_of_growth,1))
            prev_cagr[i] = [cagr_10y, cagr_5y, cagr_3y, cagr_1y]
            
        prev_cagr_df = pd.DataFrame.from_dict(prev_cagr, orient='index', columns=['cagr_10y', 'cagr_5y', 'cagr_3y', 'cagr_1y'])
        prev_cagr_df = pd.concat([tickers_df, prev_cagr_df], axis=1).drop(columns=['start_payment_date', 'frequency'], axis=1)
        return prev_cagr_df
    
    
    def color_cagr(self, x):
        # set font color to red for keys whose corresponding v is positive
        # all other values have default font color
        return pd.DataFrame('', index=x.index, columns=x.columns).assign(
            **{"CAGR Since Holding": np.where(
                x['CAGR Since Holding'] > x[['1Y CAGR', '3Y CAGR', '5Y CAGR', '10Y CAGR']].max(axis=1),
                "color:forestgreen",
                np.where(x['CAGR Since Holding'] < x[['1Y CAGR', '3Y CAGR', '5Y CAGR', '10Y CAGR']].min(axis=1),
                        "color:salmon",
                        np.where(x['CAGR Since Holding'] == x['CAGR Since Holding'], "color:lawngreen", "")
                        )
            )}
        )


    def get_tickers_payment_start_date_and_freq(self, tickers_payments_start):
        
        tickers_df = tickers_payments_start[tickers_payments_start.ticker.isin(self.current_holdings_tickers)].copy()
        tickers_df = tickers_df.merge(
            self.dividends_data.sort_values('payment_date').drop_duplicates(subset=['ticker','frequency'], keep='last')[['ticker','frequency']], 
            on='ticker', how='left'
            )    
        
        return tickers_df
    
    def merge_prev_and_forward_growth(self):
        """
        Run the dividend growth calculations.
        """
        tickers_payments_start = self.transaction_data[['ticker','start_payment_date']].copy()
        tickers_df = self.get_tickers_payment_start_date_and_freq(tickers_payments_start)
        forward_payments_cagr = self.get_forward_payments_cagr(tickers_df, self.dividends_data)
        prev_payments_cagr = self.previous_payments_cagr(tickers_df, self.dividends_data)
        growth_df = pd.concat(
            [tickers_df[['start_payment_date']], prev_payments_cagr, forward_payments_cagr.drop(['ticker'], axis=1)[['CAGR Since Holding']]], 
            axis=1)
        
        return growth_df.drop_duplicates(subset=['ticker'], keep='first').reset_index(drop=True)
        
    def plot(self, growth_df):
        
        # apply the highlighter function red_or_auto to 'v' and'key' columns of df
        df = growth_df.copy()
        df = df.set_index('ticker')
        df['start_payment_date']  = df['start_payment_date'].dt.strftime('%Y-%m-%d')
        df = df.rename(columns={'start_payment_date':'First Div Payment', 'cagr_1y':'1Y CAGR', 'cagr_3y':'3Y CAGR', 'cagr_5y':'5Y CAGR', 'cagr_10y':'10Y CAGR'})
        df = df[['First Div Payment', 'CAGR Since Holding', '1Y CAGR', '3Y CAGR', '5Y CAGR', '10Y CAGR']].copy()
        df_styled = df.style.apply(self.color_cagr, axis=None, subset=['1Y CAGR', '3Y CAGR', '5Y CAGR', '10Y CAGR', 'CAGR Since Holding'])
        return df_styled.format(precision=2)
    
    def run(self):
 
        growth_df = self.merge_prev_and_forward_growth()
        
        return growth_df