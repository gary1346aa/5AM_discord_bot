import sqlite3
import datetime

DB_FILE = "5am_bot.db"

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
        conn.commit()
    print("Database tables initialized successfully.")

def get_today_str():
    # Helper to get today's date string in UTC+8 (Asia/Taipei)
    tz_utc8 = datetime.timezone(datetime.timedelta(hours=8))
    today_dt = datetime.datetime.now(tz_utc8)
    return today_dt.strftime("%Y-%m-%d")

def check_fortune_status(discord_id):
    """
    Returns (can_get_fortune: bool, last_fortune_date: str)
    """
    today_str = get_today_str()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_fortune_date FROM users WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        
        if row is None:
            # User not in database yet
            return True, None
        
        last_date = row[0]
        if last_date == today_str:
            return False, last_date
        return True, last_date

def record_fortune(discord_id):
    today_str = get_today_str()
    with get_connection() as conn:
        cursor = conn.cursor()
        # Insert or ignore user row first, then update last_fortune_date
        cursor.execute("""
            INSERT INTO users (discord_id, last_fortune_date) 
            VALUES (?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET last_fortune_date = ?
        """, (discord_id, today_str, today_str))
        conn.commit()

# --- MILESTONE 4: LEVELING & XP FUNCTIONS ---

import random

def xp_needed_for_level(level):
    return 100 * level + 100

def get_cumulative_xp(level, current_xp):
    total = current_xp
    for lvl in range(1, level):
        total += xp_needed_for_level(lvl)
    return total

def add_chat_xp(discord_id):
    """
    Attempts to award random chat XP (15-25) if cooldown (60s) has expired.
    Returns:
        (xp_added, old_level, new_level, current_xp, xp_needed) if XP was awarded (new_level is None if no level up occurred).
        None if user is on cooldown.
    """
    now_ts = int(datetime.datetime.utcnow().timestamp())
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Check cooldown
        cursor.execute("SELECT last_chat_xp_timestamp FROM cooldowns WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        
        if row and row[0] and (now_ts - row[0] < 60):
            return None # On cooldown
            
        # Update cooldown timestamp
        cursor.execute("""
            INSERT INTO cooldowns (discord_id, last_chat_xp_timestamp) 
            VALUES (?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET last_chat_xp_timestamp = ?
        """, (discord_id, now_ts, now_ts))
        
        # Get user details
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
                
        # Update user
        cursor.execute("UPDATE users SET current_level = ?, current_xp = ? WHERE discord_id = ?", (level, new_xp, discord_id))
        conn.commit()
        
    return (xp_added, old_level, level if leveled_up else None, new_xp, xp_needed_for_level(level))

def add_voice_xp(discord_id, minutes):
    """
    Awards voice XP (10 XP per minute).
    Returns: (xp_added, old_level, new_level, current_xp, xp_needed)
    """
    xp_added = int(minutes * 10)
    if xp_added <= 0:
        # Just return current levels
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
    """
    Returns (level, xp, xp_needed)
    """
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
    """
    Returns list of tuples: [(discord_id, level, xp, total_xp), ...]
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # To order correctly by total XP, we can pull all user data
        cursor.execute("SELECT discord_id, current_level, current_xp FROM users")
        rows = cursor.fetchall()
        
    leaderboard = []
    for discord_id, level, xp in rows:
        total = get_cumulative_xp(level, xp)
        leaderboard.append((discord_id, level, xp, total))
        
    # Sort by total cumulative XP descending
    leaderboard.sort(key=lambda x: x[3], reverse=True)
    return leaderboard[:limit]

def modify_user_xp(discord_id, xp_diff):
    """
    Directly adds/removes XP. Adjusts level automatically.
    Returns: (new_level, new_xp)
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT current_level, current_xp FROM users WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        if row:
            lvl, xp = row
        else:
            lvl, xp = 1, 0
            cursor.execute("INSERT INTO users (discord_id, current_level, current_xp) VALUES (?, 1, 0)", (discord_id,))
            
        total_xp = get_cumulative_xp(lvl, xp) + xp_diff
        if total_xp < 0:
            total_xp = 0
            
        # Re-evaluate level and remaining xp
        level = 1
        rem_xp = total_xp
        while True:
            needed = xp_needed_for_level(level)
            if rem_xp >= needed:
                rem_xp -= needed
                level += 1
            else:
                break
                
        cursor.execute("UPDATE users SET current_level = ?, current_xp = ? WHERE discord_id = ?", (level, rem_xp, discord_id))
        conn.commit()
        
    return (level, rem_xp)

def modify_user_level(discord_id, level_diff):
    """
    Modifies user level directly.
    Returns: (new_level, new_xp)
    """
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
        # Cap current_xp if it exceeds the new level limit
        needed = xp_needed_for_level(new_level)
        new_xp = min(xp, needed - 1)
        
        cursor.execute("UPDATE users SET current_level = ?, current_xp = ? WHERE discord_id = ?", (new_level, new_xp, discord_id))
        conn.commit()
        
    return (new_level, new_xp)

def reset_season():
    """
    Resets all levels/XP. Returns top 10 users pre-reset for honors.
    """
    top_10 = get_leaderboard(limit=10)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET current_level = 1, current_xp = 0")
        cursor.execute("DELETE FROM cooldowns") # Reset cooldown records too
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

