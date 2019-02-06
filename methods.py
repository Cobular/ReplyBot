import re
import random
from discord.ext.commands import context
from discord import Forbidden
import discord
import json


def clean_string(string_to_clean):
    """ Cleans text fed into it. Does so pretty agresively, be warned

    Strips whitespace, lowercases message, removes all characters not matching this regrex: '[A-Za-z0-9]+'
    :param string_to_clean: The string that is going to be cleaned
    :return cleaned_string: The string post-cleaning.
    """
    return re.sub('[^A-Za-z0-9]+', '', string_to_clean.strip().lower())


def clean_string_light(string_to_clean):
    """ Cleans text fed into it. Does so pretty agresively, be warned

    Strips whitespace, lowercases message, removes all characters not matching this regrex: '[A-Za-z0-9]+'
    :param string_to_clean: The string that is going to be cleaned
    :return cleaned_string: The string post-cleaning.
    """
    return re.sub('[`\r\n]+', '', string_to_clean.strip())


def quote_selector():
    """ Randomly generates a flexy quote for the bot to say

    Uses the number of times a quote appears in the dict to control the frequency of the quote appearing
    """
    switch = {
        1: "I sawed this boat in half!",
        2: "I sawed this boat in half!",
        3: "Hi, Phil Swift here for flex tape!",
        4: "Hi, Phil Swift here for flex tape!",
        5: "That\'s a lot of damage!",
        6: "That\'s a lot of damage!"}
    selector = random.randint(1, len(switch))  # Randomly select a choice
    return switch.get(selector, "Invalid Quote Choice")


async def delete_invocation(ctx: context):
    try:
        ctx.message.detete()
    except Forbidden:
        ctx.send(
            "I don't have the permissions to delete the invocation message. I need the `Manage Messages` permission!")


with open("prefixes.json") as f:
    prefixes = json.load(f)
default_prefix = "r!"


def get_prefix_for_init(bot, message):
    return prefixes.get(str(message.guild.id), default_prefix)


def get_prefix(server_id):
    return prefixes.get(str(server_id), default_prefix)


async def update_prefix(bot, id):
    await bot.change_presence(activity=discord.Game(name='Type `' + get_prefix(id) + 'help` to get started!'))
