from discord.ext import commands


class Demo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Ping command, latency of the bot"""

        await ctx.send(f":ping_pong: Pong! {str(round(self.bot.latency * 1000, 0))[:2]}ms :signal_strength:")

    @commands.command()
    async def test(self, ctx):
        """Test command, disabled in features.yml by default"""

        await ctx.send("Test command!")


def setup(bot):
    bot.add_cog(Demo(bot))
