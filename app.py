# TODO - FIX HEADLINES NAMES
# TODO - ADD BUTTONS TO PORTFOLIO RETURNS
# TODO - ADD DIVIDEND YIELD COLUMN TO GROWTH TABLE


import os
import ast
import redis
import matplotlib
import pandas as pd
import seaborn as sns
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from flask_basicauth import BasicAuth
from flask import Flask, render_template, jsonify, url_for 

from income import Income
from executive_summery import ExecutiveSummery
from visualization import vizualize_income_bar, vizualize_sectors_bar, vizualize_cumsum_returns, visualize_historical_yield_on_cost

app = Flask(__name__)

# Basic Auth Configuration
app.config['BASIC_AUTH_USERNAME'] = 'yourusername'
app.config['BASIC_AUTH_PASSWORD'] = 'yourpassword'
basic_auth = BasicAuth(app)

def color_cagr(val, row):
    cagr_10 = row['Cagr 10y']
    cagr_5 = row['Cagr 5y']
    cagr_3 = row['Cagr 3y']
    cagr_1 = row['Cagr 1y']
    cagr_hold = val
    
    if cagr_hold > cagr_10 and cagr_hold > cagr_5 and cagr_hold > cagr_3 and cagr_hold > cagr_1:
        color = 'color:forestgreen'
    elif cagr_hold < cagr_10 and cagr_hold < cagr_5 and cagr_hold < cagr_3 and cagr_hold < cagr_1 and cagr_hold > -1:
        color = 'color:salmon'
    elif cagr_hold < 0:
        color = 'color:white'
    else:
        color = 'color:lawngreen'
    return color

