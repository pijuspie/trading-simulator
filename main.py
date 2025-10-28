import yfinance as yf
import matplotlib.pyplot as plt

# Choose your stock symbol
symbol = "GOOG"

# Fetch 5 days of 30-minute interval data
data = yf.download(symbol, period="5d", interval="30m")

# Print first few rows
print(data.head())

# Plot close prices
plt.figure(figsize=(12,6))
plt.plot(data.index, data["Close"], label=f"{symbol} Close", color="blue")
plt.title(f"{symbol} Stock Prices (30-min intervals)")
plt.xlabel("Date/Time")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
