import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from keep_alive import keepalive
import asyncio

load_dotenv()
TOKEN = os.getenv("DTOK")

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.reactions = True
        
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 1. Charger les extensions
        await self.load_extensions()
        
        # 2. Synchronisation FORCEE
        guild = discord.Object(id=1517113911810326668)
        self.tree.clear_commands(guild=guild) # <--- On vide tout le cache du serveur
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild) # <--- On renvoie tout proprement
        print("✅ Commandes totalement réinitialisées et synchronisées !")

    async def load_extensions(self):
        # Charger database en priorité
        try:
            await self.load_extension("cogs.database")
        except Exception as e:
            print(f"Erreur database : {e}")

        # Charger le reste
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != "database.py":
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                except Exception as e:
                    print(f"Erreur chargement {filename} : {e}")

async def main():
    keepalive() # Lance le serveur web
    bot = MyBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())