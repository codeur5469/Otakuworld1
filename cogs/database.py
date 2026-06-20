import discord
from discord.ext import commands
import os
from supabase import create_client, Client

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Récupération des clés dans le .env
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Erreur : Clés SUPABASE_URL ou SUPABASE_KEY manquantes dans le .env")
            self.client = None
            return

        # Connexion à Supabase
        self.client: Client = create_client(supabase_url, supabase_key)
        
        # On l'injecte dans le bot pour que les autres Cogs puissent faire "self.bot.supabase"
        self.bot.supabase = self.client
        print("✅ [Cog Database] Connexion à Supabase réussie !")

async def setup(bot):
    await bot.add_cog(Database(bot))