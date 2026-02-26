import discord
from discord import *
from libs.easydiscord import *
from discord.ext import commands

class Pingpong(commands.Cog):
    def __init__(self, bot):
      self.bot = bot
    @command(name="핑", description="을 확인 합니다.")
    async def on_btn1(self,interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        judge = '알 수 없음'
        if latency_ms > 250:
          judge = '핑이 나쁩니다.'
        elif latency_ms > 100:
          judge = '조금 느릴 수 있습니다.'
        elif latency_ms < 101:
          judge = '핑이 빠릅니다~!'
        await send(self.bot, target=interaction, content=f'<퐁>! {latency_ms}ms, {judge}')

async def setup(bot):
    await bot.add_cog(Pingpong(bot))
