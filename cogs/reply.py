"""A Cog that controls the search and reply functionality of the bot.

Also is responsible for saving messages sent to the bot
"""

import typing
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from sqlalchemy import func

import logging
from models import Message, make_session
from tools import methods


def split_message(user_input):
    """Splits up the inserted text on the :wavy-dash: character"""
    # noinspection PyBroadException
    try:
        search_terms, response = user_input.split("〰", 1)
        logging.debug(search_terms + "::" + response)
    except:
        search_terms = user_input
        response = None
        logging.debug(search_terms + "::nothing")
    return search_terms, response


async def get_message(ctx, message_id: int):
    """Gets the message from an ID"""
    message = await ctx.get_message(message_id)
    return message


def database_search(ctx: Context, channel: typing.Optional[discord.TextChannel],
                    target_user: typing.Optional[discord.Member], search_terms: str) -> discord.message.Message:
    """Searches through the database for the search for the requested message.

    :param ctx: The Context of the message
    :param channel: The channel that the desired message is in. Is optional
    :param target_user: The user that sent the desired message. Is optional
    :param search_terms: The main text that the user is searching for
    :return message: The message found. Returns None if no message is found
    """
    session = make_session()
    new_message = None

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

    session.close()
    return new_message


async def send_original_message_no_channel(ctx, message_content, message_sender, message_sent_time,
                                           message_id):
    """Sends a message as an embed, doesn't include the channel it was sent from"""
    sender = ctx.guild.get_member(message_sender)
    message = await get_message(ctx, message_id)
    embed = discord.Embed(colour=sender.color, description="**" + message_content + "**",
                          timestamp=message_sent_time)
    embed.set_author(name=sender.display_name, icon_url=sender.avatar_url,
                     url=message.jump_url)
    # embed.set_footer(text="ReplyBot", icon_url=self.bot.user.avatar_url)

    await ctx.send(embed=embed)


async def send_original_message(ctx, message_content, message_sender, message_sent_time,
                                message_id):
    """Sends a message as an embed, includes the channel it was sent from"""
    sender = ctx.guild.get_member(message_sender)
    message = await get_message(ctx, message_id)
    embed = discord.Embed(colour=sender.color, description="**" + message_content + "**",
                          timestamp=message_sent_time)
    embed.set_author(name=sender.display_name, icon_url=sender.avatar_url,
                     url=message.jump_url)
    embed.add_field(name="‍ ", value="*Sent in: " + message.channel.mention + "*")
    # embed.set_footer(text="ReplyBot", icon_url=self.bot.user.avatar_url)

    await ctx.send(embed=embed)


class ReplyCog(commands.Cog, name="Reply Commands"):
    """ReplyCog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="[<channel> <target_user>] <search term> [〰 <response>]")
    async def reply(self, ctx: Context, channel: typing.Optional[discord.TextChannel],
                    target_user: typing.Optional[discord.Member], *, user_input):
        """ Searches the past messages in a server for the text after the command.

        Place a 〰 (:wavy-dash:) between your search string and your response to activate the response functionality.

        channel: (Optional) The #channel_name for a text channel. Will only search in that channel.
        user: (Optional) The @user_name for a user. Will only search for that user.
        search term: (Required) The part of a message to search for.
        response: (Optional) Your response to append to the end of the message. Make sure to add the 〰 to deliniate.
        """
        # Null Check is used to tell if a hit was found must be initialized here
        new_message: Message = None

        search_terms, response = split_message(user_input)

        new_message = database_search(ctx, channel, target_user, search_terms)

        # Catch the failure to find a message before other things are requested of new_message, avoiding null refrences
        if not new_message:
            await ctx.send("Failed to find the requested message! Please try again with less specific search terms. "
                           "\nYou may also not be able to view the channel that the message was from.")
            return

        # Had issues getting the children of new_message, this reduced them
        new_message_content = new_message.message_content
        new_message_sender_id = new_message.message_sender
        new_message_channel_id = new_message.message_channel
        new_message_sent_time = new_message.message_sent_time
        new_message_id = new_message.message_id

        await self.send_response(ctx, response, channel, new_message_content, new_message_sender_id,
                                 new_message_channel_id, new_message_sent_time, new_message_id)

        await methods.delete_invocation(ctx)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Saves a message sent on a server the bot is in.

        Will not save if it is a command for this bot or if the message is from this bot
        """
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
            Message.prune_db(50000)

    async def send_response(self, ctx: Context, response, channel, original_content, original_sender_id,
                            original_channel_id, original_sent_time, original_message_id):
        """Checks that the requester has the read_messages permission on the requested channel.

        If so, sends message. If not, sends error to the user
        """
        # For unit testing

        # Checks to make sure the requester has perms to see the channel the message is in
        if ctx.message.author.permissions_in(self.bot.get_channel(original_channel_id)).read_messages:
            logging.debug(methods.clean_string_light(original_content))
            if response is not None:  # Check to see if the message has an attached response
                if channel is not None and channel.id != original_channel_id:  # Print with channel name included if pulled from another channel
                    await send_original_message(ctx, original_content, original_sender_id, original_sent_time,
                                                     original_message_id)
                    await ctx.send("To which " + ctx.message.author.mention + " says:")
                    await send_original_message_no_channel(ctx, response, ctx.message.author.id,
                                                                datetime.utcnow(), ctx.message.id)
                else:  # Print normally with a response
                    await send_original_message_no_channel(ctx, original_content, original_sender_id,
                                                                original_sent_time, original_message_id)
                    await ctx.send("To which " + ctx.message.author.mention + " says:")
                    await send_original_message_no_channel(ctx, response, ctx.message.author.id,
                                                                datetime.utcnow(), ctx.message.id)
            else:
                await send_original_message_no_channel(ctx, original_content, original_sender_id,
                                                            original_sent_time, original_message_id)
        else:
            logging.info("User had insufficient permissions to access that text")
            await ctx.send("Failed to find the requested message! Please try again with less specific search terms. "
                           "\nYou may also not be able to view the channel that the message was from.")


def setup(bot):
    bot.add_cog(ReplyCog(bot))
