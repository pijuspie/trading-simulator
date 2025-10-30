import yfinance as yf
import matplotlib.pyplot as plt

# --- 1. Download hourly data for the last 5 days
symbol = "AAPL"
data = yf.download(symbol, period="5d", interval="5m", auto_adjust=True)

# --- 2. Convert to New York time (market local time)
data.index = data.index.tz_convert('America/New_York')

# --- Create a sequential x-axis (no gaps for closed market)
x = range(len(data))  # 0, 1, 2, ..., n
y = data["Close"]

plt.figure(figsize=(10,5))
plt.plot(x, y, color="royalblue")
plt.title(f"{symbol} Hourly Price (Market Hours Only)")
plt.ylabel("Price (USD)")
plt.xlabel("Trading Hours (Sequential)")
plt.grid(True)

# Optionally, show one label per day
xticks = data.index.strftime("%m-%d %H:%M")
plt.xticks(x[::12], xticks[::12], rotation=90)  # show every ~12th hour label
plt.tight_layout()
plt.show()
