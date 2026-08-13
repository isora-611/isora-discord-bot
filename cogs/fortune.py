import discord
from discord import app_commands
from discord.ext import commands

import os
import json 
import random

POEM_FILE = "data/poem.json"

def load_poem():
    if not os.path.exists(POEM_FILE):
        raise FileNotFoundError(
            "cannot find json file, please make sure it is in the correct folder"
        )
    with open(POEM_FILE, "r", encoding="utf-8")as f:
        return json.load(f)

class Fortune(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="今日運勢",
        description="今天的運氣如何呢"
    )

    async def draw_slash(self, interaction: discord.interactions):
        await interaction.response.send_message("該功能尚未實裝")
        return
        poems = load_poem()
        poem = random.choice(poems)
        await interaction.response.send_message(
            f"今日運勢"
        ) 

async def setup(bot):
    await bot.add_cog(Fortune(bot))