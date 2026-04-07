#!/usr/bin/env python3
"""
🔥 ICT LIQUIDITY SWEEP HEATMAP - SINGLE FILE TRADING TOOL
Copy → Paste → pip install -r requirements.txt → python this_file.py
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
import argparse
from dataclasses import dataclass
from scipy.ndimage import gaussian_filter1d
import sys

@dataclass
class LiquiditySweep:
    index: int
    timestamp: str
    price: float
    sweep_type: str
    strength: float
    confidence: float

class LiquiditySweepDetector:
    def __init__(self, df):
        self.df = df.copy()
        self._prepare_data()
    
    def _prepare_data(self):
        """Calculate ATR and swing points"""
        # ATR
        high_low = self.df['high'] - self.df['low']
        high_close = np.abs(self.df['high'] - self.df['close'].shift())
        low_close = np.abs(self.df['low'] - self.df['close'].shift())
        tr = np.maximum(high_low, np.maximum(high_close, low_close))
        self.df['atr'] = tr.rolling(14).mean()
        
        # Swing highs/lows
        length = 5
        self.df['swing_high'] = self.df['high'].rolling(window=length*2+1, center=True).apply(
            lambda x: x[length] == x.max() if len(x) == length*2+1 else False, raw=True
        ).fillna(False).astype(bool)
        
        self.df['swing_low'] = self.df['low'].rolling(window=length*2+1, center=True).apply(
            lambda x: x[length] == x.min() if len(x) == length*2+1 else False, raw=True
        ).fillna(False).astype(bool)
    
    def detect_sweeps(self):
        """Detect ICT liquidity sweeps"""
        sweeps = []
        
        for i in range(10, len(self.df)):
            atr = self.df['atr'].iloc[i]
            if pd.isna(atr):
                continue
            
            # BULLISH SWEEP: Price sweeps below swing low then reverses up
            if (self.df['swing_low'].iloc[i] and 
                self.df['low'].iloc[i] < self.df['swing_low'].iloc[i] * 0.9995 and
                self.df['close'].iloc[i] > self.df['open'].iloc[i]):
                
                strength = (self.df['swing_low'].iloc[i] - self.df['low'].iloc[i]) / atr
                confidence = min(0.95, strength * 0.5)
                sweeps.append(LiquiditySweep(
                    i, str(self.df.index[i]), self.df['low'].iloc[i], 
                    'bullish', strength, confidence
                ))
            
            # BEARISH SWEEP: Price sweeps above swing high then reverses down
            elif (self.df['swing_high'].iloc[i] and 
                  self.df['high'].iloc[i] > self.df['swing_high'].iloc[i] * 1.0005 and
                  self.df['close'].iloc[i] < self.df['open'].iloc[i]):
                
                strength = (self.df['high'].iloc[i] - self.df['swing_high'].iloc[i]) / atr
                confidence = min(0.95, strength * 0.5)
                sweeps.append(LiquiditySweep(
                    i, str(self.df.index[i]), self.df['high'].iloc[i], 
                    'bearish', strength, confidence
                ))
        
        return sorted(sweeps, key=lambda x: x.confidence, reverse=True)[:50]

class HeatmapGenerator:
    def __init__(self, df, sweeps):
        self.df = df
        self.sweeps = sweeps
        self.heatmap = np.zeros(len(df))
    
    def generate(self):
        """Generate liquidity heatmap"""
        for sweep in self.sweeps:
            start = max(0, sweep.index - 5)
            end = min(len(self.heatmap), sweep.index + 15)
            for i in range(start, end):
                dist = abs(i - sweep.index)
                weight = np.exp(-dist/4) * sweep.confidence
                self.heatmap[i] += weight
        
        # Smooth heatmap
        self.heatmap = gaussian_filter1d(self.heatmap, sigma=2)
        self.heatmap = np.clip(self.heatmap / np.max(self.heatmap + 1e-8), 0, 1)
        return self.heatmap

def fetch_data(symbol, timeframe="1h", days=60):
    """Fetch data from yfinance"""
    symbols = {
        'EURUSD': 'EURUSD=X', 'GBPUSD': 'GBPUSD=X', 'USDJPY': 'USDJPY=X',
        'BTCUSD': 'BTC-USD', 'ETHUSD': 'ETH-USD', 'BTC': 'BTC-USD',
        'SPX': '^GSPC', 'SPY': 'SPY', 'QQQ': 'QQQ'
    }
    
    ticker_symbol = symbols.get(symbol.upper(), symbol.upper())
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=f"{days}d", interval=timeframe)
        if df.empty:
            print(f"❌ No data for {symbol}")
            return None
        
        df.columns = [col.lower() for col in df.columns]
        print(f"✅ Loaded {len(df):,} bars for {symbol}")
        return df.sort_index()
    except:
        print(f"❌ Error fetching {symbol}")
        return None

def create_chart(df, sweeps, heatmap, symbol):
    """Create interactive Plotly chart"""
    fig = go.Figure()
    
    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'], 
        low=df['low'], close=df['close'], name="Price"
    ))
    
    # Heatmap overlay
    fig.add_trace(go.Scatter(
        x=df.index, y=df['low'] - (df['high']-df['low'])*0.1,
        mode='markers', marker=dict(
            size=25, color=heatmap, colorscale='RdYlGn', 
            opacity=0.7, colorbar=dict(title="Liquidity Heat", thickness=20)
        ),
        name="🔥 Liquidity Heatmap",
        hovertemplate="%{x|%H:%M}<br>Intensity: %{customdata:.1%}<extra></extra>",
        customdata=heatmap
    ))
    
    # Bullish sweeps
    bullish = [s for s in sweeps if s.sweep_type == 'bullish']
    if bullish:
        fig.add_trace(go.Scatter(
            x=[s.timestamp for s in bullish], y=[s.price for s in bullish],
            mode='markers+text', marker=dict(symbol='triangle-up', size=18, color='lime'),
            name='💚 Bullish Sweeps', text=['B' for _ in bullish],
            hovertemplate="💚 BULLISH SWEEP<br>Time: %{x}<br>Strength: %{customdata[0]:.2f}<br>Conf: %{customdata[1]:.1%}<extra>",
            customdata=[[s.strength, s.confidence] for s in bullish]
        ))
    
    # Bearish sweeps
    bearish = [s for s in sweeps if s.sweep_type == 'bearish']
    if bearish:
        fig.add_trace(go.Scatter(
            x=[s.timestamp for s in bearish], y=[s.price for s in bearish],
            mode='markers+text', marker=dict(symbol='triangle-down', size=18, color='red'),
            name='❤️ Bearish Sweeps', text=['S' for _ in bearish],
            hovertemplate="❤️ BEARISH SWEEP<br>Time: %{x}<br>Strength: %{customdata[0]:.2f}<br>Conf: %{customdata[1]:.1%}<extra>",
            customdata=[[s.strength, s.confidence] for s in bearish]
        ))
    
    # High confidence zones
    high_conf = np.where(heatmap > 0.7)[0]
    if len(high_conf) > 0:
        fig.add_hline(y=df['close'].iloc[high_conf[0]], line_dash="dot",
                     line_color="gold", annotation_text=f"🚨 HIGH LIQ ZONE")
    
    fig.update_layout(
        title=f"🔥 ICT LIQUIDITY SWEEP HEATMAP - {symbol}", 
        height=800, template='plotly_dark',
        yaxis_title="Price", xaxis_title="Time",
        showlegend=True
    )
    
    return fig

def main():
    parser = argparse.ArgumentParser(description="🔥 ICT Liquidity Sweep Heatmap")
    parser.add_argument("--symbol", default="BTCUSD", help="BTCUSD, SPY, EURUSD, QQQ")
    parser.add_argument("--timeframe", default="1h", help="1m,5m,15m,1h,4h,1d")
    parser.add_argument("--days", type=int, default=60, help="Days of data")
    parser.add_argument("--save", help="Save chart as PNG")
    
    args = parser.parse_args()
    
    print("🔥 ICT LIQUIDITY SWEEP DETECTOR")
    print("="*50)
    
    # Fetch data
    df = fetch_data(args.symbol, args.timeframe, args.days)
    if df is None or df.empty:
        print("❌ No data! Try: BTCUSD, SPY, QQQ, EURUSD")
        return
    
    # Detect sweeps
    detector = LiquiditySweepDetector(df)
    sweeps = detector.detect_sweeps()
    
    # Generate heatmap
    heatmap_gen = HeatmapGenerator(df, sweeps)
    heatmap = heatmap_gen.generate()
    
    # Create chart
    fig = create_chart(df, sweeps, heatmap, args.symbol)
    
    # Show or save
    if args.save:
        fig.write_image(args.save)
        print(f"💾 Chart saved: {args.save}")
    else:
        fig.show()
    
    # Results summary
    bullish = len([s for s in sweeps if s.sweep_type == 'bullish'])
    bearish = len([s for s in sweeps if s.sweep_type == 'bearish'])
    high_zones = np.sum(heatmap > 0.7)
    
    print("\n" + "="*50)
    print("📊 RESULTS SUMMARY")
    print(f"   💚 Bullish Sweeps:  {bullish}")
    print(f"   ❤️ Bearish Sweeps:  {bearish}")
    print(f"   🚨 High Liq Zones:  {high_zones}")
    print(f"   📈 Total Signals:   {len(sweeps)}")
    
    if sweeps:
        best = max(sweeps, key=lambda x: x.confidence)
        print(f"   ⭐ BEST SIGNAL: {best.sweep_type.upper()} (Conf: {best.confidence:.0%})")

if __name__ == "__main__":
    main()