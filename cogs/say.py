import discord
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say")
    async def say(self, ctx, *, message: str):
        """Répète le message envoyé par l'utilisateur."""
        # Supprime le message de l'utilisateur pour ne laisser que la réponse du bot
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass # Si le bot n'a pas la permission de supprimer
        
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(Say(bot))