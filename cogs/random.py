import discord
from discord.ext import commands
from discord.ext.commands import BucketType
from tools import methods


class RandomCog(commands.Cog, name="Random Commands"):
    """RandomCog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 60, BucketType.user)
    async def invite(self, ctx):
        """ Displays the link to invite the bot to a server.

        """

        await ctx.send("Here, have an invite! Click this to add ReplyBot to your server! \n"
                       "https://discordapp.com/oauth2/authorize?client_id=494936000360087563&scope=bot&permissions=201620576")
        await methods.delete_invocation(ctx)


def setup(bot):
    bot.add_cog(RandomCog(bot))
