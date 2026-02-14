#!/bin/bash
# MedLit AI — Launch Script

echo "🩺 MedLit AI Launcher"
echo "====================="
echo ""

# Check if config exists
if [ ! -f "config.json" ]; then
    echo "❌ Error: config.json not found!"
    echo "Copy config.example.json to config.json and add your API keys."
    exit 1
fi

# Create data directory if needed
mkdir -p data

case "$1" in
    "scrape")
        echo "📚 Fetching latest papers..."
        python scraper/fetch_papers.py
        ;;
    "summarize")
        echo "🤖 Generating summaries..."
        python summarizer/generate.py "${@:2}"
        ;;
    "bot")
        echo "🤖 Starting Telegram bot..."
        python bot/telegram_bot.py
        ;;
    "full")
        echo "📚 Fetching papers..."
        python scraper/fetch_papers.py
        echo ""
        echo "🤖 Generating summaries..."
        python summarizer/generate.py --limit 20
        echo ""
        echo "🤖 Starting bot..."
        python bot/telegram_bot.py
        ;;
    "db")
        echo "📊 Opening database..."
        sqlite3 data/medlit.db
        ;;
    *)
        echo "Usage: ./launch.sh [command]"
        echo ""
        echo "Commands:"
        echo "  scrape     - Fetch latest papers from journals"
        echo "  summarize  - Generate AI summaries for new papers"
        echo "  bot        - Start Telegram bot"
        echo "  full       - Run scrape + summarize + bot"
        echo "  db         - Open SQLite database"
        echo ""
        echo "Examples:"
        echo "  ./launch.sh scrape"
        echo "  ./launch.sh summarize --specialty cardiology --limit 10"
        echo "  ./launch.sh bot"
        ;;
esac
