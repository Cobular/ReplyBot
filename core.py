import discord
import random
import re

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if re.search('flex', message.content, re.IGNORECASE):
        print('flexy message recived')
        selector = random.randint(1,10)
        if selector <= 4:
            current_message = await client.send_message(message.channel, 'I sawed this boat in half!', tts=True)
        if selector > 4 & selector < 6:
            current_message = await client.send_message(message.channel, 'Hi, Phil Swift here for flex tape!', tts=True)
        if selector <= 6:
            current_message = await client.send_message(message.channel, 'That\'s a lot of damage!', tts=True)
        await client.delete_message(current_message)

    if re.search('flex tape', message.content, re.IGNORECASE):
        await client.add_reaction(message, '™')


client.run("NDk0OTM2MDAwMzYwMDg3NTYz.Do6xPA.6cofu9CfSaKkhYJsa6TzJmrtOhk")
