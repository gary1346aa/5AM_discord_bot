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
                last_fortune_date TEXT
            );
        """)
        
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
        
        # Seed initial toxic quotes if table is empty
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
    tz_utc8 = datetime.timezone(datetime.timedelta(hours=8))
    today_dt = datetime.datetime.now(tz_utc8)
    return today_dt.strftime("%Y-%m-%d")

def check_fortune_status(discord_id):
    today_str = get_today_str()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_fortune_date FROM users WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        
        if row is None:
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

# --- LEVELING & XP FUNCTIONS ---

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
            cursor.execute("INSERT INTO users (discord_id, current_level, current_xp) VALUES (?, ?, ?)", (discord_id, 1, 0))
            
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
            cursor.execute("INSERT INTO users (discord_id, current_level, current_xp) VALUES (?, ?, ?)", (discord_id, 1, 0))
            
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
