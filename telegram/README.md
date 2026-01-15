# Signal Genius AI - Telegram Bot

Professional Telegram bot that sends high-confidence EUR/USD trading signals.

## Features

- ✅ Sends 1 signal per day per asset
- ✅ Only signals with confidence ≥ 95%
- ✅ Checks API every 15 minutes
- ✅ Uses exact signal template format
- ✅ Prevents duplicate signals

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file or set these variables:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
API_ENDPOINT=http://localhost:8000/api/v1/lab/market-reference
```

### 3. Get Telegram Bot Token

1. Talk to [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the token

### 4. Get Chat ID

**For personal chat:**
1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find your chat ID in the response

**For group chat:**
1. Add bot to your group
2. Send a message in the group
3. Visit the same URL above
4. Look for "chat":{"id":-XXXXXXXXX}

### 5. Run the Bot

```bash
python bot.py
```

## Deployment

### Railway

1. Create new project on Railway
2. Add environment variables
3. Deploy from GitHub

### Fly.io

```bash
fly launch
fly secrets set TELEGRAM_BOT_TOKEN=xxx TELEGRAM_CHAT_ID=xxx
fly deploy
```

## Signal Rules

- **Frequency**: Maximum 1 signal per asset per day
- **Confidence**: Only sends when AI confidence ≥ 95%
- **Check Interval**: Every 15 minutes
- **Format**: Plain text (no markdown)
- **Auto-Expiry**: Signals expire at NY close or when TP/SL hit

## Monitoring

The bot logs all activities:
- ✅ Signal sent successfully
- ⚠️ Low confidence (< 95%)
- ⚠️ Already sent today
- ❌ API errors
- ❌ Telegram errors

## Testing

Test the bot locally before deploying:

```bash
# Set test environment
export API_ENDPOINT=http://localhost:8000/api/v1/lab/market-reference
export TELEGRAM_BOT_TOKEN=your_token
export TELEGRAM_CHAT_ID=your_chat_id

# Run bot
python bot.py
```

## Troubleshooting

**Bot not sending messages:**
- Check bot token is correct
- Verify chat ID is correct
- Ensure bot has permission to send messages
- Check API endpoint is accessible

**Duplicate signals:**
- Bot tracks sent signals per day
- Resets at midnight UTC
- Uses asset + direction + date as unique ID

**API connection issues:**
- Verify API endpoint URL
- Check network connectivity
- Review API logs for errors

## License

© 2026 Signal Genius AI. All rights reserved.
