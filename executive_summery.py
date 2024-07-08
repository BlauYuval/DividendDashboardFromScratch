# In this script wew will create executive summery for the entire app.
# This should include streamlit metrics, including this info: Total Return, Dividend Yield, Yield on Cost, Average Dividend Growth, Income.

class ExecutiveSummery:
    
    def __init__(self, portfolio_data):
        self.portfolio_data = portfolio_data
        
    def get_total_return(self):
        """
        Get the total return
        """
        self.portfolio_data['Amount Paid'] = self.portfolio_data['Amount Paid'].apply(lambda  x: int(x.replace(',', '').replace('$', '')))
        self.portfolio_data['Current Amount'] = self.portfolio_data['Current Amount'].apply(lambda  x: int(x.replace(',', '').replace('$', '')))
        total_return = self.portfolio_data['Current Amount'].sum()
        amount_invested = self.portfolio_data['Amount Paid'].sum()
        return_yield = 100*((total_return - amount_invested) / amount_invested)
        return total_return, amount_invested, return_yield
    
    def get_dividend_yield(self, total_return, amount_invested, yearly_income):
        """
        Get the dividend yield
        """
        dividend_yield = 100*(yearly_income / total_return)
        yield_on_cost = 100*(yearly_income / amount_invested)
        return dividend_yield, yield_on_cost
        
    def get_average_dividend_growth(self, growth_df):
        """
        Get the average dividend growth
        """
        df = growth_df.set_index('Ticker').merge(self.portfolio_data, left_index=True, right_index=True)
        df = df[df['Cagr since holding'] > 0].copy()
        average_dividend_growth = (df['Cagr since holding']*df['Amount Paid']).sum()/df['Amount Paid'].sum()
        
        return average_dividend_growth
    