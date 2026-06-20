import discord
from discord.ext import commands
from datetime import datetime, timezone

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot, prefix):
        # Définition des options disponibles dans le menu déroulant
        options = [
            discord.SelectOption(
                label="Accueil", 
                description="Retourner au menu d'aide principal", 
                emoji="📚"
            ),
            discord.SelectOption(
                label="Économie", 
                description="Commandes de banque et transactions", 
                emoji="💰"
            ),
            discord.SelectOption(
                label="Casino", 
                description="Jeux de hasard et de mise", 
                emoji="🎰"
            ),
        ]
        super().__init__(
            placeholder="Choisissez une catégorie à afficher...", 
            min_values=1, 
            max_values=1, 
            options=options
        )
        self.bot = bot
        self.prefix = prefix

    async def callback(self, interaction: discord.Interaction):
        # On récupère le choix sélectionné
        value = self.values[0]
        embed = None

        if value == "Accueil":
            embed = discord.Embed(
                title="📚 • MENU D'AIDE DU BOT",
                description=(
                    f"Sélectionnez une catégorie dans le menu déroulant ci-dessous pour voir les commandes disponibles.\n\n"
                    f"**Légende :**\n"
                    f"┕ `<paramètre>` : Obligatoire.\n"
                    f"┕ `[paramètre]` : Optionnel."
                ),
                color=discord.Color.from_rgb(52, 152, 219) # Bleu moderne
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(name="💰 • ÉCONOMIE", value="*Commandes liées à votre solde et virements.*", inline=True)
            embed.add_field(name="🎰 • CASINO", value="*Tentez de doubler vos pièces avec nos jeux !*", inline=True)

        elif value == "Économie":
            embed = discord.Embed(
                title="💰 • CATÉGORIE ÉCONOMIE",
                description="Gérez votre argent et effectuez des transferts sécurisés.",
                color=discord.Color.from_rgb(46, 204, 113) # Vert émeraude
            )
            embed.add_field(
                name=f"`{self.prefix}balance [membre]`", 
                value="┕ Consulez votre solde bancaire ou celui d'un autre joueur.", 
                inline=False
            )
            embed.add_field(
                name=f"`{self.prefix}daily`", 
                value="┕ Réclamez votre bonus quotidien gratuit (cooldown de 24h).", 
                inline=False
            )
            embed.add_field(
                name=f"`{self.prefix}pay <membre> <montant>`", 
                value="┕ Transférez des pièces de votre compte à un autre joueur.", 
                inline=False
            )

        elif value == "Casino":
            embed = discord.Embed(
                title="🎰 • CATÉGORIE CASINO",
                description="Misez vos pièces sur nos jeux de hasard interactifs.",
                color=discord.Color.from_rgb(241, 196, 15) # Or étincelant
            )
            # Ajout des guides pour les futures commandes du Casino
            embed.add_field(
                name=f"`{self.prefix}roulette <montant> <choix>`", 
                value="┕ Pariez vos pièces sur une couleur (red/black) ou un numéro.", 
                inline=False
            )
            embed.add_field(
                name=f"`{self.prefix}slots <montant>`", 
                value="┕ Lancez la machine à sous et tentez d'aligner les symboles.", 
                inline=False
            )
            embed.add_field(
                name=f"`{self.prefix}blackjack <montant>`", 
                value="┕ Affrontez le croupier et tentez de vous approcher de 21 sans le dépasser.", 
                inline=False
            )

        embed.set_footer(text="Format : <requis> | [optionnel]")
        embed.timestamp = datetime.now(timezone.utc)
        
        # On met à jour l'embed sans renvoyer un nouveau message
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, bot, prefix, author_id, timeout=60):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.message = None
        # On ajoute le menu déroulant à la vue
        self.add_item(HelpDropdown(bot, prefix))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Seul l'utilisateur qui a fait la commande d'aide peut l'utiliser
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ Seul l'auteur de la commande d'aide peut utiliser ce menu déroulant !", 
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        # Désactive le menu déroulant pour éviter des interactions inutiles après l'expiration
        for item in self.children:
            item.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # On désactive la commande d'aide par défaut de discord.py
        self.bot.help_command = None

    @commands.command(name="help", aliases=["aide"])
    async def help(self, ctx, command_name: str = None):
        prefix = ctx.prefix

        # --- CAS 1 : L'utilisateur demande l'aide globale ---
        if not command_name:
            embed = discord.Embed(
                title="📚 • MENU D'AIDE DU BOT",
                description=(
                    f"Sélectionnez une catégorie dans le menu déroulant ci-dessous pour voir les commandes disponibles.\n\n"
                    f"**Légende :**\n"
                    f"┕ `<paramètre>` : Obligatoire.\n"
                    f"┕ `[paramètre]` : Optionnel."
                ),
                color=discord.Color.from_rgb(52, 152, 219) # Bleu moderne
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(name="💰 • ÉCONOMIE", value="*Commandes liées à votre solde et virements.*", inline=True)
            embed.add_field(name="🎰 • CASINO", value="*Tentez de doubler vos pièces avec nos jeux !*", inline=True)

            embed.set_footer(text=f"Demandé par {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.now(timezone.utc)

            # Création de la vue interactive
            view = HelpView(self.bot, prefix, ctx.author.id)
            view.message = await ctx.send(embed=embed, view=view)
            return

        # --- CAS 2 : L'utilisateur demande l'aide sur une commande précise ---
        command_name = command_name.lower()
        cmd = self.bot.get_command(command_name)

        if not cmd:
            embed = discord.Embed(
                title="❌ • COMMANDE INTROUVABLE",
                description=f"La commande `{command_name}` n'existe pas ou a été mal orthographiée.",
                color=discord.Color.from_rgb(231, 76, 60) # Rouge
            )
            return await ctx.send(embed=embed)

        # Configuration des détails de la commande demandée
        embed = discord.Embed(
            title=f"📖 • COMMANDE : {cmd.name.upper()}",
            color=discord.Color.from_rgb(46, 204, 113) # Vert
        )

        details = {
            "balance": {
                "desc": "Affiche votre solde de pièces ou celui d'un autre membre du serveur.",
                "usage": f"`{prefix}balance [membre]`",
                "params": [
                    ("`[membre]` *(Optionnel)*", "Le joueur dont vous voulez voir le solde. Si vide, affiche votre propre solde.")
                ]
            },
            "daily": {
                "desc": "Vous permet de réclamer votre bonus de pièces quotidien gratuit toutes les 24 heures.",
                "usage": f"`{prefix}daily`",
                "params": []
            },
            "pay": {
                "desc": "Transfère de manière sécurisée une somme de pièces de votre compte vers celui d'un autre joueur.",
                "usage": f"`{prefix}pay <membre> <montant>`",
                "params": [
                    ("`<membre>` *(Obligatoire)*", "Mention ou ID du destinataire du virement."),
                    ("`<montant>` *(Obligatoire)*", "Le nombre entier de pièces à envoyer (doit être supérieur à 0 et disponible sur votre solde).")
                ]
            }
        }

        cmd_info = details.get(cmd.name)

        if cmd_info:
            embed.description = cmd_info["desc"]
            embed.add_field(name="⚙️ Syntaxe", value=cmd_info["usage"], inline=False)
            
            if cmd_info["params"]:
                params_text = ""
                for param_name, param_desc in cmd_info["params"]:
                    params_text += f"• **{param_name}** : {param_desc}\n"
                embed.add_field(name="📋 Paramètres", value=params_text, inline=False)
        else:
            embed.description = cmd.help or "Aucune description fournie pour cette commande."
            embed.add_field(name="⚙️ Syntaxe", value=f"`{prefix}{cmd.name} {cmd.signature}`", inline=False)

        aliases = cmd.aliases
        if aliases:
            embed.add_field(name="🔗 Raccourcis", value=", ".join([f"`{a}`" for a in aliases]), inline=False)

        embed.set_footer(text=f"Format : <requis> | [optionnel]")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))