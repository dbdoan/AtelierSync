import discord
from discord.ext import commands
import pandas as pd

class GitHubUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.csv_file = 'ids.csv'

    @commands.Cog.listener()
    async def on_ready(self):
        print("GitHubUpdater Cog is ready.")

    def get_channel_id(self, guild_id):
        """Retrieve the channel ID for a given guild from the CSV file."""
        try:
            df = pd.read_csv(self.csv_file)
            # Get the channel_id corresponding to the guild_id
            channel_id_row = df.loc[df['guild_id'] == guild_id, 'channel_id']
            if not channel_id_row.empty:
                return int(channel_id_row.iloc[0])  # Return the channel_id as an integer
        except Exception as e:
            print(f"Error reading channel ID: {e}")
        return None

    async def post_github_update(self, guild_id, update_data):
        # Retrieve the appropriate channel_id from the CSV
        channel_id = self.get_channel_id(guild_id)
        
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            if channel:
                # Customize the message based on the data you receive from GitHub
                message = f"New update in the GitHub repo:\n{update_data}"
                await channel.send(message)
            else:
                print(f"Channel with ID {channel_id} not found!")
        else:
            print(f"No channel ID set for guild {guild_id}.")

async def setup(bot):
    await bot.add_cog(GitHubUpdater(bot))