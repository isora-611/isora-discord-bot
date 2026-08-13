import random 
import discord
import json
import os
from discord.ext import commands
from discord import app_commands 

STATION_FILE = "data/stations.json"
 
def load_stations():
    if not os.path.exists(STATION_FILE):
        raise FileNotFoundError(
            "cannot find station.json, please make sure it is in the correct folder"
        )
    with open(STATION_FILE, "r", encoding="utf-8")as f:
        return json.load(f)

class PullStation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="pull-taipeimetro",
        description="隨機抽出一個捷運車站"
    )
    
    async def draw_slash(self, interaction: discord.Interaction):
        stations = load_stations()
        station = random.choice(stations)
        await interaction.response.send_message(
            f"{interaction.user.mention} 你抽到了 {station["id"]} **{station["Station"]}**({station["StationEn"]})"
            )

async def setup(bot):
    await bot.add_cog(PullStation(bot))
