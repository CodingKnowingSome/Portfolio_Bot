"""
Lists all the active blacklists in an embed with multiple pages.
"""
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import logging
import config
import math

logger = logging.getLogger(__name__)
API_URL = config.API_URL


class BlacklistList(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="blacklist-list", description="List blacklisted users.")
    async def blacklist_list(self, interaction: discord.Interaction):
        """
        Calls the blacklist API endpoint for the blacklisted users, calls the build_blacklist_embed function to
        create an embed, if there are over 10 blacklists, adds the buttons, and sends the embed.
        Args:
            interaction: The interaction object from discord.Interaction.
        """
        await interaction.response.defer()
        api_key = config.API_KEY

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_URL}/blacklistlist", headers=headers) as resp:
                    data = await resp.json()
                    if resp.status == 200 and data.get("success"):
                        count = data.get("count", 0)
                        items = data.get("blacklist", [])
                        embed = build_blacklist_embed(items, count, page=0)
                        if count <= 10:
                            await interaction.followup.send(embed=embed)
                        else:
                            view = Blacklistpager(items, count, author_id=interaction.user.id)
                            await interaction.followup.send(embed=embed, view=view)
                    else:
                        await interaction.followup.send("An error occurred, please try again later.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in /blacklist-list: {e}")
            await interaction.followup.send("An error occurred, please try again later.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(BlacklistList(bot))


def build_blacklist_embed(items: list[dict], count: int, page: int, per_page: int = 10) -> discord.Embed:
    """
    Creates the embed with the blacklisted users.
    Args:
        items: The blacklisted users.
        count: The number of blacklisted users.
        page: The current page the embed is on.
        per_page: The number of users per page (default to 10).

    Returns: The current embed page.

    """
    total_pages = math.ceil(count / per_page) if count > 0 else 1
    embed = discord.Embed(
        title="Blacklisted Users",
        color=discord.Color.red()
    )
    if count == 0:
        embed.description = "No blacklisted users found."
        return embed
    start = page * per_page
    end = start + per_page
    page_items = items[start:end]
    for entry in page_items:
        ts = f"<t:{entry['last_edit']}:R>" if entry.get('last_edit') else "N/A"
        embed.add_field(
            name=f"{entry['username']} (`{entry['user_id']}`)",
            value=f"**Reason:** {entry['reason']}\n**Updated:** {ts}\n",
            inline=False
        )
    embed.set_footer(text=f"Page {page + 1} of {total_pages} | Total: {count} entries.")
    return embed


class Blacklistpager(discord.ui.View):
    def __init__(self, items: list, count: int, author_id: int, per_page: int = 10):
        super().__init__(timeout=180)
        self.items = items
        self.count = count
        self.author_id = author_id
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = math.ceil(count / per_page) if count > 0 else 1
        self.update_button_states()

    def update_button_states(self):
        """
        Disables the corresponding buttons on the first and last page.
        """
        self.prev_btn.disabled = (self.current_page == 0)
        self.next_btn.disabled = (self.current_page == self.total_pages - 1)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You can not control this list.", ephemeral=True)
            return False
        return True

    # noinspection PyUnusedLocal
    @discord.ui.button(label="< Previous")
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        The previous button.
        Args:
            interaction: The interaction object from discord.Interaction.
            button: The discord.ui.Button.
        """
        if self.current_page > 0:
            self.current_page -= 1
            self.update_button_states()
            embed = build_blacklist_embed(self.items, self.count, self.current_page, self.per_page)
            await interaction.response.edit_message(embed=embed, view=self)

    # noinspection PyUnusedLocal
    @discord.ui.button(label="Next >")
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        The next button.
        Args:
            interaction: The interaction object from discord.Interaction.
            button: The discord.ui.Button.
        """
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_button_states()
            embed = build_blacklist_embed(self.items, self.count, self.current_page, self.per_page)
            await interaction.response.edit_message(embed=embed, view=self)
