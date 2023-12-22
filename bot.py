import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
PREFIX = '!'
TOKEN_PER_MESSAGE = 0.2
TOKEN_PER_INVITE = 10
OWNER_ID = 761886210120744990

bot = commands.Bot(command_prefix=PREFIX)
bot.remove_command('help')  # Remove the default help command

user_tokens = {}


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
        title='Bot Commands',
        description='Use these commands to interact with the bot.',
        color=discord.Color.blue()
    )
    embed.add_field(name=f'{PREFIX}claim', value='Claim your free credit card.', inline=False)
    embed.add_field(name=f'{PREFIX}balance', value='Check your token balance.', inline=False)
    await ctx.send(embed=embed)


@bot.command(name='claim')
async def claim_command(ctx):
    user_id = ctx.author.id

    if user_id == OWNER_ID:
        user_tokens[user_id] = 99999
    else:
        if user_id not in user_tokens:
            user_tokens[user_id] = 0

        if user_tokens[user_id] >= 1:
            # Generate random fake credit card details
            cc_details = generate_random_cc()

            # Send a DM with the credit card details
            await ctx.author.send(f'Claim your free credit card!\n\n{cc_details}')

            # Update user tokens
            user_tokens[user_id] -= 1
        else:
            await ctx.send("Sorry, you don't have enough tokens to claim a credit card.")

    # Avoid responding to the bot's own messages
    if ctx.author != bot.user:
        # Send a message in the channel indicating the DM
        message = await ctx.send("Check your DMs for the credit card details!")

        # Add reactions to the message
        for emoji in ['👍', '👎']:
            await message.add_reaction(emoji)


@bot.command(name='balance')
async def balance_command(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_id = member.id
    balance = user_tokens.get(user_id, 0)
    await ctx.send(f'{member.mention}, your token balance: {balance}')


def generate_random_cc():
    # Generate random credit card details (placeholder values)
    cc_number = ' '.join([''.join(random.choices('0123456789', k=4)) for _ in range(4)])
    exp_date = f'{random.randint(1, 12):02}/{random.randint(2023, 2030)}'
    cvv = ''.join(random.choices('0123456789', k=3))
    currency = random.choice(['USD', 'EUR', 'GBP'])
    amount = f"${random.uniform(1, 1000):,.2f}"

    return f"{cc_number} | {exp_date} | {cvv} | {currency} | {amount}"


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return  # Ignore reactions from bots

    if reaction.message.content.startswith("Check your DMs for the credit card details!") and str(reaction.emoji) == '👍':
        await user.send("You liked the credit card! 🌟")
    elif reaction.message.content.startswith("Check your DMs for the credit card details!") and str(reaction.emoji) == '👎':
        await user.send("You disliked the credit card! 😞")


bot.run(TOKEN)
