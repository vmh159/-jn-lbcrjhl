import discord
from discord.ext import commands
import os
import random

print("🔄 Starting bot...")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="!help"))

@bot.command()
async def ping(ctx):
    await ctx.send('Pong! 🏓')

@bot.command()
async def balance(ctx):
    await ctx.send('💵 Your balance: **100 coins**')

@bot.command()
async def daily(ctx):
    reward = random.randint(50, 150)
    await ctx.send(f'🎁 Daily reward: **{reward} coins**!')

@bot.command()
async def help(ctx):
    await ctx.send('🆘 Commands: !ping, !balance, !daily')

if __name__ == "__main__":
    print("🚀 Starting bot...")
    bot.run(os.getenv('BOT_TOKEN'))