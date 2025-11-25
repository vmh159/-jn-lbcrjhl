import discord
from discord.ext import commands
import os
import random
import datetime
import sqlite3

# Настройки бота
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# База данных
def init_db():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, 
                  balance INTEGER DEFAULT 100,
                  daily_claimed TEXT DEFAULT NULL)''')
    conn.commit()
    conn.close()

init_db()

class EconomyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user_data(self, user_id):
        conn = sqlite3.connect('economy.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        
        if not user:
            self.create_user(user_id)
            return self.get_user_data(user_id)
        return user

    def create_user(self, user_id):
        conn = sqlite3.connect('economy.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", 
                 (user_id, 100))
        conn.commit()
        conn.close()

    def update_balance(self, user_id, amount):
        conn = sqlite3.connect('economy.db')
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", 
                 (amount, user_id))
        conn.commit()
        conn.close()

    # ЕЖЕДНЕВНАЯ НАГРАДА
    @commands.command(name='daily')
    async def daily(self, ctx):
        user_data = self.get_user_data(ctx.author.id)
        daily_claimed = user_data[2]
        
        if daily_claimed:
            last_claim = datetime.datetime.fromisoformat(daily_claimed)
            now = datetime.datetime.now()
            
            if (now - last_claim).days < 1:
                time_left = 24 - (now - last_claim).seconds // 3600
                await ctx.send(f"⏰ Вы уже получали награду! Ждите {time_left} часов.")
                return
        
        reward = random.randint(50, 150)
        self.update_balance(ctx.author.id, reward)
        
        conn = sqlite3.connect('economy.db')
        c = conn.cursor()
        c.execute("UPDATE users SET daily_claimed = ? WHERE user_id = ?", 
                 (datetime.datetime.now().isoformat(), ctx.author.id))
        conn.commit()
        conn.close()
        
        await ctx.send(f"🎁 Вы получили **{reward} монет**!")

    # БАЛАНС
    @commands.command(name='balance')
    async def balance(self, ctx):
        user_data = self.get_user_data(ctx.author.id)
        balance = user_data[1]
        await ctx.send(f"💵 Ваш баланс: **{balance} монет**")

    # РАБОТА
    @commands.command(name='work')
    async def work(self, ctx):
        salary = random.randint(20, 80)
        self.update_balance(ctx.author.id, salary)
        await ctx.send(f"💼 Вы заработали **{salary} монет**!")

    # ПЕРЕВОД
    @commands.command(name='pay')
    async def pay(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("❌ Сумма должна быть положительной!")
            return
        
        user_balance = self.get_user_data(ctx.author.id)[1]
        
        if user_balance < amount:
            await ctx.send("❌ Недостаточно средств!")
            return
        
        self.update_balance(ctx.author.id, -amount)
        self.update_balance(member.id, amount)
        await ctx.send(f"💸 {ctx.author.mention} перевел {member.mention} **{amount} монет**!")

    # ТОП
    @commands.command(name='top')
    async def top(self, ctx):
        conn = sqlite3.connect('economy.db')
        c = conn.cursor()
        c.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 5")
        top_users = c.fetchall()
        conn.close()
        
        embed = discord.Embed(title="🏆 Топ 5 богачей", color=0xffd700)
        
        for i, (user_id, balance) in enumerate(top_users, 1):
            user = self.bot.get_user(user_id)
            if user:
                embed.add_field(name=f"{i}. {user.display_name}", value=f"💵 {balance} монет", inline=False)
        
        await ctx.send(embed=embed)

    # ПОМОЩЬ
    @commands.command(name='help')
    async def help_command(self, ctx):
        embed = discord.Embed(title="🆘 Команды бота", color=0x9b59b6)
        commands_list = [
            ("!daily", "Ежедневная награда"),
            ("!work", "Заработать деньги"),
            ("!balance", "Проверить баланс"),
            ("!pay @user сумма", "Перевести деньги"),
            ("!top", "Топ 5 богачей")
        ]
        
        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user.name} запущен!')
    await bot.add_cog(EconomyBot(bot))
    await bot.change_presence(activity=discord.Game(name="!help"))

if __name__ == "__main__":
    bot.run(os.getenv('BOT_TOKEN'))