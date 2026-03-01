import discord
from discord.ext import commands
import discord.ext
from discord import app_commands

# shared 라이브러리 예시
command = app_commands.command
des = app_commands.describe
hybrid = commands.hybrid_command

def quick_button(label, callback_func, style=discord.ButtonStyle.gray):
    """클래스 없이 버튼을 생성하는 함수"""
    class TempView(discord.ui.View):
        def __init__(self):
            super().__init__()
            btn = discord.ui.Button(label=label, style=style)
            btn.callback = callback_func
            self.add_item(btn)
    return TempView()

async def send(bot, target, content, ephemeral=False):
  #타겟이 채널
    if isinstance(target, int):
        channel = bot.get_channel(target)
        if channel:
            return await channel.send(content)
# 타겟이 슬래시
    elif hasattr(target, "response"):
        if not target.response.is_done():
            return await target.response.send_message(content, ephemeral=ephemeral)
        else:
            return await target.followup.send(content, ephemeral=ephemeral)
# 타겟이 메시지일때
    elif hasattr(target, "send"):
        return await target.send(content)
      
# 1. 우리 팀원들의 디스코드 ID 리스트 (냥밥, 6090 등)
TEAM_LIST = [1412764683303391354, 1342787881927704577,1418797530807930940]


def m(m_id: int):
    bot_ref = getattr(discord.Object, 'bots', None)
    if not bot_ref:
        return None

    msg = discord.utils.get(bot_ref.cached_messages, id=m_id)
    return msg.channel if msg else None

def get_chan(bot, channel_id: int):
    return bot.get_channel(channel_id)
