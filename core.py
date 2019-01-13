import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import re
import os
import logging
import methods
import typing
from models import Message, make_session

bot_prefix = "r!"
long_help_formatter = commands.HelpFormatter(False, False, 100)
bot = commands.Bot(command_prefix=bot_prefix, command_not_found="Heck! That command doesn't exist!!",
                   formatter=long_help_formatter)
logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_STATE = os.environ['BOT_STATE']


# Bot connection URL: https://discordapp.com/oauth2/authorize?client_id=494936000360087563&scope=bot&permissions=201620576
# Staging Bot Connection URL: https://discordapp.com/oauth2/authorize?client_id=499998765273448478&scope=bot&permissions=201620576

#     methods.clean_database(2000, conn)  # Cleans up the database to keep it at 2000 lines


@bot.event
async def on_ready():
    for i in bot.guilds:
        print('We have logged in as {0.user}'.format(bot))
        if BOT_STATE == "PRODUCTION":
            await i.me.edit(nick="ReactionBot")
            print("Setting Nickname to production one")
        elif BOT_STATE == "STAGING":
            await i.me.edit(nick="ReactionBot_Staging")
            print("Setting Nickname to production one")
        else:
            logging.error("Couldn't Find BOT_STATE!! Defaulting to ReactionBot")
            await i.me.edit(nick="ReactionBot")
        await bot.change_presence(activity=discord.Game(name='Type `' + bot_prefix + 'help` to get started!'))


@bot.command()
async def reply(ctx, channel: typing.Optional[discord.TextChannel], target_user: typing.Optional[discord.Member],
                *, search_terms):
    """ Searches the past messages in a server for the text after the command.

    channel: (Optional) The #channel_name for a text channel. Will only search in that channel.
    user: (Optional) The @user_name for a user. Will only search for that user.
    search_terms: (Required) The part of a message to search for.
    """
    session = make_session()
    new_message = None

    if channel is not None and target_user is not None:
        new_message = session.query(Message
                                    ).filter(Message.message_content.contains(search_terms),
                                             Message.message_channel == channel.id,
                                             Message.message_sender == target_user.id,
                                             Message.message_server == ctx.guild.id
                                             ).order_by(Message.message_sent_time.desc()).first()
    elif channel is not None:
        new_message = session.query(Message
                                    ).filter(Message.message_content.contains(search_terms),
                                             Message.message_channel == channel.id,
                                             Message.message_server == ctx.guild.id
                                             ).order_by(Message.message_sent_time.desc()).first()
    elif target_user is not None:
        new_message = session.query(Message
                                    ).filter(Message.message_content.contains(search_terms),
                                             Message.message_sender == target_user.id,
                                             Message.message_server == ctx.guild.id
                                             ).order_by(Message.message_sent_time.desc()).first()
    else:
        new_message = session.query(Message
                                    ).filter(Message.message_content.contains(search_terms),
                                             Message.message_server == ctx.guild.id
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

    # Prints the response for debugging. TODO: Remove this debug print
    print("<@" + str(new_message_sender_id) + "> >> `" + new_message_content + "`")

    # Checks that the requester has the read_messages permission on the requested channel. If so, sends message. If not, returns error to the user
    if ctx.message.author.permissions_in(bot.get_channel(new_message_channel)).read_messages:
        await ctx.send("<@" + str(new_message_sender_id) + "> >> `" + new_message_content + "`")
    else:
        await ctx.send("Failed to find the requested message! Please try again with less specific search terms. "
                       "\nYou may also not be able to view the channel that the message was from.")

    # Keeps database connections clean
    session.close()


@bot.command()
@commands.cooldown(1, 60, BucketType.user)
async def invite(ctx):
    """ Creates an invite to the server

    Can be used once per 60 seconds per user
    Lasts for 2 minutes and will allow 4 people to join (enough to add everyone else in your party)
    Your username will be logged on creation, please don'r abuse this
    """
    new_invite = await ctx.message.channel.create_invite(max_age=120, max_uses=4, temporary=True, unique=False,
                                                         reason="Auto-generated by the bot for user: " + ctx.message.author.nick)
    await ctx.send(new_invite)


@bot.command(hidden=True)
@commands.has_role('Mod')
async def prefix(ctx, *, message: str):
    """ Changes the prefix used to call the bot. Only usable mod role. Currently broken

    Default prefix is r!
    Literally requires a role with name 'Mod' to use
    """
    global bot_prefix
    bot_prefix = message
    bot.command_prefix(bot_prefix)
    await ctx.send("The bot prefix was changed to `" + bot_prefix + "`")
    await bot.change_presence(activity=discord.Game(name='Type `' + bot_prefix + 'help` to get started!'))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('That command doesn\'t seem to exist! Please try again, and type `' + bot_prefix +
                       'help` to view the help documentation.')


@bot.event
async def on_message(message):
    global bot_prefix
    skip_saving = False
    me = message.guild.me
    original_nick = me.nick

    if message.author == bot.user:
        skip_saving = True
    if bot_prefix in message.content:
        skip_saving = True
    if re.search("flex", message.content, re.IGNORECASE):
        await me.edit(nick='Phil Swift')  # Phil Swift Icon: https://i.imgur.com/TNiVQik.jpg
        print('flexy message recived')  # Debuging Stuff
        current_message = await message.channel.send(methods.quote_selector(), tts=True)  # Actually send the message
        await current_message.delete()  # Quickly delete the message so it is more sneaky
        await me.edit(nick=original_nick)  # Default Icon: https://i.imgur.com/NTHcYgR.jpg
    if re.search("flex tape", message.content, re.IGNORECASE):
        await message.add_reaction('™')

    if not skip_saving:
        session = make_session()
        current_message = Message(message_content=message.clean_content, message_sender=message.author.id,
                                  message_channel=message.channel.id, message_server=message.guild.id)
        session.add(current_message)
        session.commit()
        session.close()

    # Insures the other commands are still processed
    await bot.process_commands(message)


bot.run(BOT_TOKEN)
