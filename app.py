import discord
from discord import app_commands, Intents, TextChannel, Interaction
from discord.ext import commands
from libs.badwordcutting import *
from libs.easyfile import *
from dotenv import *

load_dotenv()

# 이건 2.0 버전
token = os.getenv("token")[::-1]
intents = Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
discord.Object.bots = bot
c = {}  # 임시 경고
bot.without = {}  # 화이트리스트 채널
bot.security_channels = {}  # 서버별 보안 채널 {guild_id: [channel_id, ...]}

bot.u_msgs = {} # 유저들의 메시지를 실시간으로다가 판별

# 화이트리스트 로드
bot.without_spam = {}

if os.path.exists('whitelist.json'):
    bot.without = read_json('whitelist.json')

if os.path.exists('whitelist_s.json'):
    bot.without_spam = read_json('whitelist_s.json')

if os.path.exists('u_msgs.json'):
    bot.u_msgs = read_json('u_msgs.json')

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
    if message.guild:
        guild_id = str(message.guild.id)
        whitelist_channels = bot.without.get(guild_id, [])
    
        if message.channel.id not in whitelist_channels:
            if cutting(message.content):
                try:
                    await message.delete()
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
        await interaction.response.send_message('이미 등록된 채널입니다.', ephemeral=True)

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
    guild_id = str(interaction.guild.id) #
    if guild_id not in bot.without:
        bot.without[guild_id] = []
    
    if channel.id not in bot.without[guild_id]:
        bot.without[guild_id].append(channel.id)
        json_write('whitelist.json', bot.without)
        await interaction.response.send_message(f'✅ {channel.mention} 채널이 화이트리스트에 등록되었습니다.', ephemeral=True)
    else:
        await interaction.response.send_message('이미 등록된 채널입니다.', ephemeral=True)

# 화이트리스트 제거 명령어
@bot.tree.command(name='욕설-화이트리스트-채널-제거', description='이 채널을 다시 욕설 검열에 포함합니다.')
@app_commands.describe(channel='다시 포함할 채널')
async def wl_remove(interaction: Interaction, channel: TextChannel):
    guild_id = str(interaction.guild.id)
    if guild_id in bot.without and channel.id in bot.without[guild_id]:
        bot.without[guild_id].remove(channel.id)
        json_write('whitelist.json', bot.without)
        await interaction.response.send_message(f'🗑️ {channel.mention} 채널을 화이트리스트에서 제거했습니다.', ephemeral=True)
    else:
        await interaction.response.send_message('화이트리스트에 없는 채널입니다.', ephemeral=True)

@bot.tree.command(name='도배-화이트리스트-채널-추가', description='이 채널을 도배 검열에서 제외합니다.')
@app_commands.describe(channel='제외할 채널')
async def swl_add(interaction: Interaction, channel: TextChannel):
    guild_id = str(interaction.guild.id)
    if guild_id not in bot.without_spam:
        bot.without_spam[guild_id] = []
    if channel.id not in bot.without_spam[guild_id]:
        bot.without_spam[guild_id].append(channel.id)
        json_write('whitelist_s.json', bot.without_spam)
        await interaction.response.send_message(f'✅ {channel.mention} 채널이 화이트리스트에 등록되었습니다.', ephemeral=True)
    else:
        await interaction.response.send_message('이미 등록된 채널입니다.', ephemeral=True)

# 화이트리스트 제거 명령어
@bot.tree.command(name='도배-화이트리스트-채널-제거', description='이 채널을 다시 도배 검열에 포함합니다.')
@app_commands.describe(channel='다시 포함할 채널')
async def swl_remove(interaction: Interaction, channel: TextChannel):
    guild_id = str(interaction.guild.id)
    if guild_id in bot.without_spam and channel.id in bot.without_spam[guild_id]:
        bot.without_spam[guild_id].remove(channel.id)
        json_write('whitelist_s.json', bot.without_spam)
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

@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    try:
        await bot.reload_extension(f'cog.{extension}') # 파일 경로에 맞춰 수정
        await ctx.send(f'✅ {extension} 모듈이 새로고침 되었습니다!')
    except Exception as e:
        await ctx.send(f'❌ 오류 발생: {e}')

@bot.command()
@commands.has_permissions(manage_messages=True) # 메시지관리가 돼어야 가능함
async def pg(ctx, number, types='all'):
    if types.startswith('all'):
        num = int(number)
        await ctx.channel.purge(limit=num)
        await ctx.send(f'총 {num}개 메시지가 삭제되었어요', delete_after=2)

    elif types.startswith('<@'):
        result = ""
        for char in types:
            if char.isdigit():
                result += char
        result = int(result)
        num = int(number)
        deleted = await ctx.channel.purge(limit=num, check=lambda mess: mess.author.id == result)
        await ctx.send(f'"{deleted[0].author}"님의 메시지 {num}개가 삭제되었어요', delete_after=2)

    elif types.startswith('bot'):
        num = int(number)
        def haha(mess):
            return mess.author.bot
        deleted = await ctx.channel.purge(limit=num, check=haha)
        if deleted:
            await ctx.send(f'봇의 메시지 {len(deleted)}개가 삭제되었어요', delete_after=2)
        else:
            await ctx.send('삭제할 일반 유저 메시지가 없네요!', delete_after=2)
    elif types.startswith('user'):
        num = int(number)
        def haha(mess):
            return not mess.author.bot
        deleted = await ctx.channel.purge(limit=num, check=haha)
        if deleted:
            await ctx.send(f'일반 유저의 메시지 {len(deleted)}개가 삭제되었어요', delete_after=2)
        else:
            await ctx.send('삭제할 일반 유저 메시지가 없네요!', delete_after=2)
bot.run(token)
