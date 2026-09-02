# 5AM Discord Guild Bot 🌅

A custom Discord bot tailored for the **5AM** guild, featuring automated member onboarding, voice activity logging, daily fortune/fun commands, and a complete chat & voice leveling system.

---

## 🚀 Features

- **🌅 Welcome & Farewell System**: Branded embed greeting cards showing member avatars, server rules shortcut, member count, and local join timestamp (UTC+8).
- **🔊 Voice Activity Logging**: Real-time logging of voice room joins, leaves, and channel switches.
- **🔮 Daily Fortune & Entertainment**:
  - /每日運勢: Daily fortune-telling with daily cooldown lock, lucky color, noble constellation, and custom commentary.
  - /toxic: Demotivational toxic quote generator with toxicity rating.
- **📊 Activity Leveling & Leaderboard**:
  - **Chat XP**: 15–25 XP per message (60s cooldown).
  - **Voice XP**: 10 XP/minute based on active voice time.
  - /等級: Personal rank card with visual progress bar (▰▰▱▱).
  - /排行榜: Server Top 30 leaderboard categorised into *Hall of Fame (1–10)*, *Backbone (11–20)*, and *Close Behind (21–30)*.
  - **Admin Commands**: /加權升等, /天災降等, and /重置賽季 (monthly leaderboard reset with Top 10 honor board broadcast).
- **🛠️ Testing & Simulation Commands**:
  - /sim_welcome, /sim_farewell, /sim_voice, /sim_fortune, /ping.

---

## 📦 Installation & Setup

### 1. Clone the Repository
`ash
git clone https://github.com/gary1346aa/5AM_discord_bot.git
cd 5AM_discord_bot
`

### 2. Install Dependencies
`ash
pip install -r requirements.txt
`

### 3. Configure Environment Variables
Copy .env.example to .env and fill in your bot token and server channel IDs:
`ash
cp .env.example .env
`

`env
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_guild_id_here
WELCOME_CHANNEL_ID=your_welcome_channel_id
VOICE_LOG_CHANNEL_ID=your_voice_log_channel_id
QUOTE_CHANNEL_ID=your_quote_channel_id
LEVEL_CHANNEL_ID=your_level_channel_id
RULES_CHANNEL_ID=your_rules_channel_id
`

### 4. Run the Bot
`ash
python bot.py
`

---

## ⚙️ Required Discord Bot Privileged Intents
Ensure the following **Privileged Gateway Intents** are enabled in the [Discord Developer Portal](https://discord.com/developers/applications):
- **Server Members Intent** (intents.members = True)
- **Message Content Intent** (intents.message_content = True)
- **Voice State Intent** (intents.voice_states = True)
