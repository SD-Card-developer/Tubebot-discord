import discord
from discord import app_commands, Intents, TextChannel, Interaction
from discord.ext import commands
from badwordcutting import *
from libs.easyfile import *

os.environ["token"] = ''
intents = Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
discord.Object.bots = bot
c = {}  # 임시 경고
bot.without = []  # 화이트리스트 채널
bot.security_channels = {}  # 서버별 보안 채널 {guild_id: [channel_id, ...]}

# 화이트리스트 로드
if os.path.exists('whitelist.txt'):
    with open('whitelist.txt', 'r', encoding='utf-8') as r:
        bot.without = [int(i) for i in r.read().split()]

if os.path.exists('whitelist_s.txt'):
    with open('whitelist_s.txt', 'r', encoding='utf-8') as r:
        bot.without = [int(i) for i in r.read().split()]

# 보안 채널 ds로드 (channels.txt -> 서버ID:채널ID)
if os.path.exists('channels.txt'):
    r = allread('channels.txt', 'utf-8')
    for l in r:
        try:
            gid, cid = map(int, l.strip().split(':'))
            if gid not in bot.security_channels:
                bot.security_channels[gid] = []
            bot.security_channels[gid].append(cid)
        except:
            continue

# 영구 경고 데이터 로드 (warn.json)
bot.warnlist = read_json('warn.json')

# 보안 로그 전송 함수
async def send_security_log(guild, message_text):
    target_ids = bot.security_channels.get(guild.id, [])
    for c_id in target_ids:
        chan = bot.get_channel(c_id)
        if chan:
            await chan.send(message_text)


# 준비 완료
@bot.event
async def on_ready():
    print(f'로그인 완료: {bot.user.name}')
    await bot.tree.sync()


@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    if message.channel.id not in bot.without:
        if cutting(message.content):
            try:
                # 슥슥 컷! -- ㅜ
                await message.delete()
                # ㅜ --- 새로 배운것. 이벤트를 보내기! 디스패치!
                bot.dispatch("bad_word_caught", message)
            except Exception as e:
                print(f"삭제 에러: {e}")
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    u_id_str = str(member.id)
    user_warns = bot.warnlist.get(u_id_str, 0)
    if user_warns >= 30:
        await send_security_log(member.guild,
            f"🚨 **분탕 의심 인물 입장**: {member.mention}\n"
            f"📈 누적 경고: `{user_warns}`회\n"
            f"💡 *오탐일 수 있으니 최근 활동을 지켜보세요.*")
    if user_warns >= 60:
        await send_security_log(member.guild,
            f"🚨 **악성 유저입니다!**: {member.mention}\n"
            f"📈 누적 경고: `{user_warns}`회\n"
            f"바로 밴하세요! 신고된 사람입니다.")

# 슬래시 명령어들 (서버별 보안 채널 설정/삭제)
@bot.tree.command(name='보안채널설정', description='보안 메시지 채널 추가')
async def set_sec(interaction: Interaction, channel: TextChannel):
    gid, cid = interaction.guild.id, channel.id
    if cid not in bot.security_channels.get(gid, []):
        bot.security_channels.setdefault(gid, []).append(cid)
        with open("channels.txt", "a", encoding='utf-8') as f:
            f.write(f"{gid}:{cid}\n")
        await interaction.response.send_message(f'✅ {channel.mention} 등록 완료.', ephemeral=True)
    else:
        await interaction.response.send_message('이미 등록된 채널이야.', ephemeral=True)

@bot.tree.command(name='보안-채널-삭제', description='보안 메시지 채널 삭제')
async def del_sec(interaction: Interaction, channel: TextChannel):
    gid, cid = interaction.guild.id, channel.id
    if cid in bot.security_channels.get(gid, []):
        bot.security_channels[gid].remove(cid)
        # 파일 전체 갱신 (서버ID:채널ID 형식 유지)
        with open("channels.txt", "w", encoding='utf-8') as f:
            for g, c_list in bot.security_channels.items():
                for c_item in c_list:
                    f.write(f"{g}:{c_item}\n")
        await interaction.response.send_message('🗑️ 삭제 완료.', ephemeral=True)
    else:
        await interaction.response.send_message('목록에 없는 채널이에요', ephemeral=True)

@bot.command(name='청소')
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f'{amount}개 삭제 완료!', delete_after=3)

# 화이트리스트 추가 명령어
@bot.tree.command(name='욕설-화이트리스트-채널-추가', description='이 채널을 욕설 검열에서 제외합니다.')
@app_commands.describe(channel='제외할 채널')
async def wl_add(interaction: Interaction, channel: TextChannel):
    global without
    if channel.id not in without:
        without.append(channel.id)
        # 파일에 추가 저장
        with open("whitelist.txt", "a", encoding='utf-8') as f:
            f.write(f"{channel.id}\n")
        await interaction.response.send_message(f'✅ {channel.mention} 채널이 화이트리스트에 등록되었습니다.', ephemeral=True)
    else:
        await interaction.response.send_message('이미 등록된 채널입니다.', ephemeral=True)

# 화이트리스트 제거 명령어
@bot.tree.command(name='욕설-화이트리스트-채널-제거', description='이 채널을 다시 욕설 검열에 포함합니다.')
@app_commands.describe(channel='다시 포함할 채널')
async def wl_remove(interaction: Interaction, channel: TextChannel):
    global without
    if channel.id in without:
        without.remove(channel.id)
        # 파일에서 해당 ID 삭제하고 다시 쓰기
        with open("whitelist.txt", "w", encoding='utf-8') as f:
            for c_id in without:
                f.write(f"{c_id}\n")
        await interaction.response.send_message(f'🗑️ {channel.mention} 채널을 화이트리스트에서 제거했습니다.', ephemeral=True)
    else:
        await interaction.response.send_message('화이트리스트에 없는 채널입니다.', ephemeral=True)

@bot.tree.command(name='도배-화이트리스트-채널-추가', description='이 채널을 도배 검열에서 제외합니다.')
@app_commands.describe(channel='제외할 채널')
async def swl_add(interaction: Interaction, channel: TextChannel):
    global without
    if channel.id not in without:
        without.append(channel.id)
        # 파일에 추가 저장
        with open("whitelist.txt_s", "a", encoding='utf-8') as f:
            f.write(f"{channel.id}\n")
        await interaction.response.send_message(f'✅ {channel.mention} 채널이 화이트리스트에 등록되었습니다.', ephemeral=True)
    else:
        await interaction.response.send_message('이미 등록된 채널입니다.', ephemeral=True)

# 화이트리스트 제거 명령어
@bot.tree.command(name='도배-화이트리스트-채널-제거', description='이 채널을 다시 도배 검열에 포함합니다.')
@app_commands.describe(channel='다시 포함할 채널')
async def swl_remove(interaction: Interaction, channel: TextChannel):
    global without
    if channel.id in without:
        without.remove(channel.id)
        # 파일에서 해당 ID 삭제하고 다시 쓰기
        with open("whitelist_s.txt", "w", encoding='utf-8') as f:
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


bot.run(os.environ["token"])
