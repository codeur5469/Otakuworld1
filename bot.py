import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from keep_alive import keepalive
import asyncio

load_dotenv()
TOKEN = "MTUxNzU5MDU4Mjk1MDg4NzQzNA.GzSSnL.jivYXmkwCOvOXg4YmJZ6_QaV09pLkDfnqA3VMg"

intents = discord.Intents.default()
intents.members = True          # Indispensable pour on_raw_reaction_add
intents.message_content = True  # Pour la lecture des messages
intents.reactions = True        # Pour détecter les réactions

bot = commands.Bot(command_prefix="!", intents=intents)

# --- AJOUT : Fonction pour charger automatiquement tous les Cogs du dossier ---
async def load_extensions():
    # 1. On force le chargement du cog database en premier !
    try:
        await bot.load_extension("cogs.database")
        print("Cog database chargé en priorité.")
    except Exception as e:
        print(f"Erreur chargement priorité database : {e}")

    # 2. Ta boucle actuelle qui charge le reste (en évitant de recharger database)
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != "database.py":
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
            except Exception as e:
                print(f"Erreur lors du chargement de {filename} : {e}")

# Exemple dans ton main.py
@bot.event
async def on_ready():
    print(f"✅ {bot.user} est connecté !")
    
    # C'est cette ligne qui fait toute la magie :
    try:
        synced = await bot.tree.sync()
        print(f"🔄 {len(synced)} commandes slash synchronisées avec Discord !")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation : {e}")

# --- AJOUT : Fonction principale asynchrone pour lancer le bot ---
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

keepalive()

# On remplace bot.run(TOKEN) par l'exécution de la fonction main
asyncio.run(main())