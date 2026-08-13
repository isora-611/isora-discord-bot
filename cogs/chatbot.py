import discord 
import os
import asyncio
from discord.ext import commands
from ollama import chat
from utils.aichat import ai_chat
from utils.history import(
    get_history,
    user_message,
    ai_response,
    trim_history
)

class ChatBot(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if self.bot.user not in message.mentions:
            return

        messages = get_history(
            message.guild.id,
            message.channel.id,
            message.author.id
        )

        content = message.content

        for user in message.mentions:
            content = content.replace(user.mention, "")

        content = content.strip()

        if not content:
            return

        user_message(messages, content)

        async with message.channel.typing():
            reply = await asyncio.to_thread(
                ai_chat,
                messages
            )

        ai_response(messages, reply)

        trim_history(messages)

        await message.reply(reply)

async def setup(bot):
    await bot.add_cog(ChatBot(bot))