# 5AM Discord Guild Bot 🌅

A custom Discord bot tailored for the **5AM** guild, featuring automated member onboarding, voice activity logging, dual fortune-telling systems, and dynamic toxic quotes management.

---

## 🚀 Active Features & Commands

- **🌅 Welcome & Farewell System**: Branded embed greeting cards showing member avatars, server rules shortcut, member count, and local join timestamp (UTC+8).
- **🔊 Voice Activity Logging**: Real-time logging of voice room joins, leaves, and channel switches.
- **🔮 Dual Fortune Systems**:
  - `/每日運勢`: **經典星座色彩版** — 查看每日吉凶、今日短評、幸運色與貴人星座。
  - `/每日運勢2`: **Artale 冒險神諭版** — 專為打王冒險設計，包含：
    - 📜 今日神諭
    - ⭕ 今日【宜】*(如：墊卷衝裝大成功、準時上車打龍王分寶)*
    - ❌ 今日【忌】*(如：頭鐵狂點30%詛咒卷、王死噴寶瞬間斷線)*
    - 🤝 貴人隊友 *(12 職業特色稱號)*
    - 🗺️ 幸運地圖 *(炎魔祭壇、龍王洞穴、海怒斯洞窟等)*
    - 💎 掉寶預測 *(日鏢、月鏢、雷鏢、炎盔、龍王項鍊、詛咒卷等)*
    - 🎴 命運塔羅指引
- **🥣 Toxic Quotes System**:
  - `/每日毒湯`: 隨機領取一碗心靈毒雞湯 (普通毒湯 / 劇毒砒霜)。
  - `/新增毒湯`: 管理員自訂新增毒雞湯至語錄庫。

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/gary1346aa/5AM_discord_bot.git
cd 5AM_discord_bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your bot token and server channel IDs:
```bash
cp .env.example .env
```

```env
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=1375419109323440169
WELCOME_CHANNEL_ID=your_welcome_channel_id
VOICE_LOG_CHANNEL_ID=your_voice_log_channel_id
QUOTE_CHANNEL_ID=your_quote_channel_id
LEVEL_CHANNEL_ID=your_level_channel_id
RULES_CHANNEL_ID=your_rules_channel_id
```

### 4. Run the Bot
```bash
python bot.py
```
