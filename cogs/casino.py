import discord
from discord.ext import commands
import random
from PIL import Image
import io

# ID du rôle obligatoire pour accéder aux commandes de jeux
REQUIRED_ROLE_ID = 1517655811986428004 

class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.supabase.table("users")

    async def get_db_user(self, user_id: int):
        economy_cog = self.bot.get_cog("Economy")
        if economy_cog:
            return await economy_cog.get_user(user_id)
        response = self.db.select("*").eq("id", user_id).execute()
        if not response.data:
            new_user = {"id": user_id, "wallet": 1000, "last_daily": None}
            response = self.db.insert(new_user).execute()
            return response.data[0]
        return response.data[0]

    # --- PARTIE ROULETTE ---
    @commands.command(name="roulette")
    async def roulette(self, ctx, mise: int, pari: str):
        # Vérification par ID de rôle
        if REQUIRED_ROLE_ID not in [role.id for role in ctx.author.roles]:
            return await ctx.send(f"❌ Le rôle avec l'ID **{REQUIRED_ROLE_ID}** est requis pour jouer ici.")

        u = await self.get_db_user(ctx.author.id)

        if mise > u.get("wallet", 0) or mise <= 0:
            return await ctx.send("❌ Solde insuffisant ou mise invalide.")

        # Tirage de la roulette européenne (0 à 36)
        tirage = random.randint(0, 36)
        col = "vert" if tirage == 0 else ("rouge" if tirage in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36] else "noir")
        emoji = "🔴" if col == "rouge" else "⚫" if col == "noir" else "🟢"
        seq = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

        def get_col_emoji(n):
            if n == 0: return "🟢"
            return "🔴" if n in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36] else "⚫"

        idx = seq.index(tirage)
        track = []
        for i in range(-2, 3):
            n = seq[(idx + i) % 37]
            e = get_col_emoji(n)
            if i == 0:
                track.append(f"⭐【{e}{n}】⭐")
            else:
                track.append(f"[{e}{n}]")

        track_str = " ── ".join(track)
        pari = pari.lower()
        g, m = False, 2

        if pari.isdigit() and int(pari) == tirage:
            g, m = True, 35
        elif pari == col:
            g, m = True, (35 if col == "vert" else 2)

        if g:
            gain = mise * m
            new_wallet = u["wallet"] + (gain - mise)
            color = discord.Color.from_rgb(46, 204, 113)
            title = "🎉 • ROULETTE — VICTOIRE !"
            result_banner = f"```diff\n+ {gain} pièces\n```"
            description = f"La bille s'est arrêtée sur la bonne case ! Félicitations !"
        else:
            new_wallet = u["wallet"] - mise
            color = discord.Color.from_rgb(231, 76, 60)
            title = "💀 • ROULETTE — DÉFAITE"
            result_banner = f"```diff\n- {mise} pièces\n```"
            description = f"La chance n'était pas de votre côté cette fois-ci."
       
        self.db.update({"wallet": new_wallet}).eq("id", ctx.author.id).execute()

        embed = discord.Embed(title=title, description=description, color=color)
        embed.add_field(name="🎡 Piste de la Roulette (Roue)", value=f"```ml\n{track_str}\n```", inline=False)
        embed.add_field(name="🎯 Votre Pari", value=f"┕ `{pari.upper()}`", inline=True)
        embed.add_field(name="🎰 Numéro gagnant", value=f"┕ {emoji} **{tirage} {col.upper()}**", inline=True)
        embed.add_field(name="📊 Transaction", value=result_banner, inline=False)
        embed.add_field(name="💳 Nouveau Solde", value=f"```fix\n{new_wallet} pièces\n```", inline=False)
        embed.set_footer(text="Casino de Kumo • Roulette Européenne")

        await ctx.send(embed=embed)

    # --- PARTIE SLOTS ---
    @commands.command(name="slots")
    async def slots(self, ctx, mise: int):
        # Vérification par ID de rôle
        if REQUIRED_ROLE_ID not in [role.id for role in ctx.author.roles]:
            return await ctx.send(f"❌ Le rôle avec l'ID **{REQUIRED_ROLE_ID}** est requis pour jouer ici.")
            
        u = await self.get_db_user(ctx.author.id)
        if mise > u.get("wallet", 0) or mise <= 0:
            return await ctx.send("❌ Solde insuffisant ou mise invalide.")
        
        res = [random.choice(["💎","🔔","🍋","🍒","🍇"]) for _ in range(3)]
        
        if res[0] == res[1] == res[2]:
            w = mise * 10
            txt = f"3 symboles alignés : **{res[0]}** ! (Jackpot)"
            color = discord.Color.from_rgb(241, 196, 15)
            title = "🌟 • SLOTS — JACKPOT !"
            result_banner = f"```diff\n+ {w} pièces\n```"
        elif len(set(res)) == 2:
            w = mise * 2
            sym = res[0] if res.count(res[0]) == 2 else res[1]
            txt = f"Paire de **{sym}** trouvée !"
            color = discord.Color.from_rgb(52, 152, 219)
            title = "✨ • SLOTS — DOUBLÉ !"
            result_banner = f"```diff\n+ {w} pièces\n```"
        else:
            w = 0
            txt = "Aucune correspondance sur les rouleaux."
            color = discord.Color.from_rgb(149, 165, 166)
            title = "🎰 • SLOTS — PERDU"
            result_banner = f"```diff\n- {mise} pièces\n```"

        new_wallet = u["wallet"] + (w - mise)
        self.db.update({"wallet": new_wallet}).eq("id", ctx.author.id).execute()
        
        machine_art = (
            f"```\n"
            f" 🎰 ─── [ {res[0]} ] ─── [ {res[1]} ] ─── [ {res[2]} ] ─── 🎰 \n"
            f"```"
        )
        
        embed = discord.Embed(title=title, description=txt, color=color)
        embed.add_field(name="🎰 Rouleaux", value=machine_art, inline=False)
        embed.add_field(name="📊 Résultat", value=result_banner, inline=True)
        embed.add_field(name="💳 Nouveau Solde", value=f"```fix\n{new_wallet} pièces\n```", inline=True)
        embed.set_footer(text="Casino de Kumo • Machine à sous progressive")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Casino(bot))