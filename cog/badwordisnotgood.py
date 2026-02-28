from discord.ext import commands
from libs.easyfile import json_write


class BadWordKiller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnlist = bot.warnlist

    @commands.Cog.listener()
    async def on_bad_word_caught(self, message):
        u_id_str = str(message.author.id)
        self.warnlist[u_id_str] = self.warnlist.get(u_id_str, 0) + 1
        json_write('warn.json', self.warnlist)  # 바로 저장

        await message.channel.send(f"⚠️ {message.author.name}님, 욕설 주의! (누적: {self.warnlist[u_id_str]})", delete_after=1)


async def setup(bot):
    from __main__ import warnlist
    await bot.add_cog(BadWordKiller(bot))
