import discord
from discord.ext import commands
import os
import random
import sqlite3

print("🔄 Bot starting...")

# Используем py-cord который стабильнее
bot = commands.Bot(command_prefix='!')

# База данных
def init_db():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 100)''')
    conn.commit()
    conn.close()

init_db()

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user.name} is online!')
    await bot.change_presence(activity=discord.Game(name="!help"))

@bot.command()
async def balance(ctx):
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", (ctx.author.id, 100))
    c.execute("SELECT balance FROM users WHERE user_id = ?", (ctx.author.id,))
    balance = c.fetchone()[0]
    conn.close()
    await ctx.send(f"💵 Ваш баланс: **{balance} монет**")

@bot.command()
async def daily(ctx):
    reward = random.randint(50, 150)
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", (ctx.author.id, 100))
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, ctx.author.id))
    conn.commit()
    conn.close()
    await ctx.send(f"🎁 Вы получили **{reward} монет**!")

@bot.command()
async def work(ctx):
    salary = random.randint(20, 60)
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", (ctx.author.id, 100))
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (salary, ctx.author.id))
    conn.commit()
    conn.close()
    await ctx.send(f"💼 Вы заработали **{salary} монет**!")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🆘 Команды бота", color=0x00ff00)
    embed.add_field(name="!balance", value="Проверить баланс", inline=False)
    embed.add_field(name="!daily", value="Ежедневная награда", inline=False)
    embed.add_field(name="!work", value="Заработать деньги", inline=False)
    await ctx.send(embed=embed)

print("🚀 Launching bot...")
bot.run(os.getenv('BOT_TOKEN'))
