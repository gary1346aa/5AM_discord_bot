import sqlite3
import datetime
import random

DB_FILE = "5am_bot.db"

DEFAULT_TOXIC_QUOTES = [
    ("有些人出生就在終點，而你還在找停車位。", "⭐ 普通毒湯"),
    ("有夢想很好，但現實通常不配合。", "⭐ 普通毒湯"),
    ("你不努力一下，怎麼知道自己真的不行？", "⭐ 普通毒湯"),
    ("努力不一定會成功，但放棄一定很舒服。", "💀 劇毒砒霜"),
    ("世上無難事，只要肯放棄。", "💀 劇毒砒霜"),
    ("上帝為你關了一扇門，順便把窗戶也焊死了。", "💀 劇毒砒霜"),
    ("雖然你長得醜，但你想得美啊。", "⭐ 普通毒湯"),
    ("今天解決不了的事，別著急，明天也一樣解決不了。", "💀 劇毒砒霜"),
    ("世上只有一種英雄主義，那就是認清生活真相後依然擺擺爛。", "⭐ 普通毒湯"),
    ("你不是一無所有，你不是還有病嗎？", "💀 劇毒砒霜")
]

# --- FORTUNE 2 (ARTALE 冒險者專屬神諭與塔羅數據) ---

FORTUNE2_TIERS = ["🌟 大吉", "✨ 中吉", "🍀 小吉", "💦 凶", "😱 大凶"]

ORACLE_MESSAGES = [
    "神清氣爽！阿泰爾的 GM 今天特別眷顧你！",
    "運勢平順，只要穩扎穩打，必有收穫。",
    "平平安安，適合在熟悉的打獵區輕鬆練功。",
    "今天出門似乎踩到了綠水靈，出團請多加留意。",
    "黑軍壓境... 建議今天待在村莊裡看風景就好。",
    "今天手氣旺盛，連路邊的木妖都對你點頭微笑！",
    "靈感湧現，打王走位如行雲流水，神級操作！"
]

YI_ACTIONS = [
    "使用墊卷法衝裝，大成功！",
    "準時上車打龍王，分寶分到手軟",
    "不斷刷新拍賣所，成功撿漏神裝",
    "去弓箭手村找長老斯坦吸好運",
    "把不需要的母礦丟給新手積陰德",
    "逛拍賣撿漏，當個快樂的奸商",
    "跟公會隊友組隊推王，默契滿分"
]

JI_ACTIONS = [
    "頭鐵連續怒點 30% 詛咒卷",
    "王剛死掉、寶物掉下來的瞬間無情斷線",
    "打王時忘記開寵物自動補血",
    "半夜腦波弱，把主武器拿去衝白衣卷軸",
    "沒帶萬能療傷藥就被抓去打王",
    "黑騎士手滑把神聖之火關掉",
    "盲目單挑高等王，狂噴經驗值"
]

LUCKY_MAPS = [
    "殘暴炎魔的祭壇",
    "闇黑龍王洞穴",
    "天皇殿堂",
    "海怒斯洞窟",
    "蘑菇王之墓",
    "被詛咒的寺院",
    "夜市徒步區<7>",
    "鋼之肥肥公園",
    "名人大道西部區域",
    "狐狸山坡",
    "豐饒的藥草田",
    "時間神殿深處",
    "玩具城愛爾達斯"
]

DROPS_FORECAST = [
    "日之鏢",
    "月飛鏢",
    "雷之鏢",
    "炎魔頭盔",
    "闇黑龍王的項鍊",
    "闇黑龍王的翅膀",
    "楓葉祝福技能書 Lv20",
    "絕對引力技能書 Lv30",
    "眼部裝飾力量詛咒卷軸 30%",
    "眼部裝飾敏捷詛咒卷軸 30%",
    "眼部裝飾智力詛咒卷軸 30%",
    "眼部裝飾幸運詛咒卷軸 30%",
    "臉飾力量卷軸 30%",
    "臉飾敏捷卷軸 30%",
    "臉飾智力卷軸 30%",
    "臉飾幸運卷軸 30%",
    "項鍊力量卷軸 30%",
    "項鍊敏捷卷軸 30%",
    "項鍊智力卷軸 30%",
    "項鍊幸運卷軸 30%",
    "頭盔智力卷軸 60%",
    "寒冰膠囊 / 火焰膠囊"
]

