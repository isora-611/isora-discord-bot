import discord
import random
from discord.ext import commands
from discord import app_commands

class msgdetect(commands.Cog):
    
    @commands.Cog.listener()
    async def on_message(self,message):

        if message.author.bot:
            return

        if "嚇到我了" in message.content:
            await message.channel.send("被嚇到了嗎")

        if "吃什麼" in message.content:
            await message.channel.send("鼎王一桌低消650 任你吃啊\n"
                                "一個人他媽的麻辣鍋150塊啊鼎王的水都不用錢的 我都 欸冰水一壺喝完一壺 冰水一壺\n" 
                                "豆腐鴨血豆腐鴨血豆腐鴨血\n"
                                "冰水冰水冰水冰水\n"
                                "就吃飽了啊\n"
                                "白飯無限盛啊\n"
                                "白飯沒了就說\n"
                                "你給我補白飯！")

        if "？" == message.content:
            await message.channel.send(":question:")

        if "?" == message.content:
            await message.channel.send(":question:")

        if (f"<@{message.author.id}>") == message.content:
            await message.channel.send("@自己是有什麼心事= =")

        if (
            "<@1007279246332416030>" in message.content
            and "是傻逼" in message.content
            ):
            await message.channel.send("對")

        if (
            message.author.id == 1007279246332416030
            and "我是傻逼" in message.content
        ):
            await message.channel.send("對")

async def setup(bot):
    await bot.add_cog(msgdetect(bot))
