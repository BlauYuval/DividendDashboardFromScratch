import matplotlib.pyplot as plt
import seaborn as sns


def prepare_to_vizualize_income_bar(dividend_daily_data, period):
    
    data = dividend_daily_data.reset_index().copy()
    chart_data = data.groupby(data['index'].dt.to_period('M'))['NET'].sum()
    chart_data.index = chart_data.index.strftime('%Y-%m')
    if period == 'Monthly':
        chart_data = data.groupby(data['index'].dt.to_period('M'))['NET'].sum()
        chart_data.index = chart_data.index.strftime('%Y-%m')
    elif period == 'Quaterly':
        chart_data = data.groupby(data['index'].dt.to_period('Q'))['NET'].sum()
        chart_data.index = chart_data.index.strftime('%Y-%m')
    elif period == 'Yearly':
        chart_data = data.groupby(data['index'].dt.to_period('Y'))['NET'].sum()
        chart_data.index = chart_data.index.strftime('%Y')
    chart_data = chart_data.reset_index()
    chart_data.columns = [period[:-2], 'Income']
        
    return chart_data
    
def vizualize_income_bar(dividend_daily_data, period):
    
    chart_data = prepare_to_vizualize_income_bar(dividend_daily_data, period)
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='none')
    # plt.figure(figsize=(10,6))
    sns.set(style="darkgrid")
    sns.barplot(data=chart_data.reset_index(), y='Income', x=period[:-2], color="white")
    ax.set_facecolor('none')  # Set the plot background to be transparent
    ax.grid(False)  # Remove the grid
    plt.xticks(color='white')  # Set x-axis labels to white
    plt.yticks(color='white')  # Set y-axis labels to white
    plt.xticks(rotation=45)
    # plt.xlabel('Date', color='white')  # Set x-axis title to white
    # plt.ylabel('Return', color='white')  # Set y-axis title to white
    plt.title(F'{period} Income', color='white')  # Set plot title to white

    return fig
    

def prepare_to_vizualize_secotrs_bar(portfolio_data):
    """
    Get the sector investments from the portfolio data
    """
    # portfolio_by_sectors_data = portfolio_data.groupby('sector').agg({'Amount Paid':'sum'})
    # portfolio_by_sectors_data.reset_index(inplace=True)
    # df_for_plot = portfolio_by_sectors_data.copy()
    # df_for_plot['Amount Paid'] = df_for_plot['Amount Paid'].apply(lambda x: round(x, 2))
    df_for_plot = portfolio_data.copy()
    # df_for_plot['Amount Paid'] = df_for_plot['Amount Paid'].apply(lambda  x: int(x.replace(',', '').replace('$', '')))
    df_for_plot['Percent'] = (df_for_plot['Amount Paid']/df_for_plot['Amount Paid'].sum()).apply(lambda x: round(x, 2))*100     
    df_for_plot = df_for_plot.sort_values('Percent', ascending=True)
    
    return df_for_plot
    
    
def vizualize_sectors_bar(portfolio_data):
    """
    Plot the bar chart by sectors
    """
    bar_data = prepare_to_vizualize_secotrs_bar(portfolio_data)
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='none')
    sns.set(style="darkgrid")
    sns.barplot(data=bar_data, x='Sector', y='Percent',  color="white")
    ax.set_facecolor('none')  # Set the plot background to be transparent
    ax.grid(False)  # Remove the grid
    plt.xticks(color='white')  # Set x-axis labels to white
    plt.yticks(color='white')  # Set y-axis labels to white
    plt.xticks(rotation=45)
    plt.xlabel('Sector', color='white')  # Set x-axis title to white
    plt.ylabel('Percent', color='white')  # Set y-axis title to white
    plt.title(F'Sectors Breakdown', color='white')  # Set plot title to white
    plt.tight_layout()
    
    return fig

def prepare_to_vizualize_cumsum_returns(portfolio_cumsum_returns, period):
    
    if period == 'Week':
        data = portfolio_cumsum_returns[-7:]
    elif period == 'Month':
        data = portfolio_cumsum_returns[-30:]
    elif period == '6 Month':
        data = portfolio_cumsum_returns[-30*6:]
    elif period == 'YTD':
        data = portfolio_cumsum_returns[portfolio_cumsum_returns['Date'].dt.year >= portfolio_cumsum_returns['Date'].dt.year.max()]
    elif period == '1 Year':
        data = portfolio_cumsum_returns[-365:]       
    elif period == '5 Years':
        data = portfolio_cumsum_returns[-365*5:]  
    elif period == 'All':
        data = portfolio_cumsum_returns  
    else:
        data = portfolio_cumsum_returns          

    return data

def vizualize_cumsum_returns(portfolio_cumsum_returns, period):
    chart_data = prepare_to_vizualize_cumsum_returns(portfolio_cumsum_returns, period)
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='none')
    sns.set(style="darkgrid")
    sns.lineplot(data=chart_data, y='Return', x='Date', color="white", ax=ax)
    ax.set_facecolor('none')  # Set the plot background to be transparent
    ax.grid(False)  # Remove the grid
    plt.xticks(color='white')  # Set x-axis labels to white
    plt.yticks(color='white')  # Set y-axis labels to white
    plt.xlabel('Date', color='white')  # Set x-axis title to white
    plt.ylabel('Return', color='white')  # Set y-axis title to white
    plt.title('Portfolio Returns', color='white')  # Set plot title to white
    

    return fig

def vizualize_portfilio_returns(portfolio_to_plot, period):
    
    chart_data = prepare_to_vizualize_cumsum_returns(portfolio_to_plot, period).copy()
    chart_data['Return'] = chart_data['Return'] - chart_data['Return'][0]
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='none')
    sns.set(style="darkgrid")
    sns.lineplot(data=chart_data, y='Return', x='Date', color="white", ax=ax)
    ax.set_facecolor('none')  # Set the plot background to be transparent
    ax.grid(False)  # Remove the grid
    plt.xticks(color='white')  # Set x-axis labels to white
    plt.yticks(color='white')  # Set y-axis labels to white
    plt.xlabel('Date', color='white')  # Set x-axis title to white
    plt.ylabel('Return', color='white')  # Set y-axis title to white
    return_num = str(round(100*(chart_data['Return'][-1]), 2)) + ' %'
    plt.title(f'{return_num} Return', color='white')  # Set plot title to white

    return fig

def visualize_historical_yield_on_cost(hist_yield_on_cost):
    
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='none')
    sns.set(style="darkgrid")
    sns.lineplot(data=hist_yield_on_cost, y='Yield On Cost', x='Date', color="white", ax=ax)
    ax.set_facecolor('none')  # Set the plot background to be transparent
    ax.grid(False)  # Remove the grid
    plt.xticks(color='white')  # Set x-axis labels to white
    plt.yticks(color='white')  # Set y-axis labels to white
    plt.xlabel('Date', color='white')  # Set x-axis title to white
    plt.ylabel('Yield On Cost', color='white')  # Set y-axis title to white
    plt.title('Yield On Cost', color='white')  # Set plot title to white

    return fig