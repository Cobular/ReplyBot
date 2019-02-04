import re
import random


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

