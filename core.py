import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import re
import os
import logging
import methods
import typing
from models import Message, make_session
from sqlalchemy import func

long_help_formatter = commands.HelpFormatter(False, False, 100)
bot = commands.Bot(command_prefix='r!', command_not_found="Heck! That command doesn't exist!!",
                   formatter=long_help_formatter, description="Thanks for using ReplyBot, Replying for Gamers!")
logging.basicConfig(level=logging.INFO)
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_STATE = os.environ['BOT_STATE']


# Bot connection URL: https://discordapp.com/oauth2/authorize?client_id=494936000360087563&scope=bot&permissions=201620576
# Staging Bot Connection URL: https://discordapp.com/oauth2/authorize?client_id=499998765273448478&scope=bot&permissions=201620576


@bot.event
async def on_ready():
    for i in bot.guilds:
        print('We have logged in as {0.user}'.format(bot))
        if BOT_STATE == "PRODUCTION":
            await i.me.edit(nick="ReactionBot")
            print("Setting Nickname to production one")
        elif BOT_STATE == "STAGING":
            await i.me.edit(nick="ReactionBot_Staging")
            print("Setting Nickname to staging one")
            print(methods.get_prefix(i.id))
            print(i.id)
        else:
            logging.error("Couldn't Find BOT_STATE!! Defaulting to ReactionBot")
        await bot.change_presence(activity=discord.Game(name='Type r!help to get started!'))
        await bot.change_presence(activity=discord.Game(name='Type `' +
                                                             methods.get_prefix(i.id) + 'help` to get started!'))


@bot.event
async def on_guild_join(guild):
    print('We have logged in as {0.user}'.format(bot))
    if BOT_STATE == "PRODUCTION":
        await guild.me.edit(nick="ReactionBot")
        print("Setting Nickname to production one")
    elif BOT_STATE == "STAGING":
        await guild.me.edit(nick="ReactionBot_Staging")
        print("Setting Nickname to staging one")
        print(methods.get_prefix(guild.id))
        print(guild.id)
    else:
        logging.error("Couldn't Find BOT_STATE!! Defaulting to ReactionBot")
        await guild.me.edit(nick="ReactionBot")
    await bot.change_presence(activity=discord.Game(name='Type `' +
                                                         methods.get_prefix(guild.id) + 'help` to get started!'))


@bot.command(usage="[<channel> <target_user>] <search term> [〰 <response>]")
async def reply(ctx, channel: typing.Optional[discord.TextChannel], target_user: typing.Optional[discord.Member],
                *, user_input):
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
                                        ).filter(func.lower(Message.message_content).contains(func.lower(search_terms)),
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
                                        ).filter(func.lower(Message.message_content).contains(func.lower(search_terms)),
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
                                        ).filter(func.lower(Message.message_content).contains(func.lower(search_terms)),
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
                                        ).filter(func.lower(Message.message_content).contains(func.lower(search_terms)),
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

    # Checks that the requester has the read_messages permission on the requested channel.
    # If so, sends message. If not, returns error to the user
    if ctx.message.author.permissions_in(bot.get_channel(new_message_channel)).read_messages:
        print(methods.clean_string_light(new_message_content))
        if response is not None:
            if channel is not None and channel.id != new_message_channel:
                await ctx.send("<@" + str(new_message_sender_id) + "> *said* `" +
                               methods.clean_string_light(new_message_content) + "` in" + channel.mention + "\n" +
                               "`" + response + "` *responds* " + ctx.message.author.mention)
            else:
                await ctx.send("<@" + str(new_message_sender_id) + "> *said* `" +
                               methods.clean_string_light(new_message_content) + "` \n" +
                               "`" + response + "` *responds* " + ctx.message.author.mention)
        else:
            await ctx.send("<@" + str(new_message_sender_id) + "> *said* `" +
                           methods.clean_string_light(new_message_content) + "`")
    else:
        print("User had insuficent permissions to access that text")
        await ctx.send("Failed to find the requested message! Please try again with less specific search terms. "
                       "\nYou may also not be able to view the channel that the message was from.")

    # Keeps database connections clean
    session.close()
    await methods.delete_invocation(ctx)


@bot.command()
@commands.cooldown(1, 60, BucketType.user)
async def invite(ctx):
    """ Displays the link to invite the bot to a server.

    """
    await ctx.send("Here, have an invite! Click this to add ReplyBot to ypur server! \n"
                   "https://discordapp.com/oauth2/authorize?client_id=494936000360087563&scope=bot&permissions=201620576")
    await methods.delete_invocation(ctx)


@bot.command(hidden=True, name="prefix")
@commands.has_role('Mod')
async def change_prefix(ctx, *, message: str):
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
    if methods.get_prefix(message.guild.id) in message.content:
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
        if message.clean_content != '':
            current_message = Message(message_content=message.clean_content, message_sender=message.author.id,
                                      message_channel=message.channel.id, message_server=message.guild.id)
            session.add(current_message)
        session.commit()
        session.close()
        Message.prune_db(2000)

    # Insures the other commands are still processed
    await bot.process_commands(message)

bot.run(BOT_TOKEN)
