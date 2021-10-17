from re import match
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Function to caculate the high band
def DchannelUpper(i, array_high, d_periods = 20):
    x = float(0.0)
    if(i < d_periods):
        for j in range(i, -1, -1):
            x = max(array_high[j], x)
    else:
        for j in range(i, i-d_periods, -1):
            x = max(array_high[j], x)
    return x

# Function to caculate the low band
def DchannelLower(i, array_low, d_periods = 20):
    x = float("inf")
    if(i < d_periods):
        for j in range(i, -1, -1):
            x = min(array_low[j], x)
    else:
        for j in range(i, i-d_periods, -1):
            x = min(array_low[j], x)
    return x


def download_and_prep_stock(symbol):
    stck = yf.Ticker(symbol)

    base_info = None

    try:
        base_info = stck.info
    except:
        return (pd.DataFrame(), pd.DataFrame())

    hist = stck.history(period="1y", interval="1d")

    hist = hist.reset_index()
    # hist.reindex(index = hist.index[::-1])

    for i in ['Open', 'High', 'Close', 'Low']:
        hist[i] = hist[i].astype('float64')

    # print(hist.head())

    candle_trace = go.Candlestick(x = hist['Date'], open = hist['Open'], high = hist['High'], low= hist['Low'], close = hist['Close'])

    # Calc high band
    array_upper = []
    for i in range(0, hist['High'].size):
        array_upper.append(DchannelUpper(i, hist['High'], 30))

    array_upper.insert(0, None)
    array_upper.pop()

    # Calc low band
    array_lower = []
    for i in range(0, hist['Low'].size):
        array_lower.append(DchannelLower(i, hist['Low'], 30))

    array_lower_non_adjusted = array_lower.copy()

    array_lower.insert(0, None)
    array_lower.pop()

    hist['upper_dc_band'] = array_upper
    hist['lower_dc_band'] = array_lower
    hist['lower_adjusted_dc_band'] = array_lower_non_adjusted

    return (hist, candle_trace)

def plot(hist, candle_trace):
  fig = go.Figure(data = candle_trace)
  fig.add_scatter(x=hist['Date'], y=hist['upper_dc_band'], mode='lines', marker_color='green')
  fig.add_scatter(x=hist['Date'], y=hist['lower_dc_band'], mode='lines', marker_color='red')
  fig.add_scatter(x=hist['Date'], y=hist['lower_adjusted_dc_band'], mode='lines', marker_color='gray')
  #fig.add_trace(lower_dc_trace)
  #fig.add_trace(adjusted_dc_trace)

  fig.show()

def should_buy(hist):
    current_max = hist['High'][len(hist['High']) - 1]
    current_resistance = hist['upper_dc_band'][len(hist['upper_dc_band']) - 1]
    current_support = hist['lower_dc_band'][len(hist['lower_dc_band']) - 1]

    if current_max is None or current_resistance is None or current_support is None:
        return None

    margin = (current_resistance - current_support) * 0.85

    #print("Current max: " + str(current_max))
    #print("Current resistance: " + str(current_resistance))
    #print("Current resistance with margin: " + str((current_support + margin)))

    # if current_max >= current_resistance:
    #     #print("Buy it now!!!")
    #     return "Grade 2 - Should buy it now!"
    if current_max >= (current_support + margin):
        #print("Maybe late but suggestion: Put a start order for R$" + str(current_resistance))

        idx_loop = 6
        while idx_loop < len(hist['High']):
            c_max = hist['High'][len(hist['High']) - idx_loop]
            c_low = hist['Low'][len(hist['Low']) - idx_loop]
            c_res = hist['upper_dc_band'][len(hist['upper_dc_band']) - idx_loop]
            c_sup = hist['lower_dc_band'][len(hist['lower_dc_band']) - idx_loop]        

            # Had previously broke resistance
            if c_max >= c_res:
                return "Grade 2 - Maybe late but suggestion: Put a start order for R$" + str(current_resistance)

            # Had previously broken support
            if c_low <= c_sup:
                # Currently on a resistance break
                if current_max >= current_resistance:
                    return "Grade 4 - Ideal graph situation NOW: Buy today!"
                
                return "Grade 3 - Almost ideal graph situation: Put a start order for R$" + str(current_resistance)

            # print(current_max)
            idx_loop += 1

        return "(WARNING - NOT ENOUGH DATA) But, maybe late but suggestion: Put a start order for R$" + str(current_resistance)
    else:
        #print("Not the time to buy it!")
        return None

file_source_name = "symbols_watchlist.txt"
with open(file_source_name, "r") as watchlist:
    num_lines = sum(1 for line in open(file_source_name))

    for idx, line in enumerate(watchlist.readlines()):
        smbol = line.strip()
        hist, candle_trace = download_and_prep_stock(smbol)

        if hist.empty:
            print("Stock not found")
            percentage_researched = (idx / num_lines) * 100
            print("Completed: " + str(int(percentage_researched)) + "%")
            
            continue

        # plot(hist, candle_trace)
        s_buy_msg = should_buy(hist)

        f_result = open("results.txt", "a")

        if s_buy_msg != None:
            f_result.write(smbol + ": " + s_buy_msg + "\n")

        f_result.close()

        percentage_researched = (idx / num_lines) * 100
        print("Completed: " + str(int(percentage_researched)) + "%")

