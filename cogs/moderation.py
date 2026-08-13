import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import dotenv

from datetime import timezone, timedelta
taiwan_tz = timezone(timedelta(hours=8))

TRACKING_FILE = "data/tracking.json"

MESSAGE_LOG = "data/msglog.json"

GOD = {} #u can put your id here or something else idk 

class Moderation(commands.Cog):

    def __init__(self,bot):
        self.bot = bot 
        self.tracking = self.load_tracking()

    def load_tracking(self):
        if not os.path.exists(TRACKING_FILE):
            print ("cannot find json file, please make sure it is in the correct folder")
            return {}

        with open(TRACKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def save_tracking(self):
        with open(TRACKING_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tracking, f, indent=4)

    def load_messages(self):
        if not os.path.exists(MESSAGE_LOG):
            print ("cannot find json file, please make sure it is in the correct folder")
            return []
        
        with open(MESSAGE_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def save_messages(self,messages):
        with open(MESSAGE_LOG, "w", encoding="utf-8") as f:
            json.dump(
                messages,
                f,
                ensure_ascii=False,
                indent=4
            )

    @app_commands.command(
        name="start-tracking",
        description="開始監聽目前頻道(需管理員身分才可執行)"
    )
    async def start_tracking(self, interaction: discord.Interaction):

        if (
            not interaction.user.guild_permissions.administrator
            and interaction.user.id not in GOD
        ):
            
            await interaction.response.send_message(
                "You don't have permission to run this command",
                ephemeral=True
            )
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                "該指令只能在伺服器中使用"
                )
            return

        channel_id = str(interaction.channel.id)

        if(
            channel_id in self.tracking
        ):
            await interaction.response.send_message(
                "此頻道已在監聽列表中",
                ephemeral=True
            )
            return

        self.tracking[channel_id] = True

        self.save_tracking()

        embed = discord.Embed(
            title="⚠️ 警告",
            description=(
                "此頻道已開始監聽\n\n"
                "任何 **非管理員** 於此頻道發言,將立即被踢出伺服器並停權\n"
                "※機器人為偵測制,故意發言也會遭到踢出"
            ),
            color=discord.Color.red()
        )

        await interaction.channel.send(embed=embed)

        await interaction.response.send_message(
            "開始監聽目前頻道",
            ephemeral=True
        )

    @app_commands.command(
        name="stop-tracking",
        description="停止監聽目前頻道(需管理員身分才可執行)"
    )
    async def stop_tracking(self, interaction: discord.Interaction):

        if (
            not interaction.user.guild_permissions.administrator
            and interaction.user.id not in GOD
        ):
            await interaction.response.send_message(
                "You don't have permission to run this command",
                ephemeral=True
            )
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                "該指令只能在伺服器中使用"
            )
            return

        channel_id = str(interaction.channel.id)

        if(
            channel_id not in self.tracking
        ):
            await interaction.response.send_message(
                "此頻道不在監聽列表中",
                ephemeral=True
            )
            return

        self.tracking.pop(channel_id, None)

        self.save_tracking()

        await interaction.response.send_message(
            "此頻道已停止監聽",
        )

    @app_commands.command(
        name="監聽列表",
        description="查看監聽中的頻道"
    )
    async def tracking_list(self, interaction: discord.Interaction):

        if not self.tracking:
            await interaction.response.send_message(
                "目前沒有監聽中的頻道",
                ephemeral=True
            )
            return
        
        channels = []

        for channel_id in self.tracking:
            channel = self.bot.get_channel(int(channel_id))

            if channel:
                channels.append(channel.mention)

        embed = discord.Embed(
            title="目前監聽列表",
            description="\n ".join(channels),
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if str(message.channel.id) not in self.tracking:
            return
        
        time = message.created_at.astimezone(taiwan_tz)

        messages = self.load_messages()

        messages.append({
            "author": message.author.name,
            "id": message.author.id,
            "content": message.content,
            "channel": message.channel.id,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        })

        self.save_messages(messages)

        print(f"recieved messages: {message.author.name} -> {message.content}")

        if message.author.id in GOD:
            return
        
        if message.author.guild_permissions.administrator:
            return
        
        try:
            await message.author.ban(
                reason="在禁止頻道中發言,爽啦憨仔包一包滾出去",
                delete_message_seconds=86400
            )
            print(f"{message.author} has been banned")

        except discord.Forbidden:
            raise PermissionError(
                "no permission to ban members"
                )

async def setup(bot):
    await bot.add_cog(Moderation(bot))