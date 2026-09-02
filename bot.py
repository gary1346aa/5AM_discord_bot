import os
import discord
import datetime
import random
import math
from discord import app_commands
from dotenv import load_dotenv

import database

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "1375419109323440169"))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", "0"))
VOICE_LOG_CHANNEL_ID = int(os.getenv("VOICE_LOG_CHANNEL_ID", "0"))
QUOTE_CHANNEL_ID = int(os.getenv("QUOTE_CHANNEL_ID", "0"))
LEVEL_CHANNEL_ID = int(os.getenv("LEVEL_CHANNEL_ID", "0"))
RULES_CHANNEL_ID = int(os.getenv("RULES_CHANNEL_ID", "0"))

FORTUNE_LEVELS = ["大吉", "中吉", "小吉", "末吉", "凶"]

FORTUNE_COMMENTS = {
    "大吉": [
        "萬事如意，走路都會撿到錢喵！",
        "今天運勢極佳，衝卷成功機率暴增喵！",
        "福星高照，打寶打怪通通大順利喵！"
    ],
    "中吉": [
        "運氣不錯，適合開啟新計畫喵。",
        "平穩好運，今天也是美好的一天喵。",
        "做決定會很順利，相信自己的直覺喵！"
    ],
    "小吉": [
        "平穩的一天，會有小驚喜發生喵。",
        "知足常樂，今天會過得很舒心喵。",
        "小小的幸運正在路上，保持微笑喵。"
    ],
    "末吉": [
        "稍微注意一下隨身物品，平安就是福喵。",
        "今天適合穩紮穩打，不宜太過冒險喵。",
        "低調行事，今天平平安安就是最大的收穫喵。"
    ],
    "凶": [
        "今天適合宅在家裡玩遊戲，少出門為妙喵。",
        "萬事小心，多喝水，多休息喵。",
        "運勢低迷，今天適合當個快樂的薪水小偷喵。"
    ]
}

LUCKY_COLORS = ["天空藍", "薄荷綠", "珊瑚粉", "櫻花粉", "極致黑", "薰衣草紫", "琥珀橙", "檸檬黃", "象牙白", "翡翠綠"]
CONSTELLATIONS = ["牡羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座", "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"]

LEVEL_UP_PHRASES = [
    "我的天啊，你也太會聊天了吧 喵！",
    "聊天大師就是你喵！",
    "繼續保持，貓貓看好你喵！",
    "今天也是元氣滿滿的一天喵！",
    "看來有人說話停不下來喵～",
    "水啦！等級又變高了喵！"
]

def format_join_time(joined_at):
    if not joined_at:
        joined_at = discord.utils.utcnow()
    tz_utc8 = datetime.timezone(datetime.timedelta(hours=8))
    local_dt = joined_at.astimezone(tz_utc8)
    return local_dt.strftime("%Y/%m/%d %H:%M")

class FiveAMBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        database.init_db()
        
        # 1. Clear any old global commands to prevent stale commands from appearing
        print("Cleaning up old global commands...")
        self.tree.clear_commands(guild=None)
        await self.tree.sync()
        
        # 2. Sync active commands to the 5AM Guild for instant update
        if GUILD_ID != 0:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            print(f"Syncing slash commands to 5AM Guild ({GUILD_ID})...")
            await self.tree.sync(guild=guild)
            print("Slash commands synced to guild successfully!")

bot = FiveAMBot()

@bot.event
async def on_ready():
    print("------")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("5AM Bot is online and connected!")
    print("------")

    now_ts = int(datetime.datetime.utcnow().timestamp())
    for guild in bot.guilds:
        if GUILD_ID == 0 or guild.id == GUILD_ID:
            for vc in guild.voice_channels:
                for member in vc.members:
                    if not member.bot:
                        if database.get_voice_join_timestamp(member.id) is None:
                            database.set_voice_join_timestamp(member.id, now_ts)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
        
    if not message.guild or (GUILD_ID != 0 and message.guild.id != GUILD_ID):
        return
        
    res = database.add_chat_xp(message.author.id)
    if res:
        xp_added, old_lvl, new_lvl, current_xp, xp_needed = res
        if new_lvl is not None:
            channel = bot.get_channel(LEVEL_CHANNEL_ID)
            if channel:
                phrase = random.choice(LEVEL_UP_PHRASES)
                msg = (
                    f"🎊 **恭喜 {message.author.mention} 升等了！**\n"
                    f"📈 目前等級：**Lv. {new_lvl}**\n"
                    f"✨ 距離下一等還差：**{xp_needed - current_xp} XP**\n"
                    f"💡 *{phrase}*"
                )
                try:
                    await channel.send(msg)
                except Exception as e:
                    print(f"Failed to send chat level up alert: {e}")

