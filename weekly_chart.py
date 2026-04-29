import os
import yfinance as yf
import mplfinance as mpf
from telegram import Bot
import asyncio
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def main():
    bot = Bot(token=TOKEN)
    
    # === YOUR TICKERS (customize as you like) ===
    tickers = ["SPY", "QQQ", "BTC-USD", "AAPL", "NVDA", "TSLA"]
    
    await bot.send_message(
        chat_id=CHAT_ID,
        text=f"📈 **Weekly Market Charts** — {datetime.now().strftime('%B %d, %Y')}\nGenerating high-quality charts..."
    )
    
    for ticker in tickers:
        try:
            # Download 3 months of data
            data = yf.download(ticker, period="3mo", interval="1d", progress=False)
            
            if data.empty:
                continue
                
            # High-quality chart
            mpf.plot(data, type='candle', style='charles',
                     title=f"{ticker} — 3 Month Weekly Update",
                     volume=True,
                     mav=(20, 50),          # 20 & 50-day moving averages
                     savefig=f'{ticker}_weekly.png',
                     dpi=300,               # Sharp quality
                     figsize=(12, 8))
            
            # Send the chart
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=open(f'{ticker}_weekly.png', 'rb'),
                caption=f"📊 {ticker} Weekly Chart\n{data.index[-1].date()}"
            )
            
            print(f"✅ Sent chart for {ticker}")
            
        except Exception as e:
            print(f"Error with {ticker}: {e}")
            await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Could not generate chart for {ticker}")
    
    await bot.send_message(chat_id=CHAT_ID, text="✅ Weekly charts completed!")

if __name__ == "__main__":
    asyncio.run(main())
