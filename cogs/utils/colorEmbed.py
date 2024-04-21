# Description: This file contains the colors used in the embeds.

# * Import the necessary libraries
import random

# * Define the colors
Red = 0xff91ad
Green = 0x91ff9a
Blue = 0x91bfff
Yellow = 0xfff691
Orange = 0xffb391
Purple = 0xd391ff
Pink = 0xff91f2

# * Define the colors as a dictionary
colors = {
    'Red': 0xff91ad,
    'Green': 0x91ff9a,
    'Blue': 0x91bfff,
    'Yellow': 0xfff691,
    'Orange': 0xffb391,
    'Purple': 0xd391ff,
    'Pink': 0xff91f2
}

def generate_random_color():
    # Choose a random color name from the dictionary
    random_color_name = random.choice(list(colors.keys()))
    # Get the corresponding color value
    random_color = colors[random_color_name]
    return random_color