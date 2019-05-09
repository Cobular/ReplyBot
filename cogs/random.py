"""Just random fun stuff. Nothing essential to the bot will be put here"""

import re

# noinspection PyPackageRequirements
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
                       "https://discordapp.com/oauth2/authorize?client_id="
                       "494936000360087563&scope=bot&permissions=201620576")
        await ctx.message.delete()

    # Responsible for the flex-tape easter egg.
    # TODO: Add a toggle command to enable or disable the egg
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        me = message.guild.me

        if message.author == self.bot.user:
            return
        if re.search("flex", message.content, re.IGNORECASE):
            original_nick = me.nick
            await me.edit(nick='Phil Swift')  # Phil Swift Icon: https://i.imgur.com/TNiVQik.jpg
            print('flexy message received')  # Debugging Stuff
            current_message = await message.channel.send(methods.quote_selector(),
                                                         tts=True)  # Actually send the message
            await current_message.delete()  # Quickly delete the message so it is more sneaky
            await me.edit(nick=original_nick)  # Default Icon: https://i.imgur.com/NTHcYgR.jpg
        if re.search("flex tape", message.content, re.IGNORECASE):
            await message.add_reaction('™')

    @commands.command()
    async def info(self, ctx):
        await ctx.send("This is ReplyBot, replying for Gamers!\n"
                       "Developed and maintained by <@249705405372956672>. "
                       "See `r!help` for more information aBout the bot's functionality.")


def setup(bot):
    bot.add_cog(RandomCog(bot))
