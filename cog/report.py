from discord import app_commands
import discord
from discord.ext import commands
from libs.easyfile import json_write


class MyView(discord.ui.View):
    def __init__(self, bot, target_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.target_id = target_id

    @discord.ui.button(label="승인", style=discord.ButtonStyle.green, custom_id="good_btn")
    async def good_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ 신고가 승인되었습니다", ephemeral=True)
        for guild_id in self.bot.security_channels:
            channels_list = self.bot.security_channels[guild_id]

            for c_id in channels_list:
                chan = self.bot.get_channel(c_id)
                if chan:
                    try:
                        await chan.send(f'<@{self.target_id}>은 신고된 악성 유저입니다! \n'
                                        f'서버에 들어오면 밴해야 합니다.')
                    except Exception as e:
                        await interaction.channel.send(f"❌ {c_id} 전송 실패: {e}")
        target_str = str(self.target_id)
        current_warns = self.bot.warnlist.get(target_str, 0)
        self.bot.warnlist[target_str] = current_warns + 60
        json_write('warn.json', self.bot.warnlist)
        button.disabled = True
        button.label = "처리 완료"
        await interaction.message.edit(view=self)

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnlist = bot.warnlist

    @app_commands.command(name="신고", description="증거 사진과 함께 유저를 신고합니다.")
    async def report(self,interaction: discord.Interaction, target: discord.Member, reason: str,
                     evidence: discord.Attachment):
        embed = discord.Embed(title="📢 [외부 서버 신고 접수]", color=0xff0000, timestamp=discord.utils.utcnow())
        embed.add_field(name="피신고자", value=f"{target.mention} (`{target.id}`)", inline=True)
        embed.add_field(name="신고자", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=True)
        embed.add_field(name="발생 서버", value=f"**{interaction.guild.name}** (`{interaction.guild.id}`)", inline=False)
        embed.add_field(name="신고 사유", value=f"```{reason}```", inline=False)
        embed.set_image(url=evidence.url)
        embed.set_footer(text="팀장님 전용 보안 브리핑")

        report_chan = self.bot.get_channel(1477166890391441408)
        await interaction.response.send_message(
            "✅ 신고가 접수되었습니다. 관리진이 검토 후 조치하겠습니다.",
            ephemeral=True
        )
        if report_chan:
            view = MyView(self.bot, target.id)  # 피신고자 ID 전달
            await report_chan.send(embed=embed, view=view)
            try:
                await target.send(f"🚨 당신이 다른 사람에게 신고되었습니다. 사유: {reason}"
                                  f"\n -# 이 메시지는 튜브봇이 자동으로 보낸 메시지입니다")
            except discord.Forbidden:
                await interaction.followup.send(content= "이 유저는 DM을 차단해서 메시지를 못 보냈어요!", ephemeral=True)
            except AttributeError:
                await interaction.followup.send(content='어디한번 해봐라 내가 신고 되나!', ephemeral=True)

        else:
            # 채널을 못 찾을 경우를 대비한 에러 처리
            await interaction.response.send_message("⚠️ 시스템 오류로 신고 전송에 실패했습니다. 다시 시도해주세요.", ephemeral=True)
async def setup(bot):
    await bot.add_cog(Report(bot))