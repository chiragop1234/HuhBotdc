import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store user balances (user_id: tokens)
user_balances = {}

# Function to save user balances to a file
def save_balances():
    with open('balances.txt', 'w') as file:
        for user_id, tokens in user_balances.items():
            file.write(f'{user_id}:{tokens}\n')

# Load user balances from a file (if the file exists)
balances_file_path = 'balances.txt'
if os.path.exists(balances_file_path):
    with open(balances_file_path, 'r') as file:
        for line in file:
            if line.strip():  # Check if the line is not empty
                parts = line.strip().split(':')
                if len(parts) == 2:
                    user_id, tokens = parts
                    user_balances[int(user_id)] = float(tokens)
                else:
                    print(f"Ignoring invalid line in {balances_file_path}: {line.strip()}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.event
async def on_message(message):
    if message.channel.id == CHANNEL_ID:
        # Award tokens for messages
        user_id = message.author.id
        user_balances[user_id] = user_balances.get(user_id, 0) + 0.2
        save_balances()

    await bot.process_commands(message)

@bot.command()
async def balance(ctx):
    user_id = ctx.author.id
    current_balance = user_balances.get(user_id, 0)
    await ctx.send(f'Your current balance is {current_balance:.1f} tokens.')

@bot.command(name="helpme")
async def help_me(ctx):
    help_message = (
        "Welcome to the CC Bot!\n\n"
        "**Commands:**\n"
        "`!balance`: Check your token balance.\n"
        "`!claim`: Claim a CC for 1 token.\n"
        "`!helpme`: Display this help message."
    )
    await ctx.send(help_message)

@bot.command()
async def claim(ctx):
    user_id = ctx.author.id
    if user_id not in user_balances:
        # Create data for a user if it doesn't exist
        user_balances[user_id] = 0

    if user_balances.get(user_id, 0) >= 1:
        user_balances[user_id] -= 1
        save_balances()

        # Implement CC claiming logic here
        with open('cc.txt', 'r') as cc_file:
            cc_content = cc_file.read()

        # Truncate the message content to fit within Discord's limit
        truncated_content = f"CLAIM YOUR FREE CC COST 1 TOKEN\n{cc_content[:1990]}"  

        # Send CC in DM
        try:
            await ctx.author.send(truncated_content)
        except discord.Forbidden:
            await ctx.send("Failed to send CC in DM. Please make sure your DMs are open.")
        else:
            # Create an interactive message with a Claim button
            claim_button = discord.ui.Button(style=discord.ButtonStyle.green, label="Claim CC", custom_id="claim_cc")
            view = discord.ui.View()
            view.add_item(claim_button)

            await ctx.send("CC sent in DM! Check your direct messages.", view=view)
    else:
        await ctx.send("Insufficient tokens. Earn more by chatting!")

@bot.event
async def on_button_click(interaction):
    if interaction.custom_id == "claim_cc":
        # Implement additional logic for processing CC claims
        # For example, you can read from cc.txt and send the CC
        with open('cc.txt', 'r') as cc_file:
            cc_content = cc_file.read()
        await interaction.response.send_message(f"CC claimed successfully!\n{cc_content}", ephemeral=True)

bot.run(TOKEN)