@app.route('/')
@basic_auth.required
def index():
    # Load environment variables from .env file
    load_dotenv()

    # Initialize Redis connection
    redis_host = os.getenv('REDIS_HOST')
    redis_port = int(os.getenv('REDIS_PORT'))
    redis_password = os.getenv('REDIS_PASSWORD')

    r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    # Fetch data from Redis
    transaction_data_json = r.get('transaction_data')
    portfolio_to_plot_json = r.get('portfolio_to_plot')
    portfolio_table_json = r.get('portfolio_table')
    portfolio_cumsum_returns = r.get('portfolio_cumsum_returns')
    dividends_data_json = r.get('dividends_data')
    growth_data_json = r.get('growth_table')
    hist_yield_on_cost_json = r.get('hist_yield_on_cost')

    transaction_data = pd.DataFrame(ast.literal_eval(transaction_data_json.decode('utf-8')))
    transaction_data['date'] = pd.to_datetime(transaction_data['date'], unit='ms')
    transaction_data['start_payment_date'] = pd.to_datetime(transaction_data['start_payment_date'], unit='ms')
    portfolio_table = pd.DataFrame(ast.literal_eval(portfolio_table_json.decode('utf-8')))
    portfolio_to_plot = pd.DataFrame(ast.literal_eval(portfolio_to_plot_json.decode('utf-8')))
    portfolio_to_plot['Date'] = pd.to_datetime(portfolio_to_plot['Date'], unit='ms')
    portfolio_cumsum_returns = pd.DataFrame.from_dict(ast.literal_eval(portfolio_cumsum_returns.decode('utf-8')), orient='index')
    portfolio_cumsum_returns = portfolio_cumsum_returns.reset_index()
    portfolio_cumsum_returns.columns = ['Date', 'Return']
    portfolio_cumsum_returns['Date'] = pd.to_datetime(portfolio_cumsum_returns['Date'], unit='ms')
    dividends_data = pd.DataFrame(ast.literal_eval(dividends_data_json.decode('utf-8')))
    income = Income(transaction_data, dividends_data)
    monthly_income, yearly_income = income.run()
    growth_data_str = growth_data_json.decode('utf-8')
    growth_data_str = growth_data_str.replace('null', "-1")
    growth_data = pd.DataFrame(ast.literal_eval(growth_data_str))
    growth_data['start_payment_date'] = pd.to_datetime(growth_data['start_payment_date'], unit='ms')
    growth_data.columns = [" ".join([part.capitalize() for part in col.split('_')]) for col in growth_data.columns]
    hist_yield_on_cost = pd.DataFrame(ast.literal_eval(hist_yield_on_cost_json.decode('utf-8'))).reset_index()
    hist_yield_on_cost['Date'] = pd.to_datetime(hist_yield_on_cost['index'], unit='ms')
    hist_yield_on_cost = hist_yield_on_cost.rename(columns={'yield_on_cost': 'Yield On Cost'})
    
    # Display
    ## Executive Summary
    summery = ExecutiveSummery(portfolio_table)
    total_return, amount_invested, return_yield = summery.get_total_return()
    dividend_yield, yield_on_cost = summery.get_dividend_yield(total_return, amount_invested, yearly_income)
    average_dividend_growth = summery.get_average_dividend_growth(growth_data)

    total_return = f"${int(total_return):,}"
    return_yield = f"{round(return_yield, 2)}%"
    yield_on_cost = f"{round(yield_on_cost, 2)}%"
    average_dividend_growth = f"{round(average_dividend_growth, 2)}%"
    
    plt.figure(figsize=(10, 6), facecolor='none')
    sns.set(style="darkgrid")
    ax = sns.lineplot(data=portfolio_to_plot.reset_index(), y='Return', x='Date', color="white")
    ax.set_facecolor('none')  # Set the plot background to be transparent
    ax.grid(False)  # Remove the grid
    plt.xticks(color='white')  # Set x-axis labels to white
    plt.yticks(color='white')  # Set y-axis labels to white
    plt.xlabel('Date', color='white')  # Set x-axis title to white
    plt.ylabel('Return', color='white')  # Set y-axis title to white
    plt.title('Portfolio Returns', color='white')  # Set plot title to white
    plt.savefig('static/plot.png')
    plt.close()
    
    # Plot Cumsum returns
    for period in ['Week', 'Month', '6 Month', 'YTD', '1 Year', '5 Year', 'All']:
        cumsum_plot = vizualize_cumsum_returns(portfolio_cumsum_returns, period)
        period_lower = period.lower().replace(' ', '_')
        name = f'static/portfolio_cumsum_returns_{period_lower}.png'
        plt.savefig(name)
        plt.close(cumsum_plot)
        

    # Generate sectors bar plot
    sector_bar = vizualize_sectors_bar(portfolio_table)
    sector_bar.savefig('static/sectors_bar_plot.png')
    plt.close(sector_bar.figure)

    table_html = portfolio_table.to_html(classes='dataframe', border=2)

    # Format monthly and yearly income
    monthly_income = f"${int(monthly_income):,}"
    yearly_income = f"${int(yearly_income):,}"
    
    # Generate bar plots for all periods
    bar_plot_m = vizualize_income_bar(income.dividend_daily_data, 'Monthly')
    bar_plot_m.savefig('static/bar_plot_monthly.png')
    plt.close(bar_plot_m.figure)

    bar_plot_q = vizualize_income_bar(income.dividend_daily_data, 'Quaterly')
    bar_plot_q.savefig('static/bar_plot_quaterly.png')
    plt.close(bar_plot_q.figure)

    bar_plot_y = vizualize_income_bar(income.dividend_daily_data, 'Yearly')
    bar_plot_y.savefig('static/bar_plot_yearly.png')
    plt.close(bar_plot_y.figure)

    # Yield pn cost
    yield_line = visualize_historical_yield_on_cost(hist_yield_on_cost)
    yield_line.savefig('static/yield_line.png')
    plt.close(yield_line.figure)

    
    # Apply conditional formatting to growth_data
    growth_data_styled = growth_data.style.applymap(
        lambda x: color_cagr(x, growth_data.loc[growth_data.index[growth_data['Cagr since holding'] == x].tolist()[0]]),
        subset=['Cagr since holding']
    )
    growth_table_html = growth_data_styled.format(precision=2).set_table_attributes('id="growth-table" class="dataframe"').to_html()

    return render_template('index.html', 
                            table=table_html, 
                            growth_table=growth_table_html, 
                            monthly_income=monthly_income, 
                            yearly_income=yearly_income,
                            total_return=total_return,
                            return_yield=return_yield,
                            yield_on_cost=yield_on_cost,
                            average_dividend_growth=average_dividend_growth)


@app.route('/update_plot/<period>')
@basic_auth.required
def update_plot(period):
    plot_filename = f'static/bar_plot_{period}.png'
    return jsonify({'plot_url': plot_filename})

@app.route('/update_cumsum_plot/<period>')
@basic_auth.required
def update_cumsum_plot(period):
    plot_filename = f'portfolio_cumsum_returns_{period}.png'
    return jsonify({'plot_url': url_for('static', filename=plot_filename)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
