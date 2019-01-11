import discord
from discord.ext import commands
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
logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.environ['DATABASE_URL']
BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_STATE = os.environ['BOT_STATE']
# Bot connection URL: https://discordapp.com/oauth2/authorize?client_id=494936000360087563&scope=bot&permissions=201620576
# Staging Bot Connection URL: https://discordapp.com/oauth2/authorize?client_id=499998765273448478&scope=bot&permissions=201620576


# @client.event
# async def on_message(message):
#     me = message.server.me
#
#     methods.clean_database(2000, conn)  # Cleans up the database to keep it at 2000 lines
#
#     # Checks for bot command starters and removes the bot part from the message content
#     if message.clean_content.startswith(bot_prefix):
#         command_content = re.sub(r"rsp!", "", message.clean_content)
#
#         # Runs the reply command. Lots of filtering, exlpained inline
#         if command_content.startswith('reply'):
#             command_content = re.sub(r"reply ", "", command_content)  # Removes the command prefix `reply ` from the string
#             print("Reply command processed. Raw message: " + command_content)
#             cur = conn.cursor()
#             term = command_content.replace('=', '==').replace('%', '=%').replace('_', '=_')  # Redefines the characters that will cause issues (ones that need to be escaped) in other ways using the new escape character
#             sql = """SELECT id FROM messages WHERE message_content ILIKE %(content)s ESCAPE '=' LIMIT 1;"""  # Defines the query, specifically redefined the sql escape character as `=`. This resolves issues with the `\` as the escape character conflicting at different levels down the chain.
#             cur.execute(sql, dict(content='%' + term + '%'))  # Actually runs the command
#             output_message_id = cur.fetchone()
#             conn.commit()
#
#             # Check if there is no id found
#             if output_message_id is None:
#                 print("Search returned Nothing")
#                 error_message = "The search returned nothing. Please try again with a less specific search or confirm that the search text matches the original"
#                 await client.send_message(message.channel, error_message)
#                 return
#             else:
#                 print(output_message_id[0])
#
#             # Does the responding to the message
#             cur = conn.cursor()
#             cur.execute("""SELECT username FROM messages WHERE id = %s;""", (output_message_id[0],))
#             output_message_username = cur.fetchone()
#             cur.execute("""SELECT message_content FROM messages WHERE id = %s;""", (output_message_id[0],))
#             output_message_content = cur.fetchone()
#             print(output_message_username)
#             print(output_message_content)
#             print(output_message_id)
#             await client.send_message(message.channel, output_message_username[0] + " `" + output_message_content[0] + "`")
#             conn.commit()
#             return
#
#
#     # Logging the messages to the database, moved to the bottom to avoid selecting the invocation message
#     cur = conn.cursor()
#     cur.execute("""INSERT INTO messages (username, message_content, server_id, channel_id, sending_user_id)
#                 VALUES (%s, %s, %s, %s, %s);""",
#                 (message.author.mention, message.clean_content, message.server.id, message.channel.id,
#                  message.author.id))
#     conn.commit()


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
async def reply(ctx, channel: typing.Optional[discord.TextChannel], user: typing.Optional[discord.Member],
                    *, search_terms):
    """ Searches the past messages in a server for the text after the command.

    channel: (Optional) The #channel_name for a text channel. Will only search in that channel.
    user: (Optional) The @user_name for a user. Will only search for that user.
    search_terms: (Required) The part of a message to search for.
    """
    print(search_terms + ":" + str(channel) + ":" + str(user))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('That command doesn\'t seem to exist! Please try again, and type `' + bot_prefix +
                       'help` to view the help documentation.')


@bot.event
async def on_message(message):
    global bot_prefix
    me = message.guild.me
    original_nick = me.nick
    print(bot_prefix)

    if message.author == bot.user:
        return
    if re.search("flex", message.content, re.IGNORECASE):
        await me.edit(nick='Phil Swift')  # Phil Swift Icon: https://i.imgur.com/TNiVQik.jpg
        print('flexy message recived')  # Debuging Stuff
        current_message = await message.channel.send(methods.quote_selector(), tts=True)  # Actually send the message
        await current_message.delete()  # Quickly delete the message so it is more sneaky
        await me.edit(nick=original_nick)  # Default Icon: https://i.imgur.com/NTHcYgR.jpg
    if re.search("flex tape", message.content, re.IGNORECASE):
        await message.add_reaction('™')

    session = make_session()
    current_message = Message(message_content=message.clean_content, message_sender=message.author.id,
                              message_channel=message.channel.id, message_server=message.guild.id)
    session.add(current_message)
    session.commit()
    session.close()

    # Insures the other commands are still processed
    await bot.process_commands(message)


bot.run(BOT_TOKEN)
