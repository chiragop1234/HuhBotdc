import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from flask import Flask
from threading import Thread

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
WEB_PORT = 3210  # Choose your desired port for the web server

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

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

app = Flask(__name__)

# Define a route for the web server
@app.route('/')
def index():
    return 'Hello, this is your web server!'

# Run the web server in a separate thread
def run_web_server():
    app.run(host='0.0.0.0', port=WEB_PORT)

web_server_thread = Thread(target=run_web_server)
web_server_thread.start()

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
        cc_file_path = 'cc.txt'
        with open(cc_file_path, 'r') as cc_file:
            # Read all lines from cc.txt
            cc_lines = cc_file.readlines()

        if cc_lines:
            # Take the first line from cc.txt
            cc_content = cc_lines[0].strip()

            # Remove the claimed line from cc.txt
            with open(cc_file_path, 'w') as cc_file:
                cc_file.writelines(cc_lines[1:])

            # Send CC in DM
            try:
                await ctx.author.send(f"CLAIM YOUR FREE CC COST 1 TOKEN\n{cc_content}")
            except discord.Forbidden:
                await ctx.send("Failed to send CC in DM. Please make sure your DMs are open.")
            else:
                # Create an interactive message with a Claim button
                claim_button = discord.ui.Button(style=discord.ButtonStyle.green, label="Claim CC", custom_id="claim_cc")
                view = discord.ui.View()
                view.add_item(claim_button)

                await ctx.send("CC sent in DM! Check your direct messages.", view=view)
        else:
            await ctx.send("No more CCs available. Earn more by chatting!")
    else:
        await ctx.send("Insufficient tokens. Earn more by chatting!")

# Make sure to include the web server thread cleanup on bot shutdown
@bot.event
async def on_shutdown():
    print("Bot is shutting down.")
    web_server_thread.join()

bot.run(TOKEN)
