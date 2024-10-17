import asyncio
import discord
from discord.ext import commands
from my_keys import bot_token

from os import system

system('clear')

# /////////// /////////// ///////////
DISCORD_BOT_TOKEN = bot_token

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Load the Cog(s)
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

async def load_cogs():
    await bot.load_extension("commands_cog")

async def main():
    await load_cogs()
    await bot.start(DISCORD_BOT_TOKEN)

# Run the bot using asyncio.run()
if __name__ == "__main__":
    asyncio.run(main())