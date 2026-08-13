import discord 
from discord import app_commands
from discord.ext import commands

class voicechat(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @app_commands.command(
        name="join",
        description="加入語音頻道"
    )

    async def join(self, interaction: discord.Interaction):

        if interaction.guild is None:
            await interaction.response.send_message(
                "該指令只能在伺服器中使用"
            )
            return

        if interaction.user.voice is None:
            await interaction.response.send_message(
                "你不在語音頻道中",
                ephemeral=True
                )
            return

        channel = interaction.user.voice.channel

        await channel.connect()

        await interaction.response.send_message(
            f"已加入 {channel.name}"
        )

    @app_commands.command(
        name="leave",
        description="離開語音頻道"
    )

    async def leave(self, interaction: discord.Interaction):

        voice = interaction.guild.voice_client

        if interaction.guild is None:
            await interaction.response.send_message(
                "該指令只能在伺服器使用"
            )
            return

        if voice is None:
            await interaction.response.send_message(
                "我不在語音頻道中",
                ephemeral=True
            )
            return

        if interaction.user.voice is None:
            await interaction.response.send_message(
                "你不在語音頻道中",
                ephemeral=True
            )
            return

        await voice.disconnect()

        await interaction.response.send_message(
            "已離開語音頻道",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(voicechat(bot))