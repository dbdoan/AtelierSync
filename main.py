import pandas as pd
from aiohttp import web
import asyncio
import discord
from discord.ext import commands
import json
import logging
from my_keys import bot_token

from os import system

system('clear')

# /////////// /////////// ///////////
DISCORD_BOT_TOKEN = bot_token
CSV_FILE = 'ids.csv'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

async def load_cogs():
    await bot.load_extension("commands_cog")
    await bot.load_extension("github_updater_cog")

def get_guild_id_from_csv():
    """Retrieve the appropriate guild_id from the CSV file based on criteria."""
    try:
        df = pd.read_csv(CSV_FILE)
        if not df.empty:
            print(f"Loaded CSV data:\n{df}")
            return int(df.iloc[0]['guild_id'])
    except Exception as e:
        print(f"Error reading guild ID from CSV: {e}")
    return None

logging.basicConfig(level=logging.INFO)

async def github_webhook(request):
    try:
        logging.info("Received a request from GitHub webhook.")

        # Parse the incoming JSON data.
        data = await request.json()
        logging.info(f"Received JSON data: {json.dumps(data, indent=2)}")

        # Extract the branch name from the 'ref' field.
        ref = data.get('ref', '')
        branch = ref.split('/')[-1] if 'refs/heads/' in ref else 'Unknown branch'
        logging.info(f"Detected branch: {branch}")

        # Check if the branch is 'main'
        if branch.lower() != "main":
            logging.info(f"Branch '{branch}' is not 'main'. Skipping notification.")
            return web.Response(text="Branch is not main, no notification sent.", status=200)

        # Get commit message and other details.
        update_data = data.get('head_commit', {}).get('message', 'No commit message found')
        logging.info(f"Update data: {update_data}")

        # Retrieve the guild ID for the Discord server.
        guild_id = get_guild_id_from_csv()
        logging.info(f"Using guild_id: {guild_id}")

        if guild_id:
            # Send the data to the GitHubUpdater cog for further processing.
            await bot.get_cog("GitHubUpdater").post_github_update(guild_id, data, branch)
        else:
            logging.warning("No guild_id found in the CSV file.")

    except json.decoder.JSONDecodeError:
        logging.error("Failed to decode JSON. The payload might be empty or malformed.")
        return web.Response(text="Invalid JSON payload", status=400)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return web.Response(text="Internal server error", status=500)

    return web.Response(text="Received", status=200)

app = web.Application()
app.add_routes([web.post('/github-webhook', github_webhook)])

async def run_app():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("Webhook listener running on port 8080")

async def main():
    await load_cogs()
    await run_app()
    await bot.start(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())