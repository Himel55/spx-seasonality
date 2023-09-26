#import libraries
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
from argparse import ArgumentParser

# Handle command line args
parser = ArgumentParser(description='Generate a heatmap graph of average daily returns % going back to 1980', epilog="Created by @MMTmacrotrader")
parser.add_argument('-t','--ticker', metavar='AAPL', default='^GSPC', help='Enter the ticker name from yahoo - https://finance.yahoo.com/lookup ')
args = parser.parse_args()
ticker = args.ticker

# Download SPX data from 1980 to the present using yfinance
# To change index, change the ticker symbol, visit https://finance.yahoo.com/lookup for tickers.
data = yf.download(ticker, start='1980-01-01')

# Calculate the daily percent return
data['Return'] = data['Adj Close'].pct_change()

# Create columns for month and day to facilitate aggregation
data['Month'] = data.index.month
data['Day'] = data.index.day

# Group by Month and Day and calculate the mean return
average_returns = data.groupby(['Month', 'Day'])['Return'].mean().reset_index()

# Pivot the dataframe for heatmaspx-seasonality-heatmap.pyp
heatmap_data = average_returns.pivot(index="Day", columns="Month", values="Return")

# Set month names for better clarity
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
heatmap_data.columns = months

plt.figure(figsize=(12,12))
heatmap = sns.heatmap(heatmap_data, cmap='RdYlGn', annot=True, fmt=".2%", cbar=False)
plt.title(f'Average Daily Returns for {ticker} (1980-Present) @MMTmacrotrader')

# Calculate the 10-day return for each date relative to the date 10 days prior
data['10-Day Return'] = data['Adj Close'] / data['Adj Close'].shift(10) - 1

# Group by Month and Day and calculate the mean of the 10-day returns
average_ten_day_returns = data.groupby(['Month', 'Day'])['10-Day Return'].mean().reset_index()

# Pivot the dataframe for heatmap
heatmap_ten_day_data = average_ten_day_returns.pivot(index="Day", columns="Month", values="10-Day Return")

# Set month names for better clarity
heatmap_ten_day_data .columns = months

plt.figure(figsize=(12, 12))
sns.heatmap(heatmap_ten_day_data , cmap='RdYlGn', annot=True, fmt=".2%", cbar=False)
plt.title(f'Average of 10-Day Returns for {ticker} (1980-Present) @MMTmacrotrader')

# Convert the Month number to its corresponding name for better readability
average_returns['Month'] = average_returns['Month'].apply(lambda x: months[x-1])

# Pivot the dataframe for display
display_df = average_returns.pivot(index="Day", columns="Month", values="Return")

#Create a simulated yearly balance based on average daily returns
def simulate_yearly_balance(df, starting_balance=100000):
    """Simulates the yearly balance given a DataFrame of average daily returns."""
    balances = [starting_balance]  # Start with the initial balance
    dates = ["Jan 1"]  # Start with the initial date

    # Iterate over each average return and calculate the daily balance
    for month in months:
        for day in range(1, 32):
            # Some days like Feb 29 might not exist in certain months or the average_returns df
            if (month, day) in df.index:
                daily_return = df.loc[(month, day), 'Return']
                new_balance = balances[-1] + (balances[-1] * daily_return)
                balances.append(new_balance)
                
                # Add the month-day to the dates list
                dates.append(f"{month} {day}")

    return balances, dates

# Prepare the data for simulation by setting month and day as index
prepared_df = average_returns.set_index(['Month', 'Day'])

# Calculate the simulated balances and associated dates
balances, dates = simulate_yearly_balance(prepared_df)

# Convert balances to percentage change from the starting balance
percentage_changes = [(bal - 100000) / 100000 * 100 for bal in balances]

# Plot the simulated account balance trajectory in percentage
plt.figure(figsize=(14, 8))
plt.plot(dates, percentage_changes, label='SPX Returns (%)', color='blue', linewidth=2)
plt.title(f'{ticker} % Change Over a Year Using Average Daily Returns (1980-Present) @MMTmacrotrader')
plt.xlabel('Date (Month-Day)')
plt.ylabel('% change')
plt.xticks(dates[::15], rotation=45)  # Display every 15th date for better legibility
plt.legend()
plt.grid(True)
plt.tight_layout()  # Adjust layout for better appearance
plt.show()
