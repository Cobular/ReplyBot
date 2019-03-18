"""A Cog that controls the search and reply functionality of the bot.

Also is responsible for saving messages sent to the bot
"""

import discord
from discord.ext import commands
from sqlalchemy import func
from models import Message, make_session
from tools import methods
import typing
import datetime


class ReplyCog(commands.Cog, name="Reply Commands"):
    """ReplyCog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="[<channel> <target_user>] <search term> [〰 <response>]")
    async def reply(self, ctx, channel: typing.Optional[discord.TextChannel],
                    target_user: typing.Optional[discord.Member], *, user_input):
        """ Searches the past messages in a server for the text after the command.

        Place a 〰 (:wavy-dash:) between your search string and your response to activate the response functionality.

        channel: (Optional) The #channel_name for a text channel. Will only search in that channel.
        user: (Optional) The @user_name for a user. Will only search for that user.
        search term: (Required) The part of a message to search for.
        response: (Optional) Your response to append to the end of the message. Make sure to add the 〰 to deliniate.
        """
        # Created the database session for this run
        session = make_session()
        # Null Check is used to tell if a hit was found must be initialized here
        new_message = None
        try:
            search_terms, response = user_input.split("〰", 1)
            print(search_terms + "::" + response)
        except:
            search_terms = user_input
            response = None
            print(search_terms + ":: nothing")

        if channel is not None and target_user is not None:
            if search_terms != "":
                new_message = session.query(Message
                                            # func.lower() insures that case isn't an issue
                                            ).filter(
                    func.lower(Message.message_content).contains(func.lower(search_terms)),
                    Message.message_channel == channel.id,
                    Message.message_sender == target_user.id,
                    Message.message_server == ctx.guild.id
                    ).order_by(Message.message_sent_time.desc()).first()
            else:
                new_message = session.query(Message
                                            ).filter(Message.message_channel == channel.id,
                                                     Message.message_sender == target_user.id,
                                                     Message.message_server == ctx.guild.id
                                                     ).order_by(Message.message_sent_time.desc()).first()
        elif channel is not None:
            if search_terms != "":
                new_message = session.query(Message
                                            ).filter(
                    func.lower(Message.message_content).contains(func.lower(search_terms)),
                    Message.message_channel == channel.id,
                    Message.message_server == ctx.guild.id
                    ).order_by(Message.message_sent_time.desc()).first()
            else:
                new_message = session.query(Message
                                            ).filter(Message.message_channel == channel.id,
                                                     Message.message_server == ctx.guild.id
                                                     ).order_by(Message.message_sent_time.desc()).first()
        elif target_user is not None:
            if search_terms != "":
                new_message = session.query(Message
                                            ).filter(
                    func.lower(Message.message_content).contains(func.lower(search_terms)),
                    Message.message_sender == target_user.id,
                    Message.message_server == ctx.guild.id
                    ).order_by(Message.message_sent_time.desc()).first()
            else:
                new_message = session.query(Message
                                            ).filter(Message.message_sender == target_user.id,
                                                     Message.message_server == ctx.guild.id
                                                     ).order_by(Message.message_sent_time.desc()).first()
        else:
            if search_terms != '':
                new_message = session.query(Message
                                            ).filter(
                    func.lower(Message.message_content).contains(func.lower(search_terms)),
                    Message.message_server == ctx.guild.id
                    ).order_by(Message.message_sent_time.desc()).first()
            else:
                new_message = session.query(Message
                                            ).filter(Message.message_server == ctx.guild.id
                                                     ).order_by(Message.message_sent_time.desc()).first()

        # Catch the failure to find a message before other things are requested of new_message, avoiding null refrences
        if not new_message:
            await ctx.send("Failed to find the requested message! Please try again with less specific search terms. "
                           "\nYou may also not be able to view the channel that the message was from.")
            return

            # Now tries to send the response
        # Had issues getting the children of new_message, this reduced them
        new_message_content = new_message.message_content
        new_message_sender_id = new_message.message_sender
        new_message_channel = new_message.message_channel
        new_message_sent_time = new_message.message_sent_time

        # Checks that the requester has the read_messages permission on the requested channel.
        # If so, sends message. If not, returns error to the user
        if ctx.message.author.permissions_in(self.bot.get_channel(new_message_channel)).read_messages:
            print(methods.clean_string_light(new_message_content))
            if response is not None:  # Check to see if the message has an attached response
                if channel is not None and channel.id != new_message_channel:  # Print with channel name included if pulled from another channel
                    await ctx.send("<@" + str(new_message_sender_id) + "> *said* `" +
                                   methods.clean_string_light(new_message_content) + "` in" + channel.mention + "\n" +
                                   "`" + response + "` *responds* " + ctx.message.author.mention)
                else:  # Print normally with a response
                    await ctx.send("<@" + str(new_message_sender_id) + "> *said* `" +
                                   methods.clean_string_light(new_message_content) + "` \n" +
                                   "`" + response + "` *responds* " + ctx.message.author.mention)
            else:
                await self.send_original_message(ctx, new_message_content, new_message_sender_id, new_message_sent_time)
        else:
            print("User had insufficient permissions to access that text")
            await ctx.send("Failed to find the requested message! Please try again with less specific search terms. "
                           "\nYou may also not be able to view the channel that the message was from.")

        # Keeps database connections clean
        session.close()
        await methods.delete_invocation(ctx)

    @commands.Cog.listener()
    async def on_message(self, message):
        skip_saving = False

        if message.author == self.bot.user:
            skip_saving = True
        if 'r!' in message.content:
            skip_saving = True

        if not skip_saving:
            session = make_session()
            if message.clean_content != '':
                current_message = Message(message_content=message.clean_content, message_sender=message.author.id,
                                          message_channel=message.channel.id, message_server=message.guild.id,
                                          message_id=message.id)
                session.add(current_message)
            session.commit()
            session.close()
            Message.prune_db(2000)

    async def send_original_message(self, ctx, message_content, message_sender, message_sent_time):
        sender = ctx.guild.get_member(message_sender)
        embed = discord.Embed(colour=sender.color,
                              description=message_content,
                              timestamp=message_sent_time)
        embed.set_author(name=sender.display_name, icon_url=sender.avatar_url)
        embed.set_footer(text="ReplyBot", icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ReplyCog(bot))