@bot.event
async def on_member_join(member):
    if WELCOME_CHANNEL_ID == 0:
        return
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        join_time_str = format_join_time(member.joined_at)
        rules_text = f"📜 請先閱讀規則並領取身分組 <#{RULES_CHANNEL_ID}>。\n" if RULES_CHANNEL_ID != 0 else "📜 請先閱讀伺服器規則並領取身分組。\n"
        embed = discord.Embed(
            title="🌅 歡迎加入 5AM 🌅",
            description=(
                f"Hi! {member.mention}\n\n"
                f"✨ 歡迎加入 ✨ 5AM，願你在這裡遇見屬於自己的早晨與陪伴。\n\n"
                f"{rules_text}"
                f"📝 請將暱稱修改為遊戲暱稱 / 職業。\n"
                f"💬 有任何問題都可以詢問管理員。\n\n"
                f"🤍 希望你能在這裡留下美好的回憶。\n\n"
                f"📊 目前伺服器人數\n"
                f"**{member.guild.member_count} 人**\n\n"
                f"加入時間 : {join_time_str}"
            ),
            color=0xF39C12
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Failed to send welcome message: {e}")

@bot.event
async def on_member_remove(member):
    if WELCOME_CHANNEL_ID == 0:
        return
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        leave_time_str = format_join_time(None)
        embed = discord.Embed(
            title="🌙 成員離開了 5AM 🌙",
            description=(
                f"**{member.name}**（{member.mention}）已經離開了我們。\n\n"
                f"✨ 感謝你曾陪伴我們度過這段時光，祝你未來旅途一切順利！\n\n"
                f"📊 目前伺服器人數\n"
                f"**{member.guild.member_count} 人**\n\n"
                f"離開時間 : {leave_time_str}"
            ),
            color=0x808080
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Failed to send farewell message: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    if GUILD_ID != 0 and member.guild.id != GUILD_ID:
        return

    log_channel = bot.get_channel(VOICE_LOG_CHANNEL_ID) if VOICE_LOG_CHANNEL_ID != 0 else None
    lvl_channel = bot.get_channel(LEVEL_CHANNEL_ID) if LEVEL_CHANNEL_ID != 0 else None
    now_ts = int(datetime.datetime.utcnow().timestamp())

    # Case A: Connect
    if before.channel is None and after.channel is not None:
        database.set_voice_join_timestamp(member.id, now_ts)

    # Case B: Disconnect
    elif before.channel is not None and after.channel is None:
        join_ts = database.get_voice_join_timestamp(member.id)
        database.clear_voice_join_timestamp(member.id)
        if join_ts:
            minutes = (now_ts - join_ts) / 60.0
            xp_res = database.add_voice_xp(member.id, minutes)
            xp_added, old_lvl, new_lvl, current_xp, xp_needed = xp_res
            if new_lvl is not None and lvl_channel:
                msg = f"🎊 **{member.mention}** 在語音頻道中進化了！目前等級：**Lv.{new_lvl}** 喵！"
                try:
                    await lvl_channel.send(msg)
                except Exception as e:
                    print(f"Failed to send voice level up alert: {e}")

    # Case C: Switch
    elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
        join_ts = database.get_voice_join_timestamp(member.id)
        database.set_voice_join_timestamp(member.id, now_ts)
        if join_ts:
            minutes = (now_ts - join_ts) / 60.0
            xp_res = database.add_voice_xp(member.id, minutes)
            xp_added, old_lvl, new_lvl, current_xp, xp_needed = xp_res
            if new_lvl is not None and lvl_channel:
                msg = f"🎊 **{member.mention}** 在語音頻道中進化了！目前等級：**Lv.{new_lvl}** 喵！"
                try:
                    await lvl_channel.send(msg)
                except Exception as e:
                    print(f"Failed to send voice level up alert: {e}")

    # Voice logging
    if not log_channel:
        return

    if before.channel is None and after.channel is not None:
        msg = (
            f"🔊 **{member.display_name}** 進入了語音頻道\n"
            f"📍 頻道：**{after.channel.name}**\n"
            f"👥 目前人數：**{len(after.channel.members)}**"
        )
        try:
            await log_channel.send(msg)
        except Exception as e:
            print(f"Failed to send voice join log: {e}")

    elif before.channel is not None and after.channel is None:
        msg = (
            f"🔇 **{member.display_name}** 離開了語音頻道\n"
            f"📍 頻道：**{before.channel.name}**\n"
            f"👥 剩餘人數：**{len(before.channel.members)}**"
        )
        try:
            await log_channel.send(msg)
        except Exception as e:
            print(f"Failed to send voice leave log: {e}")

    elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
        msg = (
            f"🔄 **{member.display_name}** 切換了語音頻道\n"
            f"📤 離開：**{before.channel.name}** ({len(before.channel.members)}人)\n"
            f"📥 進入：**{after.channel.name}** ({len(after.channel.members)}人)"
        )
        try:
            await log_channel.send(msg)
        except Exception as e:
            print(f"Failed to send voice switch log: {e}")

# ----------------- DAILY FORTUNE & TOXIC QUOTES -----------------

@bot.tree.command(name="每日運勢", description="查看今日運勢、幸運色與貴人星座")
async def fortune(interaction: discord.Interaction):
    discord_id = interaction.user.id
    can_get, last_date = database.check_fortune_status(discord_id)
    
    if not can_get:
        await interaction.response.send_message(
            f"⚠️ {interaction.user.mention}，你今天已經算過命囉！明日請早喵～",
            ephemeral=False
        )
        return
    
    level = random.choice(FORTUNE_LEVELS)
    comment = random.choice(FORTUNE_COMMENTS[level])
    color = random.choice(LUCKY_COLORS)
    noble = random.choice(CONSTELLATIONS)
    
    embed = discord.Embed(
        title=f"🔮 {interaction.user.display_name} 的今日運勢",
        color=0xF39C12
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    embed.add_field(name="✨ 運勢等級", value=level, inline=False)
    embed.add_field(name="💬 今日短評", value=comment, inline=False)
    embed.add_field(name="🎨 幸運色", value=f"`{color}`", inline=True)
    embed.add_field(name="🤝 貴人星座", value=f"`{noble}`", inline=True)
    embed.add_field(name="\u200b", value="占卜結果僅供參考，祝你有美好的一天！喵 ˊˇˋ", inline=False)
    
    database.record_fortune(discord_id)
    
    if QUOTE_CHANNEL_ID == 0:
        await interaction.response.send_message(embed=embed)
        return
        
    quote_channel = bot.get_channel(QUOTE_CHANNEL_ID)
    if not quote_channel:
        await interaction.response.send_message(embed=embed)
        return
        
    if interaction.channel_id == QUOTE_CHANNEL_ID:
        await interaction.response.send_message(embed=embed)
    else:
        try:
            await quote_channel.send(embed=embed)
            await interaction.response.send_message(
                f"🔮 你的今日運勢已發送到 {quote_channel.mention} 囉喵！",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(embed=embed)

@bot.tree.command(name="每日毒湯", description="隨機領取一碗心靈毒雞湯")
async def toxic(interaction: discord.Interaction):
    quote, toxicity_level = database.get_random_toxic_quote()
    
    is_normal = "普通" in toxicity_level
    embed = discord.Embed(
        title="🥣 今日心靈毒湯" if is_normal else "💀 今日劇毒砒霜",
        description=f"```{quote}```",
        color=0x808080 if is_normal else 0x111111
    )
    embed.add_field(name="☠️ 毒性等級", value=toxicity_level, inline=True)
    embed.set_footer(text=f"5AM 毒湯庫 ｜ 點閱者: {interaction.user.display_name}")
    
    if QUOTE_CHANNEL_ID == 0:
        await interaction.response.send_message(embed=embed)
        return
        
    quote_channel = bot.get_channel(QUOTE_CHANNEL_ID)
    if not quote_channel:
        await interaction.response.send_message(embed=embed)
        return
        
    if interaction.channel_id == QUOTE_CHANNEL_ID:
        await interaction.response.send_message(embed=embed)
    else:
        try:
            await quote_channel.send(embed=embed)
            await interaction.response.send_message(
                f"🥣 毒雞湯已送入 {quote_channel.mention} 囉喵！",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(embed=embed)

@bot.tree.command(name="新增毒湯", description="管理員新增自訂毒雞湯至語錄庫")
@app_commands.describe(quote="要新增的毒雞湯內容", toxicity_level="毒湯等級分類")
@app_commands.choices(toxicity_level=[
    app_commands.Choice(name="⭐ 普通毒湯", value="⭐ 普通毒湯"),
    app_commands.Choice(name="💀 劇毒砒霜", value="💀 劇毒砒霜")
])
async def add_toxic(interaction: discord.Interaction, quote: str, toxicity_level: str = "⭐ 普通毒湯"):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ 只有管理員可以新增毒雞湯喵！", ephemeral=True)
        return
        
    if not quote.strip():
        await interaction.response.send_message("❌ 請輸入有效的毒雞湯內容喵！", ephemeral=True)
        return
        
    success, msg = database.add_toxic_quote(quote.strip(), toxicity_level, interaction.user.id)
    if success:
        total_count = database.get_toxic_quote_count()
        embed = discord.Embed(
            title="✅ 毒雞湯新增成功！",
            description=f"```{quote.strip()}```",
            color=0x2ECC71
        )
        embed.add_field(name="☠️ 毒性等級", value=toxicity_level, inline=True)
        embed.add_field(name="📚 語錄庫總數", value=f"`{total_count}` 則", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(f"⚠️ {msg}", ephemeral=True)

# ----------------- LEVELING & LEADERBOARD COMMANDS -----------------

@bot.tree.command(name="等級", description="查看自己或他人的活躍等級與經驗值")
async def rank(interaction: discord.Interaction, member: discord.Member = None):
    target_member = member or interaction.user
    if target_member.bot:
        await interaction.response.send_message("❌ 機器人沒有活躍等級喵！", ephemeral=True)
        return
        
    lvl, xp, needed = database.get_level_data(target_member.id)
    total_xp = database.get_cumulative_xp(lvl, xp)
    
    percentage = min(1.0, xp / needed) if needed > 0 else 1.0
    filled = int(percentage * 10)
    bar = "▰" * filled + "▱" * (10 - filled)
    
    embed = discord.Embed(
        title=f"📊 {target_member.display_name} 的活躍等級",
        color=0xF39C12
    )
    embed.set_thumbnail(url=target_member.display_avatar.url)
    embed.add_field(name="📈 目前等級", value=f"**Lv. {lvl}**", inline=True)
    embed.add_field(name="🏆 累計總經驗", value=f"`{total_xp:,} XP`", inline=True)
    embed.add_field(
        name="✨ 經驗值 (XP)", 
        value=f"`{xp:,} / {needed:,} XP`\n{bar} ({int(percentage * 100)}%)", 
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="排行榜", description="查看伺服器活躍等級排行榜前30名")
async def leaderboard(interaction: discord.Interaction):
    top_30 = database.get_leaderboard(limit=30)
    
    if not top_30:
        await interaction.response.send_message("📊 排行榜目前空空如也，快去說話聊天吧喵！", ephemeral=True)
        return
        
    embed = discord.Embed(
        title="🏆 5AM 伺服器活躍度等級排行榜 (TOP 30)",
        description="快來看看是誰在伺服器裡最愛聊天與掛網！\n*每個月 1 號將會自動清空歸零。*",
        color=0xF39C12
    )
    
    hall_of_fame = []
    backbone = []
    close_behind = []
    
    for i, row in enumerate(top_30, 1):
        uid, lvl, xp, total_xp = row
        if i == 1:
            rank_label = "🥇"
        elif i == 2:
            rank_label = "🥈"
        elif i == 3:
            rank_label = "🥉"
        elif i <= 10:
            rank_label = f"`#{i:02d}`"
        else:
            rank_label = f"`#{i}`"
            
        line = f"{rank_label} <@{uid}> ｜ **Lv.{lvl}** ｜ Total XP: `{total_xp:,}`"
        
        if i <= 10:
            hall_of_fame.append(line)
        elif i <= 20:
            backbone.append(line)
        else:
            close_behind.append(line)
            
    if hall_of_fame:
        embed.add_field(name="👑 榮譽殿堂 (1 - 10)", value="\n".join(hall_of_fame), inline=False)
    if backbone:
        embed.add_field(name="✨ 中流砥柱 (11 - 20)", value="\n".join(backbone), inline=False)
    if close_behind:
        embed.add_field(name="🔥 緊追在後 (21 - 30)", value="\n".join(close_behind), inline=False)
        
    await interaction.response.send_message(embed=embed)

# --- ADMIN ACTIONS ---

@bot.tree.command(name="加權升等", description="管理員加持直接提升成員等級")
@app_commands.describe(member="要升等的成員", levels="要提升的等級數量")
async def add_level(interaction: discord.Interaction, member: discord.Member, levels: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ 你沒有權限使用此管理員指令喵！", ephemeral=True)
        return
        
    if member.bot:
        await interaction.response.send_message("❌ 無法為機器人修改等級喵！", ephemeral=True)
        return
        
    if levels <= 0:
        await interaction.response.send_message("❌ 請輸入大於 0 的等級數量喵！", ephemeral=True)
        return
        
    new_lvl, new_xp = database.modify_user_level(member.id, levels)
    announcement = f"🎊 透過管理員加持，{member.mention} 升到了 **Lv.{new_lvl}**！"
    lvl_channel = bot.get_channel(LEVEL_CHANNEL_ID)
    
    if lvl_channel:
        try:
            await lvl_channel.send(announcement)
        except Exception as e:
            print(f"Failed to post admin level up broadcast: {e}")
            
    await interaction.response.send_message(f"✅ 已成功將 {member.display_name} 升等至 Lv. {new_lvl}。", ephemeral=True)

@bot.tree.command(name="天災降等", description="天災懲罰降低成員等級")
@app_commands.describe(member="要降等的成員", levels="要降低的等級數量")
async def remove_level(interaction: discord.Interaction, member: discord.Member, levels: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ 你沒有權限使用此管理員指令喵！", ephemeral=True)
        return
        
    if member.bot:
        await interaction.response.send_message("❌ 無法為機器人修改等級喵！", ephemeral=True)
        return
        
    if levels <= 0:
        await interaction.response.send_message("❌ 請輸入大於 0 的等級數量喵！", ephemeral=True)
        return
        
    new_lvl, new_xp = database.modify_user_level(member.id, -levels)
    announcement = f"⚡ 喔不！有人被雷劈到，{member.mention} 竟然降到了 **Lv.{new_lvl}**... 😭"
    lvl_channel = bot.get_channel(LEVEL_CHANNEL_ID)
    
    if lvl_channel:
        try:
            await lvl_channel.send(announcement)
        except Exception as e:
            print(f"Failed to post admin level down broadcast: {e}")
            
    await interaction.response.send_message(f"✅ 已成功將 {member.display_name} 降等至 Lv. {new_lvl}。", ephemeral=True)

@bot.tree.command(name="重置賽季", description="重置全服等級並發布上賽季終極榮譽榜")
async def reset_season_cmd(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ 你沒有權限使用此管理員指令喵！", ephemeral=True)
        return
        
    top_10 = database.reset_season()
    lvl_channel = bot.get_channel(LEVEL_CHANNEL_ID)
    if not lvl_channel:
        await interaction.response.send_message("❌ 找不到等級通知頻道，無法完成廣播喵！", ephemeral=True)
        return
        
    honor_lines = []
    for i, row in enumerate(top_10, 1):
        uid, lvl, xp, total_xp = row
        if i == 1:
            emoji = "🥇"
        elif i == 2:
            emoji = "🥈"
        elif i == 3:
            emoji = "🥉"
        else:
            emoji = f"`#{i:02d}`"
        honor_lines.append(f"{emoji} **Lv.{lvl}** - <@{uid}> (總經驗: {total_xp:,} XP)")
        
    honor_board = (
        "🏆 **【5AM 上賽季活躍度等級終極榮譽榜 - TOP 10】** 🏆\n"
        "感謝以下十位大老上個月在伺服器的爆肝陪伴！\n"
        "---------------------------------------\n" +
        "\n".join(honor_lines) +
        "\n---------------------------------------"
    )
    
    season_start = (
        "📅 📌 **【5AM 新賽季正式啟動通知】**\n"
        "新的一個月開始了！全伺服器的**等級與經驗值已全數歸零重置** 喵！\n"
        "聊天與語音的新戰場正式展開，大家重新出發吧！衝啊 ˊˇˋ ✨"
    )
    
    try:
        await lvl_channel.send(honor_board)
        await lvl_channel.send(season_start)
        await interaction.response.send_message("✅ 賽季重置廣播已成功送出！", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ 廣播發送失敗: {e}", ephemeral=True)

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN is not set in the .env file.")
    else:
        bot.run(TOKEN)
