# In this file, we will create the income data from the transaction data and dividend data.
# We will create a class called Income that produce the monthly income streamlit bullet, bar chart of monthly/quaterly/yearly income, 
# and forecasted for the next 12 months.

import pandas as pd

class Income:
    
    def __init__(self, transaction_data, dividend_data):
        self.transaction_data = transaction_data
        self.dividends_data = dividend_data
        self.tax_rate = 0.25
        
    def _get_start_date_for_payments(self, ticker, date, dividends_data):
        """
        For a given ticker and date, get the start date for the payments
        Args:
            ticker (str): ticker
            date (str): date
            dividends_data (pd.DataFrame): dividends data
        Returns:
            start_date (pd.Timestamp) : start date for the payments
        """
        dividends = dividends_data[dividends_data.ticker == ticker]
        dividends_ex_date_after_transaction = dividends[dividends.ex_date > date.strftime("%Y-%m-%d")]
        if dividends_ex_date_after_transaction.shape[0] > 0:
            start_date = pd.to_datetime(dividends_ex_date_after_transaction.iloc[0]['ex_date'])
        else:
            start_date = dividends[dividends.ex_date <= date.strftime("%Y-%m-%d")].iloc[-1]['payment_date']
            start_date = (pd.to_datetime(start_date) + pd.Timedelta(1,'d'))
            
        return start_date    
        
    def _add_start_payment_date_to_transaction_data(self):
        """
        Add the start payment date to the transaction data
        """
        self.dividends_data.sort_values(by=['ticker', 'ex_date'], inplace=True)
        self.transaction_data['start_payment_date'] = self.transaction_data.apply(
            lambda row: self._get_start_date_for_payments(row.ticker, row.date, self.dividends_data), axis=1
            )
        
    def _init_daily_data(self):
        """
        Initialize the daily data for the income class
        """
        dividend_daily_data = pd.DataFrame(index = pd.date_range(self.transaction_data['date'].min(), pd.Timestamp.today()))
        dividend_daily_data = dividend_daily_data.merge(pd.pivot_table(self.transaction_data, 
                                                                    index='start_payment_date', 
                                                                    columns='ticker', 
                                                                    values='signed_shares').fillna(0), 
                                                        how='left', right_index=True,left_index=True)
        self.dividend_daily_data = dividend_daily_data.fillna(0).cumsum()
    
    def get_income_data(self):
        """
        Get the income data from the transaction data and dividend data
        Store it in the dividend_daily_data attribute
        """
        self._add_start_payment_date_to_transaction_data()
        self._init_daily_data()
        tickers = self.transaction_data.ticker.unique()
        for ticker in tickers:
            dividends = self.dividends_data[self.dividends_data.ticker == ticker]
            if len(dividends) > 0:
                dividends = dividends.rename(columns = {'payment_date':'date', 'value':f'{ticker}_dividends'})
                dividends['date'] = pd.to_datetime(dividends['date'])

                self.dividend_daily_data = self.dividend_daily_data.merge(dividends[['date', f'{ticker}_dividends']].set_index('date'), 
                                                                how='left', right_index=True,left_index=True)
                self.dividend_daily_data[f'{ticker}_dividends'] = self.dividend_daily_data[f'{ticker}_dividends'].fillna(0) 

                self.dividend_daily_data[ticker] = self.dividend_daily_data[ticker]*self.dividend_daily_data[f'{ticker}_dividends']
                self.dividend_daily_data.drop([f'{ticker}_dividends'], axis=1, inplace=True)
            else:
                self.dividend_daily_data.drop([ticker], axis=1, inplace=True)
                
        self.dividend_daily_data['SUM'] = self.dividend_daily_data.sum(axis=1)
        self.dividend_daily_data['NET'] = self.dividend_daily_data['SUM']*(1 - self.tax_rate)
        
    def get_monthly_and_yearly_income(self):
        
        ticker_shares = self.transaction_data.groupby('ticker').agg({'signed_shares':'sum'})
        ticker_last_amount = self.dividends_data[self.dividends_data.groupby(['ticker'])['payment_date'].transform('max') == self.dividends_data['payment_date']].set_index('ticker')[['value','frequency']]
        income = ticker_shares.merge(ticker_last_amount, left_index=True, right_index=True)
        # income['frequency'] = income['frequency'].apply(lambda x: 12 if x == 'monthly' else 4 if x == 'quarterly' else 2 if x == 'semi-annual' else 1)
        income['amount'] = income['signed_shares']*income['value']*income['frequency']
        income['amount_after_tax'] = income['amount']*(1 - self.tax_rate)
        
        monthly_income = income.amount_after_tax.sum()/12
        yearly_income = income.amount_after_tax.sum()   
        
        return monthly_income, yearly_income 
       
    # def get_income_streamlit_bullet(self, monthly_income, yearly_income ):
    #     """
    #     Get the monthly income streamlit bullet.
    #     Do it by sum the NET column of the past 3 whole months and devide it by 3
    #     """
    #     # ticker_shares = self.transaction_data.groupby('ticker').agg({'signed_shares':'sum'})
    #     # ticker_last_amount = self.dividends_data[self.dividends_data.groupby(['ticker'])['payment_date'].transform('max') == self.dividends_data['payment_date']].set_index('ticker')[['value','frequency']]
    #     # income = ticker_shares.merge(ticker_last_amount, left_index=True, right_index=True)
    #     # # income['frequency'] = income['frequency'].apply(lambda x: 12 if x == 'monthly' else 4 if x == 'quarterly' else 2 if x == 'semi-annual' else 1)
    #     # income['amount'] = income['signed_shares']*income['value']*income['frequency']
    #     # income['amount_after_tax'] = income['amount']*(1 - self.tax_rate)
        
    #     # monthly_income = income.amount_after_tax.sum()/12
    #     # yearly_income = income.amount_after_tax.sum()

    #     kpi1, kpi2 = st.columns(2)

    #     # fill in those three columns with respective metrics or KPIs
    #     kpi1.metric(
    #         label="Monthly Income",
    #         value=f"{round(monthly_income, 2)}$",
    #     )
    #     kpi2.metric(
    #         label="Yearly Income",
    #         value=f"{round(yearly_income, 2)}$",
    #     )

    # def get_income_bar_chart(self):
    #     """
    #     Plot the income bar chart for the given period - montly, quaterly, yearly
    #     """  
        
    #     period = st.selectbox(
    #     "Choose Period",
    #     ("Monthly", "Quaterly", "Yearly"),
    #     index=None,
    #     placeholder="Monthly",
    #     )      
        
    #     data = self.dividend_daily_data.reset_index().copy()
    #     chart_data = data.groupby(data['index'].dt.to_period('M'))['NET'].sum()
    #     chart_data.index = chart_data.index.strftime('%Y-%m')
    #     if period == 'Monthly':
    #         chart_data = data.groupby(data['index'].dt.to_period('M'))['NET'].sum()
    #         chart_data.index = chart_data.index.strftime('%Y-%m')
    #     elif period == 'Quaterly':
    #         chart_data = data.groupby(data['index'].dt.to_period('Q'))['NET'].sum()
    #         chart_data.index = chart_data.index.strftime('%Y-%m')
    #     elif period == 'Yearly':
    #         chart_data = data.groupby(data['index'].dt.to_period('Y'))['NET'].sum()
    #         chart_data.index = chart_data.index.strftime('%Y')
            
    #     st.bar_chart(chart_data)
        
        
    def run(self):
        self.get_income_data()
        monthly_income, yearly_income = self.get_monthly_and_yearly_income()
        
        return monthly_income, yearly_income
