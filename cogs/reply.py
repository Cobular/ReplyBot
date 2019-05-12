"""A Cog that controls the search and reply functionality of the bot.

Also is responsible for saving messages sent to the bot
"""

import datetime
import logging
import typing

import discord
from discord.ext import commands
from discord.ext.commands.context import Context

from models import Message, make_session, TempMessage
from tools import methods, elastisearch


def split_message(user_input: str):
    """Splits up the inserted text on the :wavy-dash: character"""
    # noinspection PyBroadException
    try:
        search_terms, response = user_input.split("〰", 1)
        logging.info(search_terms + "::" + response)
        search_terms = search_terms.strip()
        response = response.strip()
    except:
        search_terms = user_input.strip()
        response = None
        logging.info(search_terms + "::nothing")
    return search_terms, response


async def get_message(ctx, message_id: int):
    """Gets the message from an ID"""
    message = await ctx.fetch_message(message_id)
    return message


async def database_search(ctx: Context, channel: typing.Optional[discord.TextChannel],
                          target_user: typing.Optional[discord.Member], search_terms: str) -> typing.Optional[
                          discord.Message]:
    """Searches through the database for the search for the requested message.

    :param ctx: The Context of the message
    :param channel: The channel that the desired message is in. Is optional
    :param target_user: The user that sent the desired message. Is optional
    :param search_terms: The main text that the user is searching for
    :return message: The message found. Returns None if no message is found
    """
    if channel is None:
        channel = ctx.message.channel
    rsp = elastisearch.test_search_2(search_terms, ctx.guild.id, channel.id, target_user)
    if rsp["hits"]["hits"].__len__() == 0:
        final_rsp = None
    else:
        final_rsp = await ctx.fetch_message(rsp["hits"]["hits"][0]["_source"]["message_id"])
    return final_rsp


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
        self.bot: commands.Bot = bot

    @commands.command(usage="[<channel> <target_user>] <search term> [〰 <response>]")
    async def reply(self, ctx: Context, channel: typing.Optional[discord.TextChannel],
                    target_user: typing.Optional[discord.Member], *, user_input: str):
        """ Searches the past messages in a server for the text after the command.

        Place a 〰 (:wavy-dash:) between your search string and your response to activate the response functionality.

        channel: (Optional) The #channel_name for a text channel. Will only search in that channel.
        user: (Optional) The @user_name for a user. Will only search for that user.
        search term: (Required) The part of a message to search for.
        response: (Optional) Your response to append to the end of the message. Make sure to add the 〰 to delineate.
        """
        search_terms, response = split_message(user_input)

        new_message = await database_search(ctx, channel, target_user, search_terms)

        # Catch the failure to find a message before other things are requested of new_message, avoiding null references
        if not new_message:
            print("Sending Message...")
            await ctx.send("Failed to find the requested message! Please try again with less specific search terms. "
                           "\nYou may also not be able to view the channel that the message was from.")
            print("Message Sent!")
            return

        # Had issues getting the children of new_message, this reduced them
        new_message_content = new_message.clean_content
        new_message_sender_id = new_message.author.id
        new_message_channel_id = new_message.channel.id
        new_message_sent_time = new_message.created_at
        new_message_id = new_message.id

        await self.send_response(ctx, response, channel, new_message_content, new_message_sender_id,
                                 new_message_channel_id, new_message_sent_time, new_message_id)

    async def send_response(self, ctx: Context, response: str, channel: discord.TextChannel, original_content: str,
                            original_sender_id: int, original_channel_id: int, original_sent_time: datetime.datetime,
                            original_message_id: int):
        """Checks that the requester has the read_messages permission on the requested channel.

        If so, sends message. If not, sends error to the user
        """
        # Checks to make sure the requester has perms to see the channel the message is in
        if ctx.message.author.permissions_in(self.bot.get_channel(original_channel_id)).read_messages:
            logging.debug(methods.clean_string_light(original_content))
            if response is not None:  # Check to see if the message has an attached response
                if channel is not None and channel.id != original_channel_id:
                    # Print with channel name included if pulled from another channel
                    await send_original_message(ctx, original_content, original_sender_id, original_sent_time,
                                                original_message_id)
                    await ctx.send("To which " + ctx.message.author.mention + " says:")
                    await send_original_message_no_channel(ctx, response, ctx.message.author.id,
                                                           datetime.datetime.utcnow(), ctx.message.id)
                else:  # Print normally with a response
                    await send_original_message_no_channel(ctx, original_content, original_sender_id,
                                                           original_sent_time, original_message_id)
                    await ctx.send("To which " + ctx.message.author.mention + " says:")
                    await send_original_message_no_channel(ctx, response, ctx.message.author.id,
                                                           datetime.datetime.utcnow(), ctx.message.id)
            else:
                await send_original_message_no_channel(ctx, original_content, original_sender_id,
                                                       original_sent_time, original_message_id)
        else:
            logging.info("User had insufficient permissions to access that text")
            await ctx.send("Failed to find the requested message! Please try again with less specific search terms. "
                           "\nYou may also not be able to view the channel that the message was from.")

    # -----------------------------------------------------------------------------------------------------------------

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
        if message.content.startswith("〰"):
            await self.reacted_message_response(message)
            skip_saving = True
        if not skip_saving:
            if message.clean_content != '':
                current_message = elastisearch.TestMessageDoc(message_content=message.clean_content,
                                                              message_sender=message.author.id,
                                                              message_channel=message.channel.id,
                                                              message_server=message.guild.id,
                                                              message_id=message.id,
                                                              message_sent_time=datetime.datetime.now())
                print(current_message.save())
            logging.info("Another Message Saved!")  # For metric tracking

    @commands.Cog.listener("on_message_delete")
    async def respect_deletions(self, message):
        session = make_session()
        deleted_message = session.query(Message).filter(Message.message_id == message.id).first()
        if deleted_message is not None:
            session.delete(deleted_message)
            session.commit()
        session.close()

    @commands.Cog.listener("on_message_edit")
    async def respect_edits(self, before: discord.Message, after: discord.Message):
        session = make_session()
        old_message: Message = session.query(Message).filter(Message.message_id == before.id).first()
        if old_message is not None:
            old_message.message_content = after.clean_content
            session.commit()
        session.close()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Checks to see if the reaction added is the '〰' emoji. If so, save the message from the db"""
        if payload.emoji.name == '〰':
            channel: discord.TextChannel = self.bot.get_channel(payload.channel_id)
            message: discord.message = await channel.fetch_message(payload.message_id)
            session = make_session()
            new_temp_message = TempMessage(message_id=message.id, message_sender=message.author.id,
                                           message_channel=message.channel.id, message_server=message.guild.id,
                                           message_reactor_id=payload.user_id)
            session.add(new_temp_message)
            session.commit()
            session.close()
            TempMessage.prune_db(1)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Checks to see if the reaction removed is the '〰' emoji. If so, remove the message from the db"""
        if payload.emoji.name == '〰':
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            session = make_session()
            new_temp_message = session.query(TempMessage).filter_by(message_id=message.id,
                                                                    message_server=message.guild.id,
                                                                    message_reactor_id=payload.user_id).first()
            if new_temp_message is not None:
                session.delete(new_temp_message)
            session.commit()
            session.close()

    async def reacted_message_response(self, message: discord.Message):
        session = make_session()
        original_message: TempMessage = session.query(TempMessage).filter(
            TempMessage.message_reactor_id == message.author.id).order_by(TempMessage.message_sent_time.desc()).first()
        if original_message is None:
            return
        elif original_message.message_sent_time >= datetime.datetime.now() - datetime.timedelta(minutes=5):
            request_ctx = await self.bot.get_context(message)
            original_message_data: discord.Message = await get_message(request_ctx, original_message.message_id)
            junk, response_content = split_message(message.clean_content)
            await self.send_response(request_ctx, response_content, message.channel,
                                     original_message_data.clean_content,
                                     original_message_data.author.id, original_message_data.channel.id,
                                     original_message_data.created_at, original_message_data.id)
        TempMessage.prune_db(2)


def setup(bot):
    bot.add_cog(ReplyCog(bot))
