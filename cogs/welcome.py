import discord
from discord.ext import commands
import asyncio

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Channel 2
        channel2 = member.guild.get_channel(1517126171010007113)
        if channel2:
            message = f"Bienvenue {member.mention} sur le serveur !"
            try:
                file = discord.File("3.gif")
                await channel2.send(content=message, file=file)
            except Exception as e:
                print(f"Erreur channel2 : {e}")
        
        # Channel 3
        channel3 = member.guild.get_channel(1517129461038977107)
        if channel3:
            message = f"{member.mention}"
            try:
                msg = await channel3.send(content=message)
                await asyncio.sleep(2)
                await msg.delete()
            except Exception as e:
                print(f"Erreur channel3 : {e}")

# Fonction obligatoire pour charger le cog
async def setup(bot):
    await bot.add_cog(Welcome(bot))
