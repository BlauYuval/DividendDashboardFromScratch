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
    