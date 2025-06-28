
# strategy.py – V20 logic (now mocks yfinance for environments where it's unavailable)

import pandas as pd
from datetime import datetime, timedelta

THRESHOLD_PERCENT = 20
START_DATE = (datetime.today() - timedelta(days=3*365)).strftime('%Y-%m-%d')
END_DATE = datetime.today().strftime('%Y-%m-%d')

all_stocks = [
    "RELIANCE", "INFY", "ITC"  # Trimmed for testing/demo purposes
]

# Mock download function to simulate yfinance behavior in unsupported environments
def download_data(symbol: str) -> pd.DataFrame | None:
    try:
        # Generate 1000 days of fake price data
        dates = pd.date_range(start=START_DATE, end=END_DATE)
        prices = pd.Series(100 + (pd.Series(range(len(dates))) % 10).cumsum(), index=dates)
        df = pd.DataFrame({
            'Open': prices * 0.98,
            'High': prices * 1.02,
            'Low': prices * 0.97,
            'Close': prices
        })
        df['MA200'] = df['Close'].rolling(window=200).mean()
        return df
    except Exception:
        return None

def find_v20_signals(df: pd.DataFrame):
    signals = []
    latest_close = df['Close'].iloc[-1]
    streak_low = streak_high = None

    for idx in range(1, len(df)):
        cur = df.iloc[idx]
        if cur['Close'] > cur['Open']:
            streak_low  = cur['Low'] if streak_low is None else min(streak_low, cur['Low'])
            streak_high = cur['High'] if streak_high is None else max(streak_high, cur['High'])
            continue

        if streak_low and streak_high:
            pct_move = (streak_high - streak_low) / streak_low * 100
            if pct_move >= THRESHOLD_PERCENT and streak_low < cur.get('MA200', float('inf')):
                proximity = abs(latest_close - streak_low) / streak_low * 100
                signals.append((df.index[idx].date(), round(streak_low, 2),
                                round(streak_high, 2), round(pct_move, 2),
                                round(latest_close, 2), round(proximity, 2)))
        streak_low = streak_high = None
    return signals

def run_strategy():
    signals = []
    for sym in all_stocks:
        df = download_data(sym)
        if df is None:
            continue
        for sig in find_v20_signals(df):
            sig_date, buy, sell, pct, close, prox = sig
            signals.append({
                'SignalDate': sig_date, 'Symbol': sym,
                'BuyAt': buy, 'SellAt': sell, '%Move': pct,
                'Close': close, 'Proximity%': prox
            })

    if not signals:
        return pd.DataFrame()

    df_out = pd.DataFrame(signals)
    df_out.sort_values(by=['SignalDate', 'Proximity%'], ascending=[False, True], inplace=True)
    return df_out
