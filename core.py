#!/usr/bin/env python

"""A Discord bot made with Discord.py that allows users to use a telegram-esque replying system in Discord

This file contains all the code that sets up the bot and runs the cogs, as well as a few assorted function calls that
have not yet been moved out.

tools/
  methods.py contains various utilities and tools used throughout the project
cogs/
  reply.py is the main code of the bot, it handles the saving of messages as well as the search and response to requests
  admin.py contains commands for bot administration and control. Many items there will not show up in help.
  random.py has other random crap I wrote, bot invite requests and other stuff
"""
import discord
from discord.ext import commands
import os
import logging


# ACK: Discord.py Documentation, Rapptz: https://discordpy.readthedocs.io/en/latest/
bot = commands.Bot(command_prefix='r!', command_not_found="Heck! That command doesn't exist!!",
                   description="Thanks for using ReplyBot, Replying for Gamers!")
# ACK: Python Logging Tutorial: https://realpython.com/python-logging/
logging.basicConfig(level=logging.INFO)
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_STATE = os.environ['BOT_STATE']

# Bot connection URL:
#   https://discordapp.com/oauth2/authorize?client_id=494936000360087563&scope=bot&permissions=201620576
# Staging Bot Connection URL:
#   https://discordapp.com/oauth2/authorize?client_id=499998765273448478&scope=bot&permissions=201620576

# Below cogs represents our folder our cogs are in. Following is the file name. So 'meme.py' in cogs, would be cogs.meme
initial_extensions = ['cogs.reply',
                      'cogs.random',
                      'cogs.admin']

# Here we load our extensions(cogs) listed above in [initial_extensions].
# ACK: User-made gist: https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5
if __name__ == '__main__':
    for extension in initial_extensions:
        # noinspection PyBroadException
        try:
            bot.load_extension(extension)
            logging.info(f'Successfully loaded extension {extension}')
        except Exception as e:
            logging.error(f'Failed to load extension {extension}. Exception: {e}')


# ACK: Discord.py Documentation, Rapptz: https://discordpy.readthedocs.io/en/latest/
@bot.event
async def on_ready():
    """Sets up the bot's nicknames and the game it is streaming"""

    # Checks the login state
    if BOT_STATE == "PRODUCTION":
        # ACK: Python Logging Tutorial: https://realpython.com/python-logging/
        logging.info("Loaded as Production")
    elif BOT_STATE == "STAGING":
        # ACK: Python Logging Tutorial: https://realpython.com/python-logging/
        logging.info("Loaded as Staging Changing nickname...")
        # ACK: Discord.py Documentation, Rapptz: https://discordpy.readthedocs.io/en/latest/
        await bot.user.edit(nick="ReplyBot_Staging")
    else:
        # ACK: Python Logging Tutorial: https://realpython.com/python-logging/
        logging.error("Couldn't Find BOT_STATE!! Defaulting to staging")

    # Sets up the bot's "game"
    await bot.change_presence(activity=discord.Game(
        name='Type r!help to get started.'))

    # Counts servers the bot is on
    counter = 0
    for i in bot.guilds:
        counter += 1
        print('We have logged in as {0.user}'.format(bot))
    logging.info("We are in {0} server!".format(counter))


# ACK: Discord.py Documentation, Rapptz: https://discordpy.readthedocs.io/en/latest/
@bot.event
async def on_guild_join(guild):
    """Sets up everything when the bot joins a new server"""
    # ACK: Python Logging Tutorial: https://realpython.com/python-logging/
    logging.info('We have been added to a new server  {0.name}'.format(guild))

    # Sends a message on join, will change nickname on staging and give an error elsewhere
    if BOT_STATE == "PRODUCTION":
        # ACK: Python Logging Tutorial: https://realpython.com/python-logging/
        logging.info("Loaded mid-run as Production")
    elif BOT_STATE == "STAGING":
        # ACK: Python Logging Tutorial: https://realpython.com/python-logging/
        logging.info("Loaded mid-run as Staging. Changing nickname...")
        await guild.me.edit(nick="ReplyBot_Staging")
    else:
        # ACK: Python Logging Tutorial: https://realpython.com/python-logging/
        logging.error("Loaded mid-run but couldn't Find BOT_STATE!! Defaulting to staging")

# ACK: Discord.py Documentation, Rapptz: https://discordpy.readthedocs.io/en/latest/
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('That command doesn\'t seem to exist! Please try again, and type `'
                       'help` to view the help documentation.')
        logging.info(f"Bad command entered, {error}")


@bot.event
async def on_message(message):
    # This is just here to exist in case I need it later. Should be moved out soon
    # Insures the other commands are still processed

    # ACK: User help in a github issue: https://github.com/Rapptz/discord.py/issues/186
    await bot.process_commands(message)

bot.run(BOT_TOKEN, bot=True, reconnect=True)
