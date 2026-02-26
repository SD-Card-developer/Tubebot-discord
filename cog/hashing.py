import hashlib
from discord.ext import commands

class HashTool(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="해시만들기")
    async def create_hash(self, ctx, *, text: str):
        # 해시를 만드는 명령어 그자체는 Ai가 작성(내가 hashlib를 모름)
        hash_object = hashlib.sha256(text.encode())
        hash = hash_object.hexdigest()
        await ctx.send(f"**입력값:** {text} \n **SHA-256 해시 결과:** `{hash}`")
        await ctx.send(f"")

def setup(bot):
    bot.add_cog(HashTool(bot))
