import discord
from discord import app_commands
from discord.ext import commands
import os
import aiohttp
from datetime import datetime
from datetime import (timedelta, timezone)
taiwan_timezone = timezone(timedelta(hours=8)) 

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
FETCH_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001"

PAGE_CAP = 25

async def fetch_stations():
    params = {
        "Authorization": WEATHER_API_KEY,
        "format": "JSON"
    }

    connector = aiohttp.TCPConnector(ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(FETCH_URL, params=params) as response:

            if response.status != 200:
                error_text = await response.text()
                print(f"錯誤內容: {error_text}")
                return []
            
            data = await response.json()
            stations = data.get("records", {}).get("Station", [])
            return stations

def build_embed(station: dict) -> discord.Embed:

    weather = station.get("WeatherElement", {})
    geo = station.get("GeoInfo", {})

    county = geo.get("CountyName", "N/A")
    town_name = geo.get("TownName", "")
    station_name = station.get("StationName", "未知觀測站")
    obs_time = station.get("ObsTime", {}).get("DateTime", "N/A")

    temp = weather.get("AirTemperature", "N/A")
    humidity = weather.get("RelativeHumidity", "N/A")
    wind_speed = weather.get("WindSpeed", "N/A")
    weather_desc = weather.get("Weather", "N/A")

    location = f"{county} {town_name}" if town_name else county

    embed = discord.Embed(
        title=f"{station_name} 即時天氣觀測",
        description=f"{location}",
        color=discord.Color.blue()
    )
    embed.add_field(name="溫度", value=f"{temp}°C", inline=True)
    embed.add_field(name="濕度", value=f"{humidity}%", inline=True)
    embed.add_field(name="風速", value=f"{wind_speed} m/s", inline=True)
    embed.add_field(name="天氣狀況", value=weather_desc, inline=False)
    embed.set_footer(text=f"觀測時間:{obs_time}")

    return embed

def build_county_options(stations: list):
    counties = sorted({
        s.get("GeoInfo", {}).get("CountyName")
        for s in stations
        if s.get("GeoInfo", {}).get("CountyName")
    })
    return counties

def make_station_label(s: dict):
    geo = s.get("GeoInfo", {})
    town_name = geo.get("TownName", "")
    station_name = s.get("StationName", "未知測站")
    return f"{station_name}({town_name})" if town_name else station_name

class station_select(discord.ui.Select):
    def __init__(self, stations: list, page: int, selected_id: str):
        start = page * PAGE_CAP
        end = start + PAGE_CAP
        page_stations = stations[start:end]

        options = []
        for s in page_stations:
            station_id = s.get("StationId")
            label = make_station_label(s)[:100]

            options.append(
                discord.SelectOption(
                    label=label,
                    value=station_id,
                    default=(station_id == selected_id)
                )
            )

        super().__init__(
            placeholder="請選擇測站...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        chosen_id = self.values[0]

        view = self.view

        view.selected_station_id = chosen_id
        view.confirm_button.disabled = False
        view.confirm_button.label = "查詢天氣" 

        view.rebuild()

        await interaction.response.edit_message(
            content=view.build_content(),
            view=view
            )

class previous_page(discord.ui.Button):
    def __init__(self):
        super().__init__(label="◀ 上一頁", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):

        view = self.view

        view.page -= 1
        view.rebuild()
        await interaction.response.edit_message(
            content=view.build_content(),
            view=view
        )

class next_page(discord.ui.Button):
    def __init__(self):
        super().__init__(label="下一頁 ▶", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):

        view = self.view

        view.page += 1
        view.rebuild()
        await interaction.response.edit_message(
            content=view.build_content(),
            view=view
        )

class back_to_county(discord.ui.Button):
    def __init__(self):
        super().__init__(label="↩ 重新選擇縣市", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        stations = await fetch_stations()

        if not stations:
            await interaction.edit_original_response(
                content="氣象署 API 目前無法連線,請稍後再試",
                view=None
            )
            return

        counties = build_county_options(stations)
        view = CountySelectView(counties)

        await interaction.edit_original_response(
            content="請選擇要查詢的縣市:",
            view=view
        )
        
class confirm(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="請先選擇測站",
            style=discord.ButtonStyle.primary,
            disabled=True
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        stations = await fetch_stations()

        if not stations:
            await interaction.edit_original_response(
                content="氣象署 API 目前無法連線,請稍後再試",
                embed=None,
                view=None
            )
            return

        matched_station = next(
            (s for s in stations if s.get("StationId") == self.view.selected_station_id),
            None
        )

        if matched_station is None:
            await interaction.edit_original_response(
                content="找不到該測站的資料,請重新查詢",
                embed=None,
                view=None
            )
            return

        embed = build_embed(matched_station)

        await interaction.edit_original_response(content=None, embed=embed, view=None)

class StationSelectView(discord.ui.View):
    def __init__(self, county: str, stations: list):
        super().__init__(timeout=180)
        self.county = county
        self.stations = stations
        self.page = 0
        self.total_pages = (len(stations) - 1) // PAGE_CAP + 1
        self.selected_station_id = None

        self.confirm_button = confirm()

        self.rebuild()

    def rebuild(self):
        self.clear_items()

        self.add_item(station_select(
            self.stations,
            self.page,
            self.selected_station_id
        ))

        if self.page > 0:
            self.add_item(previous_page())
        if self.page < self.total_pages - 1:
            self.add_item(next_page())

        self.add_item(self.confirm_button)
        self.add_item(back_to_county())

    def build_content(self):
        return (
            f"已選擇「{self.county}」,請選擇測站(第 {self.page + 1}/{self.total_pages} 頁),"
            f"選完後按下方按鈕確認:"
        )


class CountySelect(discord.ui.Select):
    def __init__(self, counties: list):
        options = [
            discord.SelectOption(label=county, value=county)
            for county in counties
        ]
        super().__init__(
            placeholder="請選擇縣市...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        county = self.values[0]
        stations = await fetch_stations()

        matched = [
            s for s in stations
            if s.get("GeoInfo", {}).get("CountyName") == county
            and s.get("WeatherElement", {}).get("AirTemperature") not in ("-99", "-99.0", None)
        ]

        if not matched:
            await interaction.edit_original_response(
                content=f"{county} 目前查無有效觀測資料",
                view=None
            )
            return

        view = StationSelectView(county, matched)

        await interaction.edit_original_response(
            content=view.build_content(),
            view=view
        )

class CountySelectView(discord.ui.View):
    def __init__(self, counties: list):
        super().__init__(timeout=180)
        self.add_item(CountySelect(counties))

class weather(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(
        name="weather",
        description="查詢目前天氣"
    )
    async def Weather(self, interaction: discord.Interaction):
        print(f"user {interaction.user.name} used weather command at {datetime.now(taiwan_timezone).strftime("%Y-%m-%d %H:%M:%S")}")
        await interaction.response.defer()

        stations = await fetch_stations()

        if not stations:
            await interaction.followup.send("目前無法連線至氣象屬 API, 請稍後重試")
            return

        counties = build_county_options(stations)

        view = CountySelectView(counties)
        await interaction.followup.send(
            "請選擇要查詢的縣市:",
            view=view
            )

async def setup(bot):
    await bot.add_cog(weather(bot))