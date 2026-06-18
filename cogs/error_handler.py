import discord
from discord.ext import commands

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Cet événement écoute toutes les erreurs qui se produisent lors de l'exécution d'une commande
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        
        # 1. Gestion de l'erreur : Commande inconnue (ex: !color au lieu de !colors)
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="❌ Commande inconnue",
                description=(
                    f"La commande que tu as tapée n'existe pas.\n"
                    f"Vérifie l'orthographe ou tape `{ctx.prefix}help` pour voir la liste des commandes disponibles."
                ),
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10) # Supprime le message après 10s pour ne pas polluer
            return

        # 2. Gestion de l'erreur : Permissions manquantes (ex: un membre non-admin fait !colors)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="⛔ Accès refusé",
                description="Tu n'as pas les permissions nécessaires (Administrateur) pour exécuter cette commande.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, delete_after=10)
            return

        # 3. Gestion de l'erreur : Mauvais arguments passés à une commande
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="⚠️ Mauvaise utilisation",
                description="Les arguments fournis pour cette commande sont incorrects ou manquants.",
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed, delete_after=10)
            return

        # 4. Gestion de toutes les autres erreurs (erreurs de code, bugs internes...)
        else:
            # On affiche l'erreur dans la console pour que TU puisses la voir et la corriger
            print(f"Erreur non gérée dans la commande '{ctx.command}': {error}")
            
            # On prévient gentiment l'utilisateur que le bot a eu un problème
            embed = discord.Embed(
                title="💥 Une erreur est survenue",
                description="Une erreur interne a empêché l'exécution correcte de cette commande. Les développeurs ont été prévenus.",
                color=discord.Color.dark_red()
            )
            await ctx.send(embed=embed, delete_after=10)

async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))