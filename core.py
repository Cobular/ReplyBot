import discord
import random
import re
import os
import psycopg2
import logging
from discord.ext import commands
import methods
from threading import Thread
import time
import typing


bot_prefix = "%"
bot = commands.Bot(command_prefix=bot_prefix, command_not_found="Heck! That command doesn't exist!!")
logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.environ['DATABASE_URL']
BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_STATE = os.environ['BOT_STATE']
# Bot connection URL: https://discordapp.com/oauth2/authorize?client_id=494936000360087563&scope=bot&permissions=201620576
# Staging Bot COnnection URL: https://discordapp.com/oauth2/authorize?client_id=499998765273448478&scope=bot&permissions=201620576

# conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# client = discord.Client()


# @client.event
# async def on_ready():
#     for i in client.servers:
#         print('We have logged in as {0.user}'.format(client))
#         if BOT_STATE == "PRODUCTION":
#             await client.change_nickname(i.me, "ReactionBot")
#             print("Setting Nicname to prouction one")
#         elif BOT_STATE == "STAGING":
#             await client.change_nickname(i.me, "ReactionBot_Staging")
#             print("Settimg Nicname to procuction one")
#         else:
#             logging.error("Couldn't Find BOT_STATE!! Defaulting to ReactionBot")
#             await client.change_nickname(i.me, "ReactionBot")
#         await client.change_presence(game=discord.Game(name='Type `rsp!help` to get started!'))


# @client.event
# async def on_message(message):
#     me = message.server.me
#
#     # <editor-fold desc="FlexBot Shit">
#     if message.author == client.user:
#         return
#     if re.search('flex', message.content, re.IGNORECASE):
#         await client.change_nickname(me, 'Phil Swift')  # Phil Swift Icon: https://i.imgur.com/TNiVQik.jpg
#         print('flexy message recived')  # Debuging Stuff
#         current_message = await client.send_message(message.channel, methods.quote_selector(), tts=True)  # Actually send the message
#         await client.delete_message(current_message)  # Quiclky delete the message so it is more sneaky
#         await client.change_nickname(me, 'ReactionBot')  # Default Icon: https://i.imgur.com/NTHcYgR.jpg
#
#     if re.search('flex tape', message.content, re.IGNORECASE):
#         await client.add_reaction(message, '™')
#     # </editor-fold>
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
#         # <editor-fold desc="Help Command">
#         if command_content.startswith('help'):
#             command_content = re.sub(r"help ", "", command_content)  # Removes the command prefix `reply ` from the string
#             print("Print command processed. Raw message: " + command_content)
#             await client.send_message(message.channel, "**Command Root:** `rsp!` " + os.linesep +
#                                       "**Commands:** " + os.linesep +
#                                       "`rsp!reply search-term`- Searches the last 2000 messages for the search term then sends that in the channel of the invocation message.")
#             return
#         # </editor-fold>
#
#     # Logging the messages to the database, moved to the bottom to avoid selecting the invocation message
#     cur = conn.cursor()
#     cur.execute("""INSERT INTO messages (username, message_content, server_id, channel_id, sending_user_id)
#                 VALUES (%s, %s, %s, %s, %s);""",
#                 (message.author.mention, message.clean_content, message.server.id, message.channel.id,
#                  message.author.id))
#     conn.commit()


@bot.command()
async def reply_bot(ctx, channel: typing.Optional[discord.Channel] = None, user: typing.Optional[discord.Member] = None, *, search_terms):
    await ctx.send(search_terms)
    print(user)


bot.run(BOT_TOKEN)
