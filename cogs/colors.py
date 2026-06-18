import discord
from discord.ext import commands

class ColorReactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # ⚠️ METS L'ID DU MESSAGE DE L'EMBED ICI APRÈS L'AVOIR ENVOYÉ AVEC !colors
        self.target_message_id = 111111111111111111 

        # Dictionnaire qui associe chaque émoji à l'ID de son rôle
        self.emoji_to_role = {
            "❤️": 1517218811160563853,  # Rouge
            "💙": 1517218887848951838,  # Bleu
            "💚": 1517218966706323576,  # Vert
            "💜": 1517219218091671652,  # Violet
            "🧡": 1517219254120878321,  # Orange
            "💛": 1517219302040670419,  # Jaune
            "🩷": 1517219345195860199,  # Rose
            "🤍": 1517221230124601424,  # blanc
            "🖤": 1517221182670114889,  # noir
            "🩶": 1517221286462357518,  # gris
        }

    @commands.Cog.listener()
    async def on_ready(self):
        print("Système de rôles par réactions prêt !")

    # 1. Quand un membre AJOUTE une réaction
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # On vérifie que c'est bien le bon message
        if payload.message_id != self.target_message_id:
            return

        # On ignore si c'est le bot qui réagit
        if payload.user_id == self.bot.user.id:
            return

        emoji_name = str(payload.emoji)
        if emoji_name in self.emoji_to_role:
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return

            role = guild.get_role(self.emoji_to_role[emoji_name])
            member = guild.get_member(payload.user_id)

            if role and member:
                try:
                    await member.add_roles(role)
                    print(f"Rôle {role.name} ajouté à {member.name}")
                except Exception as e:
                    print(f"Erreur lors de l'ajout du rôle : {e}")

    # 2. Quand un membre RETIRE sa réaction
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id != self.target_message_id:
            return

        emoji_name = str(payload.emoji)
        if emoji_name in self.emoji_to_role:
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return

            role = guild.get_role(self.emoji_to_role[emoji_name])
            member = guild.get_member(payload.user_id)

            if role and member:
                try:
                    await member.remove_roles(role)
                    print(f"Rôle {role.name} retiré à {member.name}")
                except Exception as e:
                    print(f"Erreur lors du retrait du rôle : {e}")

    # 3. Commande pour envoyer l'embed initial
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def colors(self, ctx):
        embed = discord.Embed(
            title="🎨 Choisis ta couleur via les Réactions !",
            description=(
                "Ajoute une réaction avec l'émoji correspondant pour obtenir ta couleur.\n"
                "Retire ta réaction pour perdre la couleur !\n\n"
                "❤️ **Rouge**  | 💙 **Bleu**  | 💚 **Vert**\n"
                "💜 **Violet** \n"
                "🧡 **Orange**  | 💛 **Jaune**  | 🩷 **Rose** \n"
                "🖤 **Noir**  | 🤍 **Blanc**  | 🩶 **Gris** \n"
            ),
            color=0x2F3136
        )
        embed.set_footer(text="Réagis pour obtenir ton rôle")
        
        # On envoie l'embed
        msg = await ctx.send(embed=embed)
        
        # Le bot ajoute automatiquement toutes les réactions sous l'embed pour que les utilisateurs cliquent juste dessus
        for emoji in self.emoji_to_role.keys():
            await msg.add_reaction(emoji)
            
        print(f"Message envoyé ! Copie cet ID et mets le à la ligne 14 : {msg.id}")
async def setup(bot):
    await bot.add_cog(ColorReactions(bot))