import discord
from discord.ext import commands
from discord import app_commands
# --- FORMULAIRE DE CONFIGURATION ---
class ReactionModal(discord.ui.Modal):
    def __init__(self, db):
        super().__init__(title="Configuration Avancée")
        self.db = db
        
        # Champs existants
        self.title_input = discord.ui.TextInput(label="Titre", required=True)
        self.desc_input = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=True)
        self.emoji_input = discord.ui.TextInput(label="Émojis (séparés par ,)", placeholder="🍎, ⚔️")
        self.role_input = discord.ui.TextInput(label="IDs Rôles (séparés par ,)", placeholder="123, 456")
        
        # Nouveaux champs optionnels
        self.image_url = discord.ui.TextInput(label="URL Image (Optionnel)", required=False)
        self.msg_id_input = discord.ui.TextInput(label="ID Message existant (Optionnel)", required=False, placeholder="Laisse vide pour un nouveau message")
        
        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.emoji_input)
        self.add_item(self.role_input)
        self.add_item(self.image_url)
        self.add_item(self.msg_id_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            # 1. On sépare les entrées par une virgule
            emojis = [e.strip() for e in self.emoji_input.value.split(',')]
            role_ids = [r.strip() for r in self.role_input.value.split(',')]

            if len(emojis) != len(role_ids):
                return await interaction.followup.send("❌ Erreur : Tu dois mettre autant d'émojis que d'IDs de rôles.", ephemeral=True)

            # 2. Création de l'embed
            embed = discord.Embed(title=self.title_input.value, description=self.desc_input.value, color=discord.Color.blue())
            
            # On ajoute un texte explicatif dans le footer
            embed.set_footer(text="Réagissez pour obtenir votre rôle.")
            msg = await interaction.channel.send(embed=embed)

            # 3. Boucle pour traiter chaque paire Emoji/Rôle
            for emoji, r_id_str in zip(emojis, role_ids):
                # Nettoyage de l'ID
                clean_id = ''.join(filter(str.isdigit, r_id_str))
                role = interaction.guild.get_role(int(clean_id))
                
                if role:
                    await msg.add_reaction(emoji)
                    # Insertion dans Supabase
                    self.db.insert({
                        "message_id": str(msg.id),
                        "emoji": str(emoji),
                        "role_id": str(role.id)
                    }).execute()

            await interaction.followup.send(f"✅ Embed créé avec {len(emojis)} rôles configurés !", ephemeral=True)

        except Exception as e:
            print(f"DEBUG ERREUR : {e}")
            await interaction.followup.send(f"❌ Une erreur est survenue : {e}", ephemeral=True)

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Assure-toi que bot.supabase existe bien ici
        self.db = self.bot.supabase.table("reaction_roles") 

    @app_commands.command(name="setup_reaction", description="Configure un rôle de réaction")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def setup_reaction(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ReactionModal(self.db))

    # --- LISTENERS ---
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Ignorer si c'est le bot qui réagit
        if payload.user_id == self.bot.user.id: 
            return

        # 1. Conversion explicite en STR pour correspondre à ta BDD
        msg_id_str = str(payload.message_id)
        emoji_str = str(payload.emoji)

        print(f"DEBUG: Réaction sur {msg_id_str} avec {emoji_str}")

        # 2. Requête sécurisée
        response = self.db.select("role_id").eq("message_id", msg_id_str).eq("emoji", emoji_str).execute()
        
        print(f"DEBUG: Résultat BDD = {response.data}")

        if response.data:
            role_id = int(response.data[0]["role_id"])
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            
            if role and member:
                await member.add_roles(role)
                print(f"✅ Rôle {role.name} ajouté à {member.name}")
            else:
                print(f"❌ Erreur : Rôle ({role_id}) ou membre introuvable.")


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # 1. Conversion des données pour la recherche
        msg_id_str = str(payload.message_id)
        emoji_str = str(payload.emoji)

        # 2. Chercher quel rôle correspond à ce message + cet émoji
        response = self.db.select("role_id").eq("message_id", msg_id_str).eq("emoji", emoji_str).execute()
        
        if response.data:
            role_id = int(response.data[0]["role_id"])
            guild = self.bot.get_guild(payload.guild_id)
            if not guild: return
            
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            
            # 3. Retirer le rôle si le membre et le rôle existent
            if role and member:
                try:
                    await member.remove_roles(role)
                    print(f"✅ Rôle {role.name} retiré à {member.name}")
                except Exception as e:
                    print(f"❌ Erreur lors du retrait : {e}")

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))