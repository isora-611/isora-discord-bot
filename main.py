import os
import discord
from discord.ext import commands 
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

print ("Bot is starting...")

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents        
        )
       
    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded: {filename}")

        synced = await self.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    
    async def on_ready(self):
        print(f"Logged in as {self.user}")


bot = MyBot()

bot.run(TOKEN)