NOBLE_ROLES = [
    "幫放祈禱的【主教】",
    "生命神聖之火的【黑騎士】",
    "爆擊輸出的【夜使者】",
    "先煙再躺的【暗影神偷】",
    "最強單體的【聖騎士】",
    "能扛能打的【英雄】",
    "閃電連鎖的【冰雷大魔導士】",
    "全畫面清怪的【火毒大魔導士】",
    "瘋狂連射的【箭神】",
    "貫穿到底的【神射手】",
    "風騷拉拉龍的【拳霸】",
    "章魚當家的【槍神】"
]

TAROT_GUIDES = [
    ("【0. 愚者】(正位)", "全新大膽嘗試！今天適合挑戰從未打過的王。"),
    ("【I. 魔術師】(正位)", "資源充足，技能全開！今天是展現實力的好日子。"),
    ("【II. 女祭司】(正位)", "直覺敏銳，你能精準判斷 Boss 的下一步動作。"),
    ("【III. 女皇】(正位)", "豐收之兆！今天的掉寶率特別高，快去農怪吧！"),
    ("【IV. 皇帝】(正位)", "穩如泰山。今天你的防禦力提升，扛怪沒煩惱。"),
    ("【VI. 戀人】(正位)", "絕佳組隊運！今天能遇到神仙隊友，默契滿分。"),
    ("【VII. 戰車】(正位)", "衝勁十足，刷怪效率極高！"),
    ("【VIII. 力量】(正位)", "堅韌意志。遇到困難不要放棄，勝利就在眼前。"),
    ("【IX. 隱者】(正位)", "適合單人行動。今天一個人靜靜練功效率更高。"),
    ("【X. 命運之輪】(逆位)", "運勢低谷。今天不宜衝裝，請把卷軸存進倉庫。"),
    ("【XIII. 死神】(正位)", "舊的結束新的開始。是時候淘汰舊裝換新武器！"),
    ("【XIV. 節制】(正位)", "保持平衡。別把藥水一次喝光，留點給後面的戰鬥。"),
    ("【XVII. 星星】(正位)", "充滿希望。今天幸運之神眷顧著你，大膽挑戰吧！"),
    ("【XIX. 太陽】(正位)", "活力充沛。今天狀態極佳，可以連續打好幾場王團！"),
    ("【XXI. 世界】(正位)", "完美達成。今天所有遠征都將圓滿結束！")
]

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                discord_id INTEGER PRIMARY KEY,
                current_level INTEGER DEFAULT 1,
                current_xp INTEGER DEFAULT 0,
                last_fortune_date TEXT,
                last_fortune2_date TEXT
            );
        """)
        
        # Add column if upgrading existing DB
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_fortune2_date TEXT")
        except sqlite3.OperationalError:
            pass
        
        # 2. characters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                character_id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id INTEGER,
                character_name TEXT UNIQUE,
                character_class TEXT,
                character_level INTEGER,
                tickets_count INTEGER DEFAULT 0,
                FOREIGN KEY (discord_id) REFERENCES users (discord_id)
            );
        """)
        
        # 3. cooldowns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cooldowns (
                discord_id INTEGER PRIMARY KEY,
                last_chat_xp_timestamp INTEGER,
                voice_join_timestamp INTEGER
            );
        """)
        
        # 4. toxic_quotes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS toxic_quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote TEXT UNIQUE,
                toxicity_level TEXT,
                added_by INTEGER,
                created_at TEXT
            );
        """)
        
        cursor.execute("SELECT COUNT(*) FROM toxic_quotes")
        if cursor.fetchone()[0] == 0:
            today_str = get_today_str()
            for q, lvl in DEFAULT_TOXIC_QUOTES:
                cursor.execute(
                    "INSERT OR IGNORE INTO toxic_quotes (quote, toxicity_level, added_by, created_at) VALUES (?, ?, ?, ?)",
                    (q, lvl, 0, today_str)
                )
        conn.commit()
    print("5AM Database tables initialized successfully.")

