import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import re
import os
import logging
from tools import methods
from models import Message, make_session

long_help_formatter = commands.HelpFormatter(False, False, 100)
bot = commands.Bot(command_prefix='r!', command_not_found="Heck! That command doesn't exist!!",
                   formatter=long_help_formatter, description="Thanks for using ReplyBot, Replying for Gamers!")
logging.basicConfig(level=logging.INFO)
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_STATE = os.environ['BOT_STATE']


# Bot connection URL: https://discordapp.com/oauth2/authorize?client_id=494936000360087563&scope=bot&permissions=201620576
# Staging Bot Connection URL: https://discordapp.com/oauth2/authorize?client_id=499998765273448478&scope=bot&permissions=201620576

# Below cogs represents our folder our cogs are in. Following is the file name. So 'meme.py' in cogs, would be cogs.meme
# Think of it like a dot path import
initial_extensions = ['cogs.reply',
                      'cogs.random',
                      'cogs.admin']

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        # try:
        bot.load_extension(extension)
        # except Exception as e:
            # print(f'Failed to load extension {extension}.')


@bot.event
async def on_ready():
    for i in bot.guilds:
        print('We have logged in as {0.user}'.format(bot))
        if BOT_STATE == "PRODUCTION":
            print("Loaded as Production")
        elif BOT_STATE == "STAGING":
            await i.me.edit(nick="ReactionBot_Staging")
            print("Setting Nickname to staging one")
        else:
            logging.error("Couldn't Find BOT_STATE!! Defaulting to whatever I was named before: " + i.me.nick)
        await bot.change_presence(activity=discord.Game(name='Type r!help to get started!'))


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


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('That command doesn\'t seem to exist! Please try again, and type `'
                       'help` to view the help documentation.')


@bot.event
async def on_message(message):
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
                                      message_channel=message.channel.id, message_server=message.guild.id,
                                      message_id=message.id)
            session.add(current_message)
        session.commit()
        session.close()
        Message.prune_db(2000)

    # Insures the other commands are still processed
    await bot.process_commands(message)

bot.run(BOT_TOKEN, bot=True, reconnect=True)
