import os
import discord
import datetime
import random
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
        
        if GUILD_ID != 0:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            self.tree.clear_commands(guild=None)
            await self.tree.sync(guild=None)
            
            print(f"Syncing slash commands to 5AM Guild ({GUILD_ID})...")
            synced = await self.tree.sync(guild=guild)
            print(f"Successfully synced {len(synced)} active commands to 5AM Guild:")
            for cmd in synced:
                print(f"  - /{cmd.name}: {cmd.description}")

bot = FiveAMBot()

@bot.event
async def on_ready():
    print("------")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("5AM Bot is online and ready!")
    print("------")

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

# ----------------- ACTIVE COMMANDS -----------------

# 1. /每日運勢 (經典星座色彩版)
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
        title=f"🔮 {interaction.user.display_name} 的今日運勢 (經典版)",
        color=0xF39C12
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    embed.add_field(name="✨ 運勢等級", value=f"**{level}**", inline=False)
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

# 2. /每日運勢2 (Artale 冒險者神諭與打王宜忌版)
@bot.tree.command(name="每日運勢2", description="Artale 冒險者專屬神諭占卜 (含打王宜忌、掉寶預測、貴人職業與幸運地圖)")
async def fortune2(interaction: discord.Interaction):
    discord_id = interaction.user.id
    can_get, last_date = database.check_fortune2_status(discord_id)
    
    if not can_get:
        await interaction.response.send_message(
            f"⚠️ {interaction.user.mention}，你今天已經領取過 Artale 冒險者神諭囉！明日請早喵～",
            ephemeral=False
        )
        return
    
    f2 = database.generate_fortune2_data()
    
    # Color palette based on tier
    if "大吉" in f2["tier"]:
        embed_color = 0xF1C40F # Gold
    elif "中吉" in f2["tier"]:
        embed_color = 0x3498DB # Blue
    elif "小吉" in f2["tier"]:
        embed_color = 0x2ECC71 # Green
    elif "大凶" in f2["tier"]:
        embed_color = 0x111111 # Dark Black
    else:
        embed_color = 0xE67E22 # Orange / Danger
        
    embed = discord.Embed(
        title=f"⚔️ {interaction.user.display_name} 的 Artale 冒險者神諭",
        description=f"> 📜 今日神諭：**{f2['oracle']}**",
        color=embed_color
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    embed.add_field(name="📜 運勢等級", value=f"### {f2['tier']}", inline=False)
    embed.add_field(name="⭕ 今日【宜】", value=f"```fix\n{f2['yi']}```", inline=False)
    embed.add_field(name="❌ 今日【忌】", value=f"```diff\n- {f2['ji']}```", inline=False)
    embed.add_field(name="🤝 貴人隊友", value=f"`{f2['noble']}`", inline=True)
    embed.add_field(name="🗺️ 幸運地圖", value=f"`{f2['map']}`", inline=True)
    embed.add_field(name="💎 掉寶預測", value=f"`{f2['drop']}`", inline=False)
    embed.add_field(name="🎴 命運塔羅指引", value=f"**{f2['tarot_card']}**\n> {f2['tarot_desc']}", inline=False)
    
    embed.set_footer(text="5AM 冒險神諭庫 ｜ 占卜結果僅供娛樂與打王參考 ˊˇˋ ✨")
    
    database.record_fortune2(discord_id)
    
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
                f"⚔️ 你的 Artale 冒險者神諭已發送到 {quote_channel.mention} 囉喵！",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(embed=embed)

# 3. /每日毒湯
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

# 4. /新增毒湯
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

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN is not set in the .env file.")
    else:
        bot.run(TOKEN)