def get_today_str():
    # 每日重置標準：台北時間每天 08:00 AM (UTC+8)
    # 透過減去 8 小時，使得 00:00~07:59:59 歸為前一天的週期，08:00 準時進入新一天週期
    tz_utc8 = datetime.timezone(datetime.timedelta(hours=8))
    today_dt = datetime.datetime.now(tz_utc8) - datetime.timedelta(hours=8)
    return today_dt.strftime("%Y-%m-%d")

# --- FORTUNE 1 FUNCTIONS ---

def check_fortune_status(discord_id):
    today_str = get_today_str()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_fortune_date FROM users WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        
        if row is None or row[0] is None:
            return True, None
        
        last_date = row[0]
        if last_date == today_str:
            return False, last_date
        return True, last_date

def record_fortune(discord_id):
    today_str = get_today_str()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (discord_id, last_fortune_date) 
            VALUES (?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET last_fortune_date = ?
        """, (discord_id, today_str, today_str))
        conn.commit()

# --- FORTUNE 2 FUNCTIONS ---

def check_fortune2_status(discord_id):
    today_str = get_today_str()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_fortune2_date FROM users WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        
        if row is None or row[0] is None:
            return True, None
        
        last_date = row[0]
        if last_date == today_str:
            return False, last_date
        return True, last_date

def record_fortune2(discord_id):
    today_str = get_today_str()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (discord_id, last_fortune2_date) 
            VALUES (?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET last_fortune2_date = ?
        """, (discord_id, today_str, today_str))
        conn.commit()

def generate_fortune2_data():
    tier = random.choice(FORTUNE2_TIERS)
    oracle = random.choice(ORACLE_MESSAGES)
    yi = random.choice(YI_ACTIONS)
    ji = random.choice(JI_ACTIONS)
    map_name = random.choice(LUCKY_MAPS)
    drop = random.choice(DROPS_FORECAST)
    noble = random.choice(NOBLE_ROLES)
    tarot_card, tarot_desc = random.choice(TAROT_GUIDES)
    
    return {
        "tier": tier,
        "oracle": oracle,
        "yi": yi,
        "ji": ji,
        "map": map_name,
        "drop": drop,
        "noble": noble,
        "tarot_card": tarot_card,
        "tarot_desc": tarot_desc
    }

# --- TOXIC QUOTES FUNCTIONS ---

def add_toxic_quote(quote: str, toxicity_level: str, added_by: int):
    today_str = get_today_str()
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO toxic_quotes (quote, toxicity_level, added_by, created_at) VALUES (?, ?, ?, ?)",
                (quote.strip(), toxicity_level, added_by, today_str)
            )
            conn.commit()
            return True, "成功新增一碗毒雞湯！"
    except sqlite3.IntegrityError:
        return False, "這句毒雞湯語錄庫裡已經有了喵！"
    except Exception as e:
        return False, f"新增失敗: {e}"

def get_random_toxic_quote():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT quote, toxicity_level FROM toxic_quotes ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row[0], row[1]
    return random.choice(DEFAULT_TOXIC_QUOTES)

def get_toxic_quote_count():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM toxic_quotes")
        return cursor.fetchone()[0]

# --- LEVELING & XP FUNCTIONS (FOR FUTURE EXPANSION) ---

def xp_needed_for_level(level):
    return 100 * level + 100

def get_cumulative_xp(level, current_xp):
    total = current_xp
    for lvl in range(1, level):
        total += xp_needed_for_level(lvl)
    return total

