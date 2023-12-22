import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
PREFIX = '!'
OWNER_ID = 761886210120744990
TOKEN_PER_MESSAGE = 0.2
TOKEN_PER_INVITE = 10

bot = commands.Bot(command_prefix=PREFIX)
bot.remove_command('help')  # Remove the default help command

user_tokens = []
credit_cards = []

# Load existing credit cards from a file
with open('cc.txt', 'r') as file:
    credit_cards = [line.strip() for line in file]

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    await bot.process_commands(message)  # Process commands

    user_id = message.author.id

    if user_id != bot.user.id:  # Ignore the bot's own messages
        # Award tokens for sending messages
        user_tokens.append(user_id)

@bot.event
async def on_invite_create(invite):
    # Award tokens for creating an invite
    user_id = invite.inviter.id
    user_tokens.append(user_id)

@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
        title='Bot Commands',
        description='Use these commands to interact with the bot.',
        color=discord.Color.blue()
    )
    embed.add_field(name=f'{PREFIX}balance', value='Check your token balance.', inline=False)
    await ctx.send(embed=embed)

@bot.command(name='balance')
async def balance_command(ctx, member: discord.Member = None):
    member = member or ctx.author
    balance = user_tokens.count(member.id) * TOKEN_PER_MESSAGE
    await ctx.send(f'{member.mention}, your token balance: {balance}')

@bot.command(name='claim')
async def claim_command(ctx):
    user_id = ctx.author.id

    if user_id == OWNER_ID:
        user_tokens.append(user_id)  # Owner has unlimited tokens
    else:
        if user_tokens.count(user_id) >= 1 and credit_cards:
            # Get and remove a credit card from the list
            cc_details = credit_cards.pop()

            # Send a DM with the credit card details
            await ctx.author.send(f'Claim your free credit card!\n\n{cc_details}')
        else:
            await ctx.send("Sorry, you don't have enough tokens or there are no more credit cards.")

    # Send a message in the channel indicating the DM
    await ctx.send("Check your DMs for the credit card details!")

bot.run(TOKEN)
