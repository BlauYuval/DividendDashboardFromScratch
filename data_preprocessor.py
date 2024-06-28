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