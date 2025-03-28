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
            channel_id_row = df.loc[df['guild_id'].astype(str) == str(guild_id), 'channel_id']
            if not channel_id_row.empty:
                print(f"Found channel_id {channel_id_row.iloc[0]} for guild_id {guild_id}")
                return int(channel_id_row.iloc[0])
            else:
                print(f"No entry for guild_id {guild_id} found in the CSV file.")
        except Exception as e:
            print(f"Error reading channel ID from CSV: {e}")
        return None

    async def post_github_update(self, guild_id, data, branch):
        """Post a formatted update to the specified guild's channel, only if it's pushed to the main branch."""
        # Since we already filtered out non-main branches, proceed directly.
        channel_id = self.get_channel_id(guild_id)
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            if channel:
                # Extract details from the data
                user = data.get('pusher', {}).get('name', 'Unknown user')
                commit_message = data.get('head_commit', {}).get('message', 'No commit message found')
                commit_url = data.get('head_commit', {}).get('url', 'No URL provided')

                # Format the message
                message = (
                    f"✅ **An update has been pushed to main** ✅\n\n"
                    f"**Pushed by**: {user}\n\n"
                    f"**Update**: \n{commit_message}\n"
                    "\n"
                    "< ==================================== >\n"
                    f"**Github Update**: {commit_url}\n"
                    "\n"
                    "**Tasks**: <https://tinyurl.com/g-docs-tasks>"
                )

                # Send the message to the channel
                await channel.send(message)
                print(f"Sent update to channel {channel_id} for guild {guild_id}.")
            else:
                print(f"Channel with ID {channel_id} not found!")
        else:
            print(f"No channel ID set for guild {guild_id}.")

async def setup(bot):
    await bot.add_cog(GitHubUpdater(bot))