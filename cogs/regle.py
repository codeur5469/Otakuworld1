import discord
from discord.ext import commands
from datetime import datetime

class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="regle")
    async def regle(self, ctx):
        """Affiche le règlement du serveur et supprime la commande."""
        # Suppression du message de commande
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass # Si le bot n'a pas la permission de supprimer le message
        except discord.HTTPException:
            pass

        # Création de l'embed
        embed = discord.Embed(
            title="📜 𝐑𝐄̀𝐆𝐋𝐄𝐌𝐄𝐍𝐓 𝐃𝐄 𝐊𝐔𝐌𝐎 ☁️",
            description=(
                "**1️⃣ Respect**\nRespectez tous les membres. Les insultes, provocations, discriminations et le harcèlement sont interdits.\n\n"
                "**2️⃣ Contenu**\nTout contenu NSFW, choquant, illégal ou inapproprié est strictement interdit.\n\n"
                "**3️⃣ Spam**\nLe spam, les messages inutiles, les mentions abusives et la publicité non autorisée sont interdits.\n\n"
                "**4️⃣ Pseudonymes & Profils**\nLes pseudos, photos de profil et statuts doivent rester corrects et respectueux.\n\n"
                "**5️⃣ Salons**\nUtilisez les salons pour leur utilisation prévue et évitez le hors-sujet excessif.\n\n"
                "**6️⃣ Vocaux**\nRespectez les autres utilisateurs en vocal. Les cris, soundboards abusifs et nuisances sonores sont interdits.\n\n"
                "**7️⃣ Staff**\nLes décisions du staff doivent être respectées. En cas de problème, ouvrez un ticket.\n\n"
                "**8️⃣ Partenariats & Publicités**\nToute publicité ou demande de partenariat doit passer par les salons ou tickets prévus à cet effet.\n\n"
                "**9️⃣ Discord TOS**\nLe règlement de Discord s’applique également sur Kumo.\n\n"
                "**🔟 Bon sens**\nLe respect, la maturité et le bon sens sont attendus de tous.\n\n"
                "⚠️ Le non-respect de ces règles peut entraîner une sanction."
            ),
        )
        
        embed.set_footer(text="☁️ Profitez de votre séjour sur Kumo et amusez-vous !")
        embed.set_image(url="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExdnFrYnJ0Mmx0cTZrYXU1MWUweXViOXhnNTU1M2FybWZtZXhkZHVxdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/e9U5tYwBssdLG/giphy.gif")

        # Envoi de l'embed
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Reglement(bot))
