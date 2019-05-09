"""Contains bot administration related commands. Currently is cog loading and a depreciated prefix changer"""

import discord
from discord.ext import commands
from asyncio import TimeoutError
import logging


class AdminCog(commands.Cog, name="Admin Commands"):
    """AdminCogs"""

    def __init__(self, bot):
        self.bot: commands.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='load new cogs', hidden=True)
    @commands.is_owner()
    async def load_cogs(self, ctx, *, cog: str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(hidden=True, name="prefix")
    @commands.has_role('Mod')
    async def change_prefix(self, ctx, *, new_prefix: str):
        """ Changes the prefix used to call the bot. Only usable mod role. Currently broken

        Default prefix is r!
        Literally requires a role with name 'Mod' to use
        """
        global bot_prefix
        bot_prefix = new_prefix
        self.bot.command_prefix(bot_prefix)
        await ctx.send("The bot prefix was changed to `" + bot_prefix + "`")
        await self.bot.change_presence(activity=discord.Game(name='Type `' + bot_prefix + 'help` to get started!'))

    @commands.command(hidden=True)
    @commands.has_permissions(kick_members=True)
    @commands.has_role("Mod")
    async def kick_bot(self, ctx: commands.Context):
        """
        Asks the bot to leave the server.

        Requires mod role or admin perms, asks for confirmation with reaction.
        """
        sent_message: discord.Message = await ctx.send(
            f"{ctx.author.display_name}, please click the check to confirm that I should leave. "
            "If this was a mistake, just ignore this message.", delete_after=35)
        await sent_message.add_reaction("✔")

        def check(reaction, user: discord.User):
            return user == ctx.author and reaction.message.id == sent_message.id

        try:
            reaction: discord.Reaction = await self.bot.wait_for("reaction_add", check=check, timeout=30)
        except TimeoutError:
            await ctx.send("Command timed out! If you are trying to kick the bot, "
                           "invoke the command again and click the reaction faster.", delete_after=5)
        else:
            if reaction[0].emoji == "✔":
                await ctx.send("Ok, cya around!", delete_after=5)
                await ctx.guild.leave()
                logging.exception(f"I was asked to leave a server", exc_info=[ctx.guild.name, ctx.guild.id])
            else:
                await ctx.send("That's not the right reaction. If that was a mistake, invoke the command again.",
                               delete_after=5)


def setup(bot):
    bot.add_cog(AdminCog(bot))
