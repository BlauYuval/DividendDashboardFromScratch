import os
import ast
import redis
import matplotlib
import pandas as pd
import seaborn as sns
matplotlib.use('Agg')  # Use the 'Agg' backend for Matplotlib
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_basicauth import BasicAuth

app = Flask(__name__)

# Basic Auth Configuration
app.config['BASIC_AUTH_USERNAME'] = 'yourusername'
app.config['BASIC_AUTH_PASSWORD'] = 'yourpassword'
basic_auth = BasicAuth(app)

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
    portfolio_to_plot_json = r.get('portfolio_to_plot')
    portfolio_table_json = r.get('portfolio_table')   
    
    portfolio_table = pd.DataFrame(ast.literal_eval(portfolio_table_json.decode('utf-8')))
    portfolio_to_plot = pd.DataFrame(ast.literal_eval(portfolio_to_plot_json.decode('utf-8')))
    portfolio_to_plot['Date'] = pd.to_datetime(portfolio_to_plot['Date'], unit='ms')
    
    plt.figure(figsize=(10,6), facecolor='none')
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
    
    table_html = portfolio_table.to_html(classes='dataframe', border=2)

    return render_template('index.html', table=table_html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
