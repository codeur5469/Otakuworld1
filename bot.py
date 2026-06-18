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

# --- AJOUT : Fonction pour charger automatiquement tous les Cogs du dossier ---
async def load_extensions():
    # os.path.exists évite une erreur si le dossier n'est pas encore créé
    if os.path.exists('./cogs'):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Cog chargé avec succès : {filename}")
    else:
        print("Erreur : Le dossier 'cogs' n'existe pas au même niveau que ce fichier.")

# --- AJOUT : Fonction principale asynchrone pour lancer le bot ---
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

keepalive()

# On remplace bot.run(TOKEN) par l'exécution de la fonction main
asyncio.run(main())