import discord
import random
import re
import os
import psycopg2

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
    if message.author == client.user:
        return
    if re.search('flex', message.content, re.IGNORECASE):
        print('flexy message recived')  # Debuging Stuff
        selector = random.randint(1,6)  # Randomly select a choice
        current_message = await  client.send_message(message.channel, quote_selector(selector), tts=True)  #Actually send the message
        await client.delete_message(current_message)  # Quiclky delete the message so it is more sneaky
        print(selector)  # Debuging Selection Choices

    if re.search('flex tape', message.content, re.IGNORECASE):
        await client.add_reaction(message, '™')

    # Logging the messages to the database
    cur = conn.cursor()
    cur.execute("""INSERT INTO messages (username, message_content) VALUES (%s, %s);""",
                (message.author.nick, message.clean_content))
    conn.commit()

    # Cleaning messages at `message_limit` messages
    message_limit = 2000
    cur = conn.cursor()
    cur.execute("""SELECT * FROM messages;""") # Get all the messages
    if cur.rowcount > message_limit:
        cur.execute("""SELECT MIN(id) FROM messages;""")
        lowest_id = cur.fetchone()
        print("Number of lowest ID:" + lowest_id)
        cur.execute("""DELETE FROM messages WHERE id = %s""", (lowest_id,))



client.run("NDk0OTM2MDAwMzYwMDg3NTYz.Do6xPA.6cofu9CfSaKkhYJsa6TzJmrtOhk")
