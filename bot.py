import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('Hello!')

bot.run(TOKEN)
