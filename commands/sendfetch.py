import discord
from discord.ext import commands
from discord import app_commands
import logging
from discord.ui import Button, View
from DutyStates.Fetch import Fetch
import logging

logger = logging.getLogger(__name__)

class SendFetch(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sendfetch", description="Send the duty state fetch message again.")
    async def sendfetch(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(1526383804464365628)
        embed = discord.Embed(
            title="Fetch a duty state!",
            color=discord.Color.blue()
        )
        button = Button(label="Fetch a duty state!", style=discord.ButtonStyle.primary)
        view = View()
        view.add_item(button)
        fetch = await channel.send(embed=embed, view=view)
        async def button_callback(interaction: discord.Interaction):
            await Fetch(self.bot, interaction.user, fetch)
        button.callback = button_callback
        await interaction.response.send_message("Fetch added.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SendFetch(bot))