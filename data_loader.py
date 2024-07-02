import os
import gspread
import pandas as pd
import yfinance as yf
from oauth2client.service_account import ServiceAccountCredentials

from data_preprocessor import TransactionDataPreprocessing, DividendDataPreprocessor
from utils import get_div_hist_per_stock


class DataLoader:
    
    def __init__(self):
        pass
    
    def get_daily_prices_data(self, tickers, start_time):
        """
        Get daily prices for a list of tickers from Yahoo Finance
        """
        daily_price = {}
        for t in tickers:
            ticker_price_history = yf.Ticker(t).history(period='1d', start=start_time, auto_adjust=False)
            ticker_price_history.index = pd.to_datetime(ticker_price_history.index).strftime('%Y-%m-%d')
            daily_price[t] = ticker_price_history.to_dict()['Close']
            
        return daily_price

    def get_transaction_data(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name('secrets/creds.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("dividend_data").sheet1  # Open the first sheet
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df

    def get_sectors_data(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('secrets/creds.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("sectors").sheet1  # Open the first sheet
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    
    def get_dividend_data(self, transaction_data):
        """
        Get the dividend data
        """
        dividends_dict = {}
        try:
            tickers = transaction_data.ticker.unique()
            for ticker in tickers:
                dividends_dict[ticker] = get_div_hist_per_stock(ticker)
                
            dividend_preprocessor = DividendDataPreprocessor()
            dividend_preprocessor.preprocess_multiple_tickers_data(dividends_dict)
            dividends_data = dividend_preprocessor.df.copy()
        except:
            dividends_data = pd.DataFrame()
        
        return dividends_data

    def run(self):
    # Fetch table data from Google Sheets
        transaction_data = self.get_transaction_data()
        transaction_preprocessor = TransactionDataPreprocessing(transaction_data)
        transaction_preprocessor.run()
        transaction_data = transaction_preprocessor.df.copy()
        sectors_data = self.get_sectors_data()
        daily_prices = self.get_daily_prices_data(transaction_data.ticker.unique(), transaction_data.date.min())
        dividend_dict = self.get_dividend_data(transaction_data)
        
        return transaction_data, sectors_data, daily_prices, dividend_dict