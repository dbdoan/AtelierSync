import discord
from discord import app_commands
from discord.ext import commands
import pandas as pd

class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.csv_file = 'ids.csv'

    @app_commands.command(name="ping", description="Responds with pong")
    @commands.has_permissions(administrator=True)
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong")
        
    @app_commands.command(name="setchannel", description="Sets channel for cat fact output")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        channel_id = interaction.channel_id
        guild_id = interaction.guild_id

        try:
            df = pd.read_csv(self.csv_file)

            # Check if the guild_id already exists in the CSV
            if df['guild_id'].eq(guild_id).any():
                df.loc[df['guild_id'] == guild_id, 'channel_id'] = channel_id
            else:
                new_row = pd.DataFrame({'guild_id': [guild_id], 'channel_id': [channel_id]})
                df = pd.concat([df, new_row], ignore_index=True)

            df.to_csv(self.csv_file, index=False)

            await interaction.followup.send(f"Channel ID for this server has been set to {channel_id}.\nThis channel will be used for Github updates output.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)

    # Uncomment in the future if you are experimenting with bot and run into a rate limit. 
    # Better to sync commands sparingly rather than every time you run the bot.

    @app_commands.command(name="sync", description="To safely sync new commands to prevent rate limit.")
    @commands.is_owner()
    async def sync(self, interaction: discord.Interaction):
        # Get the guild from the interaction
        guild = interaction.guild
        
        if guild:  # Sync only for the current guild
            self.bot.tree.copy_global_to(guild=guild)
            await self.bot.tree.sync(guild=guild)
            await interaction.response.send_message(f"Commands synced to this guild ({guild.name})", ephemeral=True)
        else:  # In case it's used outside of a guild (e.g., in DMs)
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)

    @sync.error
    async def sync_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.NotOwner):
            await interaction.response.send_message("You are not the owner!", ephemeral=True)

# /////////// /////////// ///////////
# Globally updates all commands on each bot-boot
# Not good in practice as it may cause rate-limit issues
# Manual sync command above preferred
    # @commands.Cog.listener()
    # async def on_ready(self):
    #     try:
    #         await self.bot.tree.sync()
    #         print("Commands synced globally")
    #     except Exception as e:
    #         print(f"Failed to sync commands: {e}")

# /////////// /////////// ///////////
async def setup(bot):
    await bot.add_cog(BotCommands(bot))