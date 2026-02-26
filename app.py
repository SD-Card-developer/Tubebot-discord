import os
import discord
from discord import app_commands, Intents, TextChannel, Interaction
from discord.ext import commands
from badwordcutting import *
from libs.easyfile import *

# 1. 데이터 저장소 준비
c = {}  # 임시 경고 (메모리 전용)
without = []  # 화이트리스트 채널
security_channels = {}  # 서버별 보안 채널 {guild_id: [channel_id, ...]}

# 화이트리스트 로드 (list.txt)
if os.path.exists('list.txt'):
    with open('list.txt', 'r', encoding='utf-8') as r:
        without = [int(i) for i in r.read().split()]

# 보안 채널 ds로드 (channels.txt -> 서버ID:채널ID)
if os.path.exists('channels.txt'):
    with open('channels.txt', 'r', encoding='utf-8') as r:
        for line in r:
            try:
                gid, cid = map(int, line.strip().split(':'))
                if gid not in security_channels:
                    security_channels[gid] = []
                security_channels[gid].append(cid)
            except:
                continue

# 영구 경고 데이터 로드 (warn.json)
warnlist = read_json('warn.json')

# 2. 봇 설정
os.environ["token"] = ''
intents = Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


# 3. 보안 로그 전송 함수
async def send_security_log(guild, message_text):
    target_ids = security_channels.get(guild.id, [])
    for c_id in target_ids:
        chan = bot.get_channel(c_id)
        if chan:
            await chan.send(message_text)


# 4. 준비 완료
@bot.event
async def on_ready():
    print(f'로그인 완료: {bot.user.name}')
    await bot.tree.sync()


# 5. 욕설 감지 및 경고 시스템
@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return

    if message.channel.id not in without:
        if cutting(message.content):
            try:
                await message.delete()
                u_id = message.author.id
                u_id_str = str(u_id)

                # 임시 경고 스택
                c[u_id] = c.get(u_id, 0) + 1
                await message.channel.send(f'⚠️ {message.author.name} 임시 경고 ({c[u_id]}/3)', delete_after=0.5)

                # 임시 3회 채우면 영구 경고 +1
                if c[u_id] >= 3:
                    c[u_id] = 0
                    warnlist[u_id_str] = warnlist.get(u_id_str, 0) + 1
                    # --- 여기서 네가 만든 함수 사용 ---
                    json_write('warn.json', warnlist)

                    if warnlist[u_id_str] >= 25:
                        await send_security_log(message.guild,
                                                f"🚨 **보안 경보**: {message.author.mention} 누적 경고 {warnlist[u_id_str]}회 돌파!")
            except:
                pass
    await bot.process_commands(message)


# 6. 위험 인물 입장 체크
@bot.event
async def on_member_join(member):
    u_id_str = str(member.id)
    user_warns = warnlist.get(u_id_str, 0)

    if user_warns >= 50:
        await send_security_log(member.guild, f"🔴 **위험 인물 감지**: 경고 {user_warns}")
# 7. 슬래시 명령어들 (서버별 보안 채널 설정/삭제)
@bot.tree.command(name='보안채널설정', description='보안 메시지 채널 추가')
async def set_sec(interaction: Interaction, channel: TextChannel):
    gid, cid = interaction.guild.id, channel.id
    if cid not in security_channels.get(gid, []):
        security_channels.setdefault(gid, []).append(cid)
        with open("channels.txt", "a", encoding='utf-8') as f:
            f.write(f"{gid}:{cid}\n")
        await interaction.response.send_message(f'✅ {channel.mention} 등록 완료.', ephemeral=True)
    else:
        await interaction.response.send_message('이미 등록된 채널이야.', ephemeral=True)

@bot.tree.command(name='보안채널삭제', description='보안 메시지 채널 삭제')
async def del_sec(interaction: Interaction, channel: TextChannel):
    gid, cid = interaction.guild.id, channel.id
    if cid in security_channels.get(gid, []):
        security_channels[gid].remove(cid)
        # 파일 전체 갱신 (서버ID:채널ID 형식 유지)
        with open("channels.txt", "w", encoding='utf-8') as f:
            for g, c_list in security_channels.items():
                for c_item in c_list:
                    f.write(f"{g}:{c_item}\n")
        await interaction.response.send_message('🗑️ 삭제 완료.', ephemeral=True)
    else:
        await interaction.response.send_message('목록에 없는 채널이야.', ephemeral=True)

@bot.command(name='청소')
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f'{amount}개 삭제 완료!', delete_after=3)

# 화이트리스트 추가 명령어
@bot.tree.command(name='화이트리스트', description='이 채널을 욕설 검열에서 제외합니다.')
@app_commands.describe(channel='제외할 채널')
async def wl_add(interaction: Interaction, channel: TextChannel):
    global without
    if channel.id not in without:
        without.append(channel.id)
        # 파일에 추가 저장
        with open("list.txt", "a", encoding='utf-8') as f:
            f.write(f"{channel.id}\n")
        await interaction.response.send_message(f'✅ {channel.mention} 채널이 화이트리스트에 등록되었습니다.', ephemeral=True)
    else:
        await interaction.response.send_message('이미 등록된 채널입니다.', ephemeral=True)

# 화이트리스트 제거 명령어
@bot.tree.command(name='화이트리스트-제거', description='이 채널을 다시 욕설 검열에 포함합니다.')
@app_commands.describe(channel='다시 포함할 채널')
async def wl_remove(interaction: Interaction, channel: TextChannel):
    global without
    if channel.id in without:
        without.remove(channel.id)
        # 파일에서 해당 ID 삭제하고 다시 쓰기
        with open("list.txt", "w", encoding='utf-8') as f:
            for c_id in without:
                f.write(f"{c_id}\n")
        await interaction.response.send_message(f'🗑️ {channel.mention} 채널을 화이트리스트에서 제거했습니다.', ephemeral=True)
    else:
        await interaction.response.send_message('화이트리스트에 없는 채널입니다.', ephemeral=True)

cogs = os.listdir("cog")
@bot.event
async def setup_hook():
    for cog in cogs:
        if cog.endswith('.py'):
            cog = cog.replace(".py", "")
            await bot.load_extension(f'cog.{cog}')
            print('{cog} 로드 완료!')
        else:
            pass
    await bot.tree.sync()
# 8. 봇 실행
bot.run(os.environ["token"])