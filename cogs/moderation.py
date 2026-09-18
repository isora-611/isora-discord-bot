import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime

from datetime import timezone, timedelta
taiwan_tz = timezone(timedelta(hours=8))

TRACKING_FILE = "data/tracking.json"

MESSAGE_LOG = "data/msglog.json"

WHITELIST_FILE = "data/whitelistrole.json"

GOD = {1007279246332416030}

class Moderation(commands.Cog):

    def __init__(self,bot):
        self.bot = bot 
        self.tracking = self.load_tracking()
        self.whitelist = self.load_whitelist()

    def load_tracking(self):
        try:
            with open(TRACKING_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        except FileNotFoundError:
            print ("cannot find json file, please make sure it is in the correct folder")
            return {}

        
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

    def load_whitelist(self):
        try:
            with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_whitelist(self,data):
        with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f, 
                indent=4
            )

    def check_permission(self, user: discord.Member):
        if user.guild_permissions.administrator:
            return True

        if user.id in GOD:
            return True

        if any(role.id in self.whitelist for role in user.roles):
            return True

        return False

    @app_commands.command(
            name="time",
            description="讓我告訴你現在時間"
    ) 
    async def time_now(self, interaction: discord.Interaction):

        time = datetime.now(taiwan_tz)

        await interaction.response.send_message(
            f"現在時間是 {time.strftime("%Y-%m-%d %H:%M:%S")}"
        )

    @app_commands.command(
            name="add-whitelist-role",
            description="新增白名單身分組(需管理員身分才可執行)"
    )
    @app_commands.describe(role="要加入白名單的身分組")
    async def add_whitelist_role(self, interaction: discord.Interaction, role: discord.Role):

        if (
            not interaction.user.guild_permissions.administrator
            and interaction.user.id not in GOD
            ):
            await interaction.response.send_message(
                "你沒有權限使用這個指令",   
                ephemeral=True
                )
            return

        if role.id in self.whitelist:
            await interaction.response.send_message(
                f"身分組 {role.mention} 已經在白名單中了",
                ephemeral=True
            )
            return

        self.whitelist.append(role.id)
        self.save_whitelist(self.whitelist)

        await interaction.response.send_message(
            f"已將身分組 {role.mention} 加入白名單"
            )

    @app_commands.command(
            name="remove-whitelist-role",
            description="移除白名單身分組(需管理員身分才可執行)"
    )
    @app_commands.describe(role="要移除白名單的身分組")
    async def remove_whitelist_role(self, interaction: discord.Interaction, role: discord.Role):

        if (
            not interaction.user.guild_permissions.administrator
            and interaction.user.id not in GOD
            ):
            await interaction.response.send_message(
                "你沒有權限使用這個指令",
                ephemeral=True
            )
            return
        
        if role.id not in self.whitelist:
            await interaction.response.send_message(
                f"身分組 {role.mention} 不在白名單中",
                ephemeral=True
            )
            return

        self.whitelist.remove(role.id)
        self.save_whitelist(self.whitelist)

        await interaction.response.send_message(
            f"已將身分組 {role.mention} 從白名單移除"
        )

    @app_commands.command(
        name="start-tracking",
        description="開始監聽目前頻道(需管理員身分才可執行)"
    )
    async def start_tracking(self, interaction: discord.Interaction):

        if not self.check_permission(interaction.user):
            await interaction.response.send_message(
                "你沒有權限使用這個指令",
                ephemeral=True
            )
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                "該指令只能在伺服器中使用"
                )
            return

        channel_id = str(interaction.channel.id)

        if (channel_id in self.tracking):

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
                "任何 **非管理員** 或無 **白名單身分組** 於此頻道發言,將立即被踢出伺服器並停權\n"
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

        if not self.check_permission(interaction.user):
            await interaction.response.send_message(
                "你沒有權限使用這個指令",
                ephemeral=True
            )
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                "該指令只能在伺服器中使用"
            )
            return

        channel_id = str(interaction.channel.id)

        if (channel_id not in self.tracking):

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

        if self.check_permission(message.author):
            print("user in whitelist")
            return

        try:
            await message.author.ban(
                reason="在禁止頻道中發言,爽啦憨仔包一包滾出去",
                delete_message_seconds=3600
            )
            print(f"{message.author} has been banned")

        except discord.Forbidden:
            raise PermissionError(
                "no permission to ban members"
                )

async def setup(bot):
    await bot.add_cog(Moderation(bot))
