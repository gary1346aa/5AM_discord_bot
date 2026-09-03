# 5AM Discord Guild Bot 🌅

A custom Discord bot tailored for the **5AM** guild, featuring automated member onboarding, voice activity logging, dual fortune-telling systems, equipment scrolling simulator, and dynamic toxic quotes management.

---

## 🚀 Active Features & Commands

- **🌅 Welcome & Farewell System**: Branded embed greeting cards showing member avatars, server rules shortcut, member count, and local join timestamp (UTC+8).
- **🔊 Voice Activity Logging**: Real-time logging of voice room joins, leaves, and channel switches.
- **🔨 Equipment Scrolling Simulator (衝卷模擬器)**:
  - `/衝卷`: **Artale 原汁原味裝備衝卷模擬**
    - `裝備名稱`: 自訂裝備（如：強化冥雷弩、炎魔頭盔、乾坤手套）
    - `卷軸類型`:
      - `📜 一般卷軸`: 失敗不爆裝
      - `💀 詛咒卷軸`: 失敗 50% 機率摧毀裝備
      - `⚪ 純白卷軸`: 失敗依自訂機率摧毀裝備
    - `卷軸機率`: 成功機率 % (如 10%, 15%, 30%, 60%, 65%, 70%, 100%, 1%, 3%, 5%)
    - `毀損機率`: 失敗時摧毀裝備之機率 % (詛咒卷固定 50%，純白卷可自訂)
    - **正宗遊戲提示文字**:
      - 成功：`卷軸閃爍了一下，神秘的力量傳到了{裝備名稱}身上。`
      - 失敗：`卷軸閃爍了一下，但{裝備名稱}沒有任何變化。`
      - 損毀：`受到卷軸的力量影響，{裝備名稱}被摧毀了。`
- **🔮 Dual Fortune Systems**:
  - `/每日運勢`: **經典星座色彩版** — 查看每日吉凶、今日短評、幸運色與貴人星座。
  - `/每日運勢2`: **Artale 冒險神諭版** — 專為打王冒險設計，包含今日神諭、今日宜/忌、貴人隊友、幸運地圖、掉寶預測與命運塔羅指引。
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
