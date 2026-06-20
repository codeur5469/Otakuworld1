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
        await self.load_extensions()
        
        guild = discord.Object(id=1517113911810326668)
        
        self.tree.copy_global_to(guild=guild)  # AJOUTE CETTE LIGNE
        
        try:
            await self.tree.sync(guild=guild)
            print(f"✅ Commandes synchronisées avec le serveur {guild.id}")
        except Exception as e:
            print(f"❌ ERREUR DE SYNCHRO : {e}")

    async def load_extensions(self):
        try:
            await self.load_extension("cogs.database")
        except Exception as e:
            print(f"Erreur database : {e}")
            raise  # stoppe tout, sans DB rien marche

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != "database.py":
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✅ {filename} chargé")
                except Exception as e:
                    print(f"❌ Erreur chargement {filename} : {e}")

async def main():
    keepalive() # Lance le serveur web
    bot = MyBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())