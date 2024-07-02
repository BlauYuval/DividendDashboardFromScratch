import pandas as pd
import numpy as np

class TransactionDataPreprocessing:
    
    def __init__(self, df):
        self.df = df

    def run(self):

        self.df['date'] = pd.to_datetime(self.df['date'], dayfirst=True)
        self.df.sort_values('date', inplace=True)
        self.df['activity_type'] = self.df['activity_type'].apply(lambda x: 1 if x=='buy' else -1 if x=='sell' else 0)
        self.df['signed_shares'] = self.df['activity_type'] * self.df['shares']
        self.df =  self.df[['date', 'ticker', 'stock_price', 'signed_shares']].copy()
        
        
class DividendDataPreprocessor:
    
    def __init__(self) -> None:
        pass
        
    def preprocess_single_ticker_data(self, df, ticker):
        df = df.copy()
        df.reset_index(inplace=True)
        df[['currency', 'value']] = df['amount'].apply(lambda x: ' '.join((x[:1], x[1:]))).str.split(n=1, expand=True)
        df['currency'] = df['currency'].str.replace('$', 'USD', regex=False)
        df['value'] = df['value'].astype('float')
        df.rename(columns= {'exOrEffDate': 'ex_date', 'paymentDate': 'payment_date'}, inplace=True)    
        df['ticker'] = ticker
        df['ex_date'] = pd.to_datetime(df['ex_date']).dt.strftime("%Y-%m-%d")
        df['payment_date'] = pd.to_datetime(df['payment_date'].replace('N/A', None))
        # df['payment_date'] = df['payment_date'].interpolate()
        df['payment_date'] = np.where(df['payment_date'].isnull(), pd.to_datetime(df['ex_date']) + pd.Timedelta(14, 'd'), df['payment_date'])
        frquency = round(df.groupby(df['payment_date'].dt.to_period('Y'))['value'].count()[-6:-1].mean())
        if frquency >= 12:
            df['frequency'] = 12
        elif frquency >= 3:
            df['frequency'] = 4
        elif frquency >= 1.5:
            df['frequency'] = 2
        else:
            df['frequency'] = 1
        df['payment_date'] = df['payment_date'].dt.strftime("%Y-%m-%d")
        df = df[df['type'] == 'Cash'].reset_index(drop=True)
        
        
        return df[['ticker','ex_date','payment_date','value','currency','frequency']]
        
    def preprocess_multiple_tickers_data(self, dfs:dict):
        """
        Assuming our input is a dictionary conatains the ticker as key and the dividend data as value
        """
        self.df = pd.concat([self.preprocess_single_ticker_data(dfs[ticker], ticker) for ticker in dfs])