import discord
from discord.ext import commands
from libs.badwordcutting import cutting
from libs.easyfile import *
from libs.easydiscord import m
from discord import app_commands


class ViewMyWarn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns=bot.warnlist
    @app_commands.command(name="경고조회", description="입력된 사람의 경고를 조회합니다")
    async def warn_check(self,itn: discord.Interaction, user: discord.Member=None):
        print(self)
        if user == None:
            await itn.response.send_message(f'당신의 경고 수는 {self.warns[itn.user.id]}')
        if isinstance(user, discord.Member):
            await itn.response.send_message(f'{user.mention}님의 경고 수는 {self.warns[user.id]}')

async def setup(bot):
    bot.add_cog(ViewMyWarn(bot))