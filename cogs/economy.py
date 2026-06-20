import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # On cible la table "users" de Supabase
        self.db = self.bot.supabase.table("users")

    # Fonction pour récupérer ou créer le profil SQL d'un joueur
    async def get_user(self, user_id: int):
        response = self.db.select("*").eq("id", user_id).execute()
        
        if not response.data:
            # Si le joueur n'existe pas, on l'insère avec 1000 pièces par défaut
            new_user = {"id": user_id, "wallet": 1000, "last_daily": None}
            response = self.db.insert(new_user).execute()
            return response.data[0]
            
        return response.data[0]

    # Commande pour voir son solde ou celui d'un autre
    @commands.command(name="balance", aliases=["bal", "money"])
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_data = await self.get_user(member.id)
    
    # Un embed épuré avec une couleur turquoise, l'avatar et des blocs clairs
        embed = discord.Embed(
            title="💳 • INFORMATIONS BANCAIRES",
            description=f"Voici le statut économique de {member.mention}",
            color=discord.Color.from_rgb(46, 204, 113) # Vert émeraude moderne
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Organisation en blocs d'informations propres
        embed.add_field(
            name="💰 Solde Actuel", 
            value=f"```md\n# {user_data['wallet']:,} pièces\n```", 
            inline=False
        )
        
        # Petite touche de personnalisation selon la richesse
        statut = "Débutant 🪙" if user_data['wallet'] < 1000 else "Aisé 💵" if user_data['wallet'] < 10000 else "Bourgeois 💎"
        embed.add_field(name="📈 Statut Social", value=f"┕ `{statut}`", inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        await ctx.send(embed=embed)

# Commande quotidienne pour gagner de l'argent
    @commands.command(name="daily")
    async def daily(self, ctx):
        user_data = await self.get_user(ctx.author.id)
        now = datetime.now(timezone.utc)
        
        # Vérification du cooldown de 24h
        if user_data["last_daily"]:
            last_daily = datetime.fromisoformat(user_data["last_daily"].replace("+00:00", "")).replace(tzinfo=timezone.utc)
            next_daily = last_daily + timedelta(hours=24) # Cooldown de 24 heures
            
            if now < next_daily:
                # Calcul de la barre de progression (sur 24h)
                remaining = next_daily - now
                total_seconds = 24 * 3600
                passed_seconds = total_seconds - remaining.total_seconds()
                progress = int((passed_seconds / total_seconds) * 10)
                
                # Barre de progression esthétique bicolore
                bar = "▰" * progress + "▱" * (10 - progress)
                percent = int((passed_seconds / total_seconds) * 100)
                
                # Conversion de la date cible en Timestamp UNIX pour Discord (temps réel)
                target_timestamp = int(next_daily.timestamp())

                # Calcul dynamique des heures et minutes exactes restantes
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)

                embed = discord.Embed(
                    title="🕒 • RECHARGE DU COFFRE",
                    description=f"Votre bonus journalier n'est pas encore prêt, {ctx.author.mention}.",
                    color=discord.Color.from_rgb(230, 126, 34) # Orange cuivre élégant
                )
                
                # Affichage des heures/minutes calculées ET du décompte dynamique de Discord
                embed.add_field(
                    name="⏳ Temps restant", 
                    value=f"┕ **{hours}h {minutes}m** *(Prêt <t:{target_timestamp}:R>)*", 
                    inline=False
                )
                embed.add_field(
                    name="📊 Progression de la recharge", 
                    value=f"┕ `{bar}` **{percent}%**", 
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return

        reward = 200
        new_wallet = user_data["wallet"] + reward
        
        # Mise à jour dans Supabase
        self.db.update({"wallet": new_wallet, "last_daily": now.isoformat()}).eq("id", ctx.author.id).execute()
        
        embed = discord.Embed(
            title="🎁 • BONUS JOURNALIER RÉCUPÉRÉ",
            description=f"Félicitations {ctx.author.mention}, votre fidélité est récompensée !",
            color=discord.Color.from_rgb(241, 196, 15) # Or étincelant
        )
        embed.add_field(name="💵 Somme créditée", value=f"```diff\n+ {reward} pièces\n```", inline=True)
        embed.add_field(name="💳 Nouveau solde", value=f"```fix\n{new_wallet} pièces\n```", inline=True)
        embed.set_footer(text="Revenez demain à la même heure !")
        
        file = discord.File("money.gif", filename="money.gif")
        embed.set_image(url="attachment://money.gif")
        await ctx.send(file=file, embed=embed) # Remplace ton ctx.send(embed=embed) à la fin par ça

# ✨ COMMANDE DE TRANSFERT : Donner de l'argent à un autre joueur
    @commands.command(name="pay", aliases=["give"])
    async def pay(self, ctx, member: discord.Member, amount: int):
        # 1. Empêcher de se donner de l'argent à soi-même
        if member.id == ctx.author.id:
            return await ctx.send("⚠️ Vous ne pouvez pas effectuer de virement vers votre propre compte.")

        # 2. Empêcher de donner un montant invalide (négatif ou zéro)
        if amount <= 0:
            return await ctx.send("⚠️ Le montant du virement doit être supérieur à 0.")

        # 3. Récupérer les données de l'émetteur
        author_data = await self.get_user(ctx.author.id)

        # 4. Vérifier si l'émetteur a assez d'argent
        if author_data["wallet"] < amount:
            embed = discord.Embed(
                title="❌ • VIREMENT REFUSÉ",
                description="Transaction annulée pour provision insuffisante.",
                color=discord.Color.from_rgb(231, 76, 60)
            )
            embed.add_field(name="Solde actuel", value=f"`{author_data['wallet']}` pièces", inline=True)
            embed.add_field(name="Montant demandé", value=f"`{amount}` pièces", inline=True)
            return await ctx.send(embed=embed)

        # 5. Récupérer les données du destinataire
        target_data = await self.get_user(member.id)

        # 6. Calculer les nouveaux soldes
        new_author_wallet = author_data["wallet"] - amount
        new_target_wallet = target_data["wallet"] + amount

        # 7. Appliquer les changements simultanément dans Supabase
        self.db.update({"wallet": new_author_wallet}).eq("id", ctx.author.id).execute()
        self.db.update({"wallet": new_target_wallet}).eq("id", member.id).execute()

        # 8. Reçu de paiement hyper propre
        embed = discord.Embed(
            title="💸 • REÇU DE TRANSFERT",
            description="Le virement inter-bancaire a été validé avec succès.",
            color=discord.Color.from_rgb(52, 152, 219) # Bleu pro
        )
        embed.add_field(name="👤 Émetteur", value=f"{ctx.author.mention}\n`-{amount} 🪙`", inline=True)
        embed.add_field(name="👤 Destinataire", value=f"{member.mention}\n`+{amount} 🪙`", inline=True)
        embed.add_field(name="📉 Votre Nouveau Solde", value=f"```fix\n{new_author_wallet} pièces\n```", inline=False)
        
        embed.timestamp = datetime.now(timezone.utc)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))