import discord
import random
import re
import os
import psycopg2
import logging
from discord.ext import commands

bot_prefix = "rsp!"
bot = commands.Bot(command_prefix=bot_prefix, command_not_found="Heck! That command doesn't exist!!")
logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

client = discord.Client()

def quote_selector(argument):
    switch = {
        1: "I sawed this boat in half!",
        2: "I sawed this boat in half!",
        3: "Hi, Phil Swift here for flex tape!",
        4: "Hi, Phil Swift here for flex tape!",
        5: "That\'s a lot of damage!",
        6: "That\'s a lot of damage!"}
    return switch.get(argument, "Invalid Quote Choice")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    me = message.server.me

    if message.author == client.user:
        return
    if re.search('flex', message.content, re.IGNORECASE):
        await client.change_nickname(me, 'Phil Swift') # Phil Swift Icon: https://i.imgur.com/TNiVQik.jpg
        print('flexy message recived')  # Debuging Stuff
        selector = random.randint(1,6)  # Randomly select a choice
        current_message = await  client.send_message(message.channel, quote_selector(selector), tts=True)  #Actually send the message
        await client.delete_message(current_message)  # Quiclky delete the message so it is more sneaky
        print(selector)  # Debuging Selection Choices
        await client.change_nickname(me, 'ReactionBot')  # Default Icon: https://i.imgur.com/NTHcYgR.jpg

    if re.search('flex tape', message.content, re.IGNORECASE):
        await client.add_reaction(message, '™')


    ### Cleaning messages at `message_limit` messages to avoid $$ issues
    message_limit = 2000
    cur = conn.cursor()
    cur.execute("""SELECT * FROM messages;""") # Get all the messages
    if cur.rowcount > message_limit:
        cur.execute("""SELECT MIN(id) FROM messages;""")
        lowest_id = cur.fetchone()
        print("Deleted message with id:")
        print(lowest_id)
        cur.execute("""DELETE FROM messages WHERE id = %s""", (lowest_id,))
        conn.commit()


    ### Checks for bot command starters and removes the bot part from the message content
    if message.clean_content.startswith(bot_prefix):
        command_content = re.sub(r"rsp!", "", message.clean_content)
        ### Runs the reply command. Lots of filtering, exlpained inlive
        if 'reply' in command_content:
            command_content = re.sub(r"reply ", "", command_content)  # Removes the command prefix `reply ` from the string
            print("Raw message: " + command_content)
            cur = conn.cursor()
            term = command_content.replace('=', '==').replace('%', '=%').replace('_', '=_')  # Redefines the characters that will cause issues (ones that need to be escaped) in other ways using the new escape character
            sql = """SELECT id FROM messages WHERE message_content LIKE %(content)s ESCAPE '=' LIMIT 1;"""  # Defines the query, specifically redefined the sql escape character as `=`. This resolves issues with the `\` as the escape character conflicting at different levels down the chain.
            cur.execute(sql, dict(content='%' + term + '%'))  # Actually runs the command
            output_message_id = cur.fetchone()
            print(output_message_id[0])
            conn.commit()

            # Does the responding to the message
            cur = conn.cursor()
            cur.execute("""SELECT username FROM messages WHERE id = %s;""", (output_message_id[0],))
            output_message_username = cur.fetchone()
            cur.execute("""SELECT message_content FROM messages WHERE id = %s;""", (output_message_id[0],))
            output_message_content = cur.fetchone()
            print(output_message_username)
            print(output_message_content)
            print(output_message_id)
            output_message_overall = output_message_username[0] + ": " + output_message_content[0]
            await client.send_message(message.channel, output_message_overall)
            conn.commit()


    ### Logging the messages to the database, moved to the bottom to avoid selecting the invocation message
    cur = conn.cursor()
    cur.execute("""INSERT INTO messages (username, message_content) VALUES (%s, %s);""",
                (message.author.mention, message.clean_content))
    conn.commit()


client.run("NDk0OTM2MDAwMzYwMDg3NTYz.Do6xPA.6cofu9CfSaKkhYJsa6TzJmrtOhk")
