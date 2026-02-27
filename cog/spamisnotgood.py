import discord
from discord.ext import commands
from datetime import timedelta, datetime
import asyncio

def lines_count(content):
    if not content:
        return 0
    length = len(content)
    # 큰 글자 (# )
    if content.startswith('# '):
        return length / 21
    # 중간 글자 (## )
    elif content.startswith('## '):
        return length / 26
    # 일반 글자
    else:
        return length / 32
# 10분 지나면 초기화하기
class Spam1killer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.u_temp_warn = {}
        self.u_saved = {}
        self.u_msg_id = {}
        self.cn_message={}
        self.task = {}
    @commands.Cog.listener()
    async def on_message(self, messages):
        key = messages.author.id
        c_id = messages.channel.id
        lines = lines_count(messages.content)
        now = datetime.now()
        # 봇이 쓴 메시지는 무시
        if messages.author.bot:
            return
        # ㅜ 채널 - 메시지 관련 / 유저랑은 관계 X
        if not c_id in self.cn_message: # 채널이 딗에 등록되어 있지 않으면
            self.cn_message[c_id] = [lines, now]
        else:
            data_c = self.cn_message[c_id]
            if now - data_c[1] >= timedelta(seconds=10): # 간격이 10초보다 크면 채널값 초기화
                self.cn_message[c_id] = [lines, now]
            else:
                data_c[0] += lines
                data_c[1] = now
                if self.cn_message[c_id][0] > 30:
                    if messages.channel.slowmode_delay != 30:
                        try:
                            await messages.channel.edit(slowmode_delay=30)

                        except discord.Forbidden: # 권한없음 에러
                            pass
                    # ---------ㅜ 생성형 인공지능 생성 ㅜ ----------
                    if c_id not in self.task or self.task[c_id].done():
                        async def auto_off():
                            await asyncio.sleep(300)  # 5분 대기
                            if messages.channel.slowmode_delay == 30: # 여전히?
                                await messages.channel.edit(slowmode_delay=0)
                        t = asyncio.create_task(auto_off()) # 난 모름
                        self.task[c_id] = t
                        # ---------ㅗ 생성형 인공지능 생성 ㅗ ----------
                        self.cn_message[c_id] = [0, now] # 채널별 메시지 초기화
                        return
# ---------------- ㅜ 아래는 큰 글자 도배 ㅜ ---------------------------- #
        if lines > 14:
            if not key in self.u_saved: # 처음 한 사용자일때는 딕셔너리에 추가하가기
                self.u_saved[key] = now
                self.u_msg_id[key] = []
                self.u_temp_warn[key] = 12 if lines > 40 else 1
                self.u_msg_id[key].append(messages.id)

            elif lines > 40: # 엄청난도배
                if not key in self.u_msg_id: self.u_msg_id[key] = []
                self.u_msg_id[key].append(messages.id)
                self.u_temp_warn[key] = self.u_temp_warn.get(key, 0) + 12
            else:
                start = self.u_saved[key] # 마지막 도배시간
                if now - start > timedelta(minutes=10): # 10분이 지났을 때
                    self.u_saved[key] = now
                    if self.u_temp_warn.get(key, 0) > 0: # 경고가 있어야
                        self.u_temp_warn[key] = self.u_temp_warn.get(key, 0) - 1 # 빼기
                    if key in self.u_msg_id: # 사용자명에 해당하는 메시지id가 존재하면
                        self.u_msg_id[key] = self.u_msg_id[key][-1:]
                else:
                    self.u_temp_warn[key] = self.u_temp_warn.get(key, 0) + 1
                    self.u_msg_id[key].append(messages.id)

        # ---- ㅜ 처벌만 하는 로직 ----ㅜ ----
        if self.u_temp_warn.get(key, 0) > 3: # 도배로 판정됨
            safe = []
            _now = discord.utils.utcnow()
            limit = _now - timedelta(days=14)
            mid_clear = set(self.u_msg_id.get(key, []))
            for m_id in mid_clear:
                # 만들어진 시간들이 2주이내
                if discord.Object(id=m_id).created_at > limit:
                    safe.append(m_id)

            self.u_msg_id[key] = safe

            msg = self.u_msg_id.get(key, []) # 삭제할 메시지것들을 모으기
            try:
                if hasattr(messages.author, 'timeout'):
                    await messages.author.timeout(timedelta(minutes=30), reason = '도배')
                # -- 일부 로직 Ai 참고 -- Object와 delete_messages 새로 배워갑니다~~
                to_delete = [discord.Object(id=i) for i in msg[:100]]
                await messages.channel.delete_messages(to_delete)
                # 참고 끝
            except (discord.HTTPException, AttributeError,TypeError,KeyError):
                pass

            self.u_saved[key] = datetime.now()
            self.u_msg_id[key] = []
            self.u_temp_warn[key] = 0

async def setup(bot):
    await bot.add_cog(Spam1killer(bot))
