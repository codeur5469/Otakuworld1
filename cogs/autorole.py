import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# --- FORMULAIRE SIMPLIFIÉ ---
class ReactionModal(discord.ui.Modal):
    def __init__(self, db):
        super().__init__(title="Configuration Rôles")
        self.db = db
        
        self.title_input = discord.ui.TextInput(label="Titre", required=True)
        self.desc_input = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=True)
        self.emoji_input = discord.ui.TextInput(label="Émojis (séparés par ,)", placeholder="🍎, ⚔️")
        self.role_input = discord.ui.TextInput(label="IDs Rôles (séparés par ,)", placeholder="123, 456")
        
        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.emoji_input)
        self.add_item(self.role_input)

    async def on_submit(self, interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            # Création de l'embed simple
            embed = discord.Embed(
                title=self.title_input.value, 
                description=self.desc_input.value, 
                color=discord.Color.blue()
            )
            embed.set_footer(text="Réagissez pour obtenir votre rôle.")
            msg = await interaction.channel.send(embed=embed)

            # Traitement des emojis et rôles
            emojis = [e.strip() for e in self.emoji_input.value.split(',')]
            role_ids = [r.strip() for r in self.role_input.value.split(',')]

            if len(emojis) != len(role_ids):
                return await interaction.followup.send("❌ Erreur : Le nombre d'émojis et de rôles doit correspondre.", ephemeral=True)

            for emoji, r_id_str in zip(emojis, role_ids):
                clean_id = ''.join(filter(str.isdigit, r_id_str))
                role = interaction.guild.get_role(int(clean_id))
                
                if role:
                    await msg.add_reaction(emoji)
                    self.db.insert({
                        "message_id": str(msg.id),
                        "emoji": str(emoji),
                        "role_id": str(role.id)
                    }).execute()
            
            await interaction.followup.send("✅ Rôles configurés avec succès !", ephemeral=True)

        except Exception as e:
            print(f"DEBUG ERREUR : {e}")
            await interaction.followup.send(f"❌ Une erreur est survenue : {e}", ephemeral=True)

# --- COG ---
class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.supabase.table("reaction_roles") 

    @app_commands.command(name="setup_reaction", description="Configure un rôle de réaction")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def setup_reaction(self, interaction):
        await interaction.response.send_modal(ReactionModal(self.db))

    # --- LISTENERS (inchangés) ---
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id: return
        msg_id_str = str(payload.message_id)
        emoji_str = str(payload.emoji)
        response = self.db.select("role_id").eq("message_id", msg_id_str).eq("emoji", emoji_str).execute()
        if response.data:
            role_id = int(response.data[0]["role_id"])
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if role and member: await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        msg_id_str = str(payload.message_id)
        emoji_str = str(payload.emoji)
        response = self.db.select("role_id").eq("message_id", msg_id_str).eq("emoji", emoji_str).execute()
        if response.data:
            role_id = int(response.data[0]["role_id"])
            guild = self.bot.get_guild(payload.guild_id)
            if not guild: return
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if role and member: await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))