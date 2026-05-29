import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from keep_alive import keepalive
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_member_join(member):
    # Channel 2
    channel2 = member.guild.get_channel(1495055776216121425)
    if channel2:
        message = f"Bienvenue {member.mention} sur le serveur !"
        try:
            file = discord.File("welcome.gif")
            await channel2.send(content=message, file=file)
        except Exception as e:
            print(f"Erreur channel2 : {e}")
    
    channel3 = member.guild.get_channel(1495120367365390456)
    if channel3:
        message = f"{member.mention}"
        try:
            msg = await channel3.send(content=message)
            await asyncio.sleep(2)
            await msg.delete()
        except Exception as e:
            print(f"Erreur channel3 : {e}")

keepalive()
bot.run(TOKEN)