import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from keep_alive import keepalive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_member_join(member):
    # Channel 1
    channel1 = member.guild.get_channel(1495041626798817443)
    if channel1:
        message = f"Bienvenue {member.mention} sur le serveur !"
        try:
            file = discord.File("gen.gif")
            await channel1.send(content=message, file=file)
        except Exception as e:
            print(f"Erreur channel1 : {e}")

    # Channel 2
    channel2 = member.guild.get_channel(1495055776216121425)
    if channel2:
        message = f"Bienvenue {member.name} sur le serveur !"
        try:
            file = discord.File("welcome.gif")
            await channel2.send(content=message, file=file)
        except Exception as e:
            print(f"Erreur channel2 : {e}")

@bot.event
async def on_member_remove(member):
    channel = member.guild.get_channel(1495055943417856000)
    
    if channel:
        message = f"**{member.name}** vient de quitter le serveur. 👋"
        try:
            file = discord.File("bye.gif")
            await channel.send(content=message, file=file)
        except Exception as e:
            print(f"Erreur : {e}")

keepalive()
bot.run(TOKEN)