def add_chat_xp(discord_id):
    now_ts = int(datetime.datetime.utcnow().timestamp())
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT last_chat_xp_timestamp FROM cooldowns WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        
        if row and row[0] and (now_ts - row[0] < 60):
            return None
            
        cursor.execute("""
            INSERT INTO cooldowns (discord_id, last_chat_xp_timestamp) 
            VALUES (?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET last_chat_xp_timestamp = ?
        """, (discord_id, now_ts, now_ts))
        
        cursor.execute("SELECT current_level, current_xp FROM users WHERE discord_id = ?", (discord_id,))
        user_row = cursor.fetchone()
        
        if user_row:
            old_level, old_xp = user_row
        else:
            old_level, old_xp = 1, 0
            cursor.execute("INSERT INTO users (discord_id, current_level, current_xp) VALUES (?, 1, 0)", (discord_id,))
            
        xp_added = random.randint(15, 25)
        new_xp = old_xp + xp_added
        
        level = old_level
        leveled_up = False
        while True:
            needed = xp_needed_for_level(level)
            if new_xp >= needed:
                new_xp -= needed
                level += 1
                leveled_up = True
            else:
                break
                
        cursor.execute("UPDATE users SET current_level = ?, current_xp = ? WHERE discord_id = ?", (level, new_xp, discord_id))
        conn.commit()
        
    return (xp_added, old_level, level if leveled_up else None, new_xp, xp_needed_for_level(level))

def add_voice_xp(discord_id, minutes):
    xp_added = int(minutes * 10)
    if xp_added <= 0:
        lvl, xp, needed = get_level_data(discord_id)
        return (0, lvl, None, xp, needed)
        
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT current_level, current_xp FROM users WHERE discord_id = ?", (discord_id,))
        user_row = cursor.fetchone()
        
        if user_row:
            old_level, old_xp = user_row
        else:
            old_level, old_xp = 1, 0
            cursor.execute("INSERT INTO users (discord_id, current_level, current_xp) VALUES (?, 1, 0)", (discord_id,))
            
        new_xp = old_xp + xp_added
        level = old_level
        leveled_up = False
        while True:
            needed = xp_needed_for_level(level)
            if new_xp >= needed:
                new_xp -= needed
                level += 1
                leveled_up = True
            else:
                break
                
        cursor.execute("UPDATE users SET current_level = ?, current_xp = ? WHERE discord_id = ?", (level, new_xp, discord_id))
        conn.commit()
        
    return (xp_added, old_level, level if leveled_up else None, new_xp, xp_needed_for_level(level))

def get_level_data(discord_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT current_level, current_xp FROM users WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        if row:
            level, xp = row
        else:
            level, xp = 1, 0
            cursor.execute("INSERT INTO users (discord_id, current_level, current_xp) VALUES (?, 1, 0)", (discord_id,))
            conn.commit()
            
    return (level, xp, xp_needed_for_level(level))

def get_leaderboard(limit=30):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT discord_id, current_level, current_xp FROM users")
        rows = cursor.fetchall()
        
    leaderboard = []
    for discord_id, level, xp in rows:
        total = get_cumulative_xp(level, xp)
        leaderboard.append((discord_id, level, xp, total))
        
    leaderboard.sort(key=lambda x: x[3], reverse=True)
    return leaderboard[:limit]

def modify_user_level(discord_id, level_diff):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT current_level, current_xp FROM users WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        if row:
            lvl, xp = row
        else:
            lvl, xp = 1, 0
            cursor.execute("INSERT INTO users (discord_id, current_level, current_xp) VALUES (?, 1, 0)", (discord_id,))
            
        new_level = max(1, lvl + level_diff)
        needed = xp_needed_for_level(new_level)
        new_xp = min(xp, needed - 1)
        
        cursor.execute("UPDATE users SET current_level = ?, current_xp = ? WHERE discord_id = ?", (new_level, new_xp, discord_id))
        conn.commit()
        
    return (new_level, new_xp)

def reset_season():
    top_10 = get_leaderboard(limit=10)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET current_level = 1, current_xp = 0")
        cursor.execute("DELETE FROM cooldowns")
        conn.commit()
    return top_10

def set_voice_join_timestamp(discord_id, timestamp):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cooldowns (discord_id, voice_join_timestamp) 
            VALUES (?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET voice_join_timestamp = ?
        """, (discord_id, timestamp, timestamp))
        conn.commit()

def get_voice_join_timestamp(discord_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT voice_join_timestamp FROM cooldowns WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        return row[0] if row else None

def clear_voice_join_timestamp(discord_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE cooldowns SET voice_join_timestamp = NULL WHERE discord_id = ?", (discord_id,))
        conn.commit()
