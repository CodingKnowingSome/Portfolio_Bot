import discord
from discord.ext import commands
from discord import app_commands
import logging

from DutyStates.Views import PersistentFetchView
from access_check import has_required_role

logger = logging.getLogger(__name__)

class SendFetch(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sendfetch", description="Send the duty state fetch message again.")
    async def sendfetch(self, interaction: discord.Interaction):
        ADMIN_ROLE_ID = 1526372536273862776
        if not await has_required_role(interaction, ADMIN_ROLE_ID):
            return

        channel = self.bot.get_channel(1526383804464365628)
        embed = discord.Embed(
            title="Fetch a duty state!",
            color=discord.Color.blue()
        )
        view = PersistentFetchView(self.bot)
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message("Fetch added.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SendFetch(bot))
    bot.add_view(PersistentFetchView(bot))
