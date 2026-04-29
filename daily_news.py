import os
import requests
from telegram import Bot
import asyncio
from datetime import datetime, timezone

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# High-impact keywords for extra importance
HIGH_IMPACT = ["breaking", "fed", "rate cut", "crash", "war", "conflict", "AI breakthrough", "Bitcoin ETF", "earnings beat", "merger", "acquisition"]

async def main():
    bot = Bot(token=TOKEN)
    
    topics = "US stock OR stocks OR SPY OR QQQ OR Bitcoin OR BTC OR Tech OR technology OR AI OR artificial intelligence OR Business OR Politics OR War OR Marketing"
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topics,
        "language": "en",
        "sortBy": "relevancy",      # ← Changed to most relevant first
        "pageSize": 20,             # Fetch more so we can score and pick the best
        "apiKey": NEWS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        articles = data.get("articles", [])
        
        if not articles:
            await bot.send_message(chat_id=CHAT_ID, text="📰 No major news found today.")
            return
        
        # === SCORING SYSTEM FOR IMPORTANCE ===
        scored = []
        now = datetime.now(timezone.utc)
        
        for article in articles:
            title = (article.get('title') or "").lower()
            desc = (article.get('description') or "").lower()
            published = article.get('publishedAt')
            
            # Base score from relevancy (NewsAPI already sorted)
            score = 10
            
            # Topic match bonus
            topic_matches = sum(1 for word in ["stock", "bitcoin", "btc", "ai", "tech", "business", "politics", "war", "marketing"] if word in title or word in desc)
            score += topic_matches * 8
            
            # High-impact keyword bonus
            impact_matches = sum(1 for word in HIGH_IMPACT if word in title or word in desc)
            score += impact_matches * 15
            
            # Recency bonus (very recent = higher score)
            if published:
                try:
                    pub_time = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    hours_old = (now - pub_time).total_seconds() / 3600
                    if hours_old < 6:
                        score += 20
                    elif hours_old < 12:
                        score += 10
                except:
                    pass
            
            scored.append((score, article))
        
        # Sort by score (highest first) and take only top 2
        scored.sort(reverse=True, key=lambda x: x[0])
        top_two = [art for _, art in scored[:2]]
        
        # Send the 2 most important news as separate messages
        for i, article in enumerate(top_two, 1):
            title = article['title']
            description = article.get('description') or "No description available."
            url_link = article['url']
            source = article['source']['name']
            time = datetime.now().strftime("%b %d, %I:%M %p UTC")
            
            message = f"""📰 **Top Important News #{i}** ({time})

**{title}**
{description[:200]}...

📌 Source: {source}
🔗 {url_link}"""
            
            await bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            await asyncio.sleep(2)  # small pause between posts
        
        print(f"✅ Sent 2 most important news items")
        
    except Exception as e:
        print(f"Error: {e}")
        await bot.send_message(chat_id=CHAT_ID, text="⚠️ Could not fetch news today.")

if __name__ == "__main__":
    asyncio.run(main())
