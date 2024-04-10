# This example requires the 'message_content' privileged intent to function.
from __future__ import annotations
import re
from typing import Final
import os
from dotenv import load_dotenv
from discord.ext import commands
import discord

get = discord.utils.get

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Define a simple View that persists between bot restarts
# In order for a view to persist between restarts it needs to meet the following conditions:
# 1) The timeout of the View has to be set to None
# 2) Every item in the View has to have a custom_id set
# It is recommended that the custom_id be sufficiently unique to
# prevent conflicts with other buttons the bot sends.
# For this example the custom_id is prefixed with the name of the bot.
# Note that custom_ids can only be up to 100 characters long.
class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Go Online', style=discord.ButtonStyle.gray, custom_id='persistent_view:status')
    async def toggleStatus(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = get(interaction.guild.roles, name="Online")
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("see you soon...", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("welcome back 😈", ephemeral=True)

class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('/'), intents=intents)

    async def setup_hook(self) -> None:
        # Register the persistent view for listening here.
        # Note that this does not send the view to any message.
        # In order to do this you need to first send a message with the View, which is shown below.
        # If you have the message_id you can also pass it as a keyword argument, but for this example
        # we don't have one.
        self.add_view(PersistentView())

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = PersistentViewBot()

@bot.command()
async def offline(ctx: commands.Context):
    """Makes user appear offline to server."""
    await ctx.message.delete()
    role = ctx.author.get_role(1220986329467195463)
    if (role):
        await ctx.author.remove_roles(role)

@bot.command()
@commands.is_owner()
async def status_button(ctx: commands.Context):
    """Creates the server's status button."""
    # In order for a persistent view to be listened to, it needs to be sent to an actual message.
    # Call this method once just to store it somewhere.
    # In a more complicated program you might fetch the message_id from a database for use later.
    # However this is outside of the scope of this simple example.
    await ctx.message.delete()
    await ctx.send("", view=PersistentView())

bot.run(TOKEN)