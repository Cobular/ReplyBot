"""Contains bot administration related commands. Currently is cog loading and a depreciated prefix changer"""

import discord
from discord.ext import commands


# General Cog Structure ACK: Discord.py Documentation, Rapptz: https://discordpy.readthedocs.io/en/latest/
class AdminCog(commands.Cog, name="Admin Commands"):
    """AdminCogs"""

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    # ACK: User-made gist: https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load_cog(self, ctx, *, cog: str):
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
        """ Changes the prefix used to call the bot. Only usable mod role. Currently broken, DO NOT USE!!

        Default prefix is r!
        Literally requires a role with name 'Mod' to use
        """
        global bot_prefix
        bot_prefix = new_prefix
        self.bot.command_prefix(bot_prefix)
        await ctx.send("The bot prefix was changed to `" + bot_prefix + "`")
        await self.bot.change_presence(activity=discord.Game(name='Type `' + bot_prefix + 'help` to get started!'))


# ACK: User-made gist: https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5
def setup(bot):
    bot.add_cog(AdminCog(bot))
