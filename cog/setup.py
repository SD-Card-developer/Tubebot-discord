import discord
from discord import app_commands
from discord.ext import commands
from libs.easyfile import json_write

embed_1 = discord.Embed(
    title=f"욕 검열을 하시겠어요?",
    description="이 서버에서 욕을 검열합니다", color=0x2b2d31)
embed_2 = discord.Embed(
    title=f"도배를 막으시겠어요?",
                        description="이 서버에서 도배를 검열합니다", color=0x2b2d31)
embed_3 = discord.Embed(
    title=f"욕설 화이트리스트 설정",
    description="욕설을 검열하는 기능에서\n 제외할 채널을 선택하세요.\n 나중에 선택이 가능합니다", color=0x2b2d31)
embed_4 = discord.Embed(
    title=f"도배 화이트리스트 설정",
    description="도배 메시지를 검열하는 기능에서\n 제외할 채널을 선택하세요.\n 나중에 선택이 가능합니다", color=0x2b2d31)
embed_5 = discord.Embed(
    title=f"설정 완료",
    description="설정이 완료되었어요!\n이제 서버를 쾌적하게 이용하시면 됩니다!", color=0x2b2d31)
embed_list = [None, embed_1, embed_2, embed_3, embed_4, embed_5]

class StartView(discord.ui.View):
    def __init__(self, bot, guild_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = str(guild_id)
        self.step = 0
        self.guild_int = int(self.guild_id)
        if not hasattr(self.bot, 'setting'):
            self.bot.setting = {}

        if self.guild_id not in self.bot.setting:
            self.bot.setting[self.guild_id] = {'bw': False, 'spam': False, 'wl': [], 'wl_s': []}
    def start(self):
        self.clear_items()
        if self.step == 0:
            async def if_go(interaction: discord.Interaction):
                self.step += 1
                self.start()
                await interaction.response.edit_message(
                    embed=embed_list[self.step],
                    view=self
                )
            btn_yes = discord.ui.Button(label="갑시다", style=discord.ButtonStyle.green)
            btn_yes.callback = if_go
            self.add_item(btn_yes)

        if self.step == 1: # 진짜 시작
            async def if_yes(interaction: discord.Interaction):
                self.bot.setting[self.guild_id]['bw'] = True
                self.step = 3
                self.start()
                await interaction.response.edit_message(
                    embed=embed_list[3],
                    view=self
                )
            async def if_no(interaction: discord.Interaction):
                self.bot.setting[self.guild_id]['bw'] = False
                self.step = 2
                self.start()
                await interaction.response.edit_message(
                    embed=embed_list[self.step],
                    view=self
                )
            btn_yes = discord.ui.Button(label="네", style=discord.ButtonStyle.green)
            btn_yes.callback = if_yes
            btn_no = discord.ui.Button(label="아니오", style=discord.ButtonStyle.red)
            btn_no.callback = if_no
            self.add_item(btn_yes)
            self.add_item(btn_no)

        if self.step == 2:
            async def if_yes(interaction: discord.Interaction):
                self.bot.setting[self.guild_id]['spam'] = True
                self.step = 4
                self.start()
                await interaction.response.edit_message(
                    embed=embed_list[4],
                    view=self
                )
            async def if_no(interaction: discord.Interaction):
                self.bot.setting[self.guild_id]['spam'] = False
                self.step = 5
                self.start()
                await interaction.response.edit_message(
                    embed=embed_list[5],
                    view=None
                )
            btn_yes = discord.ui.Button(label="네", style=discord.ButtonStyle.green)
            btn_yes.callback = if_yes
            btn_no = discord.ui.Button(label="아니요", style=discord.ButtonStyle.red)
            btn_no.callback = if_no
            self.add_item(btn_yes)
            self.add_item(btn_no)
        if self.step == 3:
            if self.bot.setting[self.guild_id]['bw']:
                select = discord.ui.ChannelSelect(
                    placeholder="검열에서 제외할 채널을 선택하세요...",
                    min_values=0,
                    max_values=10
                )
                async def select_callback(itn: discord.Interaction):
                     # 선택한 채널들의 ID를 리스트에 저장
                    self.bot.setting[self.guild_id]['wl'] = [ch.id for ch in select.values]
                    self.step = 2
                    self.start()
                    await itn.response.edit_message(embed=embed_list[self.step], view=self)
                select.callback = select_callback
                self.add_item(select)
        if self.step == 4:
            if self.bot.setting[self.guild_id]['spam']:
                select = discord.ui.ChannelSelect(
                    placeholder="검열에서 제외할 채널을 선택하세요...",
                    min_values=0,
                    max_values=10
                )
                async def select_callback(itn: discord.Interaction):
                    # 선택한 채널들의 ID를 리스트에 저장
                    self.bot.setting[self.guild_id]['wl_s'] = [ch.id for ch in select.values]
                    self.step = 5
                    self.start()
                    await itn.response.edit_message(embed=embed_list[self.step], view=self)
                    data = self.bot.setting[self.guild_id]
                    json_write('whitelist.json',
                               {self.guild_id:self.bot.setting[self.guild_id]['wl']})
                    json_write('whitelist_s.json',
                               {self.guild_id:self.bot.setting[self.guild_id]['wl_s']})
                    config_data = {self.guild_id: {'bw': data['bw'], 'spam': data['spam']}}
                    json_write("config.json", config_data)
                select.callback = select_callback
                self.add_item(select)

class SetupConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="시작하기", description="서버 초기 설정을 시작합니다.")
    @app_commands.checks.has_permissions(administrator=True)
    async def start_setup(self, itn: discord.Interaction):
        view = StartView(bot=self.bot, guild_id=itn.guild_id or 0) # 뷰 만들기
        view.start() # 시작
        embed = discord.Embed(title="설정 시작",
                              description="아래 버튼을 눌러주세요.\n 시작하기를 하지 않으면\n봇의 기능을 이용하기 어렵습니다",
                              color=0x2b2d31)
        await itn.response.send_message(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupConfig(bot))