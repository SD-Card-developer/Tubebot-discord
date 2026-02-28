import discord
import discord.ext
from discord import app_commands

# shared 라이브러리 예시
command = app_commands.command
des = app_commands.describe

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

async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """지정된 팀 리스트에게만 시스템 에러를 보고하는 핸들러"""
    
    # 권한 부족은 사용자에게만 알림 (팀원들에게 알릴 필요 없음)
    if isinstance(error, app_commands.MissingPermissions):
        await send(interaction, "❌ 이 명령어를 실행할 권한이 없습니다.", ephemeral=True)
        return

    error_message = (
        f"⚠️ **[시스템 에러 발생]**\n"
        f"**명령어**: /{interaction.command.name}\n"
        f"**발생자**: {interaction.user.name}\n"
        f"**에러 내용**: ```{error}```"
    )

    for user_id in TEAM_LIST:
        try:
            user = interaction.client.get_user(user_id) or await interaction.client.fetch_user(user_id)
            if user:
                await send(user, error_message)
        except Exception as e:
            # DM이 닫혀 있거나 등의 이유로 실패할 경우 로그만 남김
            print(f"팀원({user_id})에게 에러 전송 실패: {e}")
