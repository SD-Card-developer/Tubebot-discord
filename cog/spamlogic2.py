# RTX 6090 바보!

import discord
from discord.ext import commands
from libs.badwordcutting import cutting
from libs.easyfile import *
from libs.easydiscord import m


class Spam2killer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.u_msgs = self.bot.u_msgs
        self.dict_msg = {}  # 유저별 중복 메시지를 저장할 딕셔너리

    @commands.Cog.listener()
    async def on_message(self, messages):
        author = messages.author
        if author.bot:
            return
        if messages.channel.slowmode_delay >= 300:
            return
        if not author.id in self.u_msgs: # 사용자가 없으면
            self.u_msgs[author.id] = [] # 빈리스트 넣기

        self.u_msgs[author.id].append((messages.content, messages.id, messages.channel)) # 딕셔너리[유저] 리스트에 넣기
        if len(self.u_msgs[author.id]) > 20:
            self.u_msgs[author.id].pop(0)
        # ㅜ ----- 각각 메시지 전체정보, 메시지의 콘텐츠만 모은 리스트, 중복 없앤것, 중복 저장공간
        msgs = self.u_msgs[author.id]
        contents = [ms for ms, ids, chan in msgs]
        msgs_set = set(contents)
        many_msg = [] # 중복 메시지를 저장할 임시리스트

        if len(contents) > len(msgs_set):
            for pee, poop, trash in msgs:
                if contents.count(pee) >= 2:
                    many_msg.append((discord.Object(id=poop), trash))
                else:
                    pass
        if many_msg:
            self.dict_msg[author.id] = many_msg
            try:
                # ㅜ -- 메시지부터 지우고
                for obj, channel in many_msg: # 같이 튜풀에 담긴 내용/채널을 가지고옴
                    try:
                        await channel.delete_messages([obj]) # 리스트로 넣어서 지ㅣ우고ㅇ
                    except (discord.Forbidden, discord.HTTPException):
                        continue
                # ㅜ -- 리스트에서 지우기
                ids = [obj.id for obj, channel in many_msg]
                for it in self.u_msgs[author.id][:]:
                    if it[1] in ids:  # 원본의 메시지 ID가 삭제 목록에 있다면
                        self.u_msgs[author.id].remove(it)
                self.dict_msg[author.id] = [] # 임시메모장 비우기

                await messages.channel.send('도배이기 때문에 메시지가 삭제되었어요', delete_after=2)
            except discord.Forbidden:
                await messages.channel.send(f'권한이 없어서 못지웁니다 {messages.guild.owner.mention}')
                return

async def setup(bot):
    await bot.add_cog(Spam2killer(bot))