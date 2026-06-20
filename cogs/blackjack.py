import discord
from discord.ext import commands
import random
from PIL import Image
import io
from datetime import datetime, timezone, timedelta

# --- CONFIGURATION ---
# Remplace cet ID par l'ID du rôle requis sur ton serveur
REQUIRED_ROLE_ID = 1517655811986428004 

def generate_hand_image(p_hand, d_hand):
    card_w, card_h = 140, 190
    padding = 25
    total_w = max(len(p_hand), len(d_hand)) * (card_w + padding) + padding
    total_h = (card_h * 2) + (padding * 3)
    combined = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    
    def get_card_img(card):
        suit_map = {'♠️': 'S', '♥️': 'H', '♦️': 'D', '♣️': 'C'}
        suit = suit_map.get(card['suit'], 'S')
        filename = f"{card['rank']}{suit}.png" if not card.get("hidden") else "back.png"
        path = f"cogs/cards/{filename}"
        try: 
            return Image.open(path).convert("RGBA").resize((card_w, card_h))
        except Exception:
            return Image.new("RGBA", (card_w, card_h), (200, 200, 200, 255))

    for i, card in enumerate(p_hand):
        combined.paste(get_card_img(card), (padding + i * (card_w + padding), padding))
    for i, card in enumerate(d_hand):
        combined.paste(get_card_img(card), (padding + i * (card_w + padding), card_h + (padding * 2)))

    buffer = io.BytesIO()
    combined.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(fp=buffer, filename="hand.png")

class BJView(discord.ui.View):
    def __init__(self, ctx, mise, user_id, db):
        super().__init__(timeout=60)
        self.ctx, self.mise, self.user_id, self.db = ctx, mise, user_id, db
        self.expiry = datetime.now(timezone.utc) + timedelta(seconds=60)
        
        suits = ["♠️", "♥️", "♦️", "♣️"]
        ranks = [(2,"2"),(3,"3"),(4,"4"),(5,"5"),(6,"6"),(7,"7"),(8,"8"),(9,"9"),(10,"10"),(10,"J"),(10,"Q"),(10,"K"),(11,"A")]
        self.deck = [{"val": v, "rank": r, "suit": s} for s in suits for v, r in ranks]
        random.shuffle(self.deck)
        
        self.d_hand = [{"val": self.deck[0]["val"], "rank": self.deck[0]["rank"], "suit": self.deck[0]["suit"], "hidden": True}, self.deck[1]]
        self.p_hand = [self.deck.pop(), self.deck.pop()]
        self.deck.pop(0); self.deck.pop(0)

    def count(self, hand):
        s = sum(c["val"] for c in hand if not c.get("hidden", False))
        aces = sum(1 for c in hand if c["rank"] == "A" and not c.get("hidden", False))
        while s > 21 and aces > 0: s -= 10; aces -= 1
        return s

    def update_balance(self, multiplier):
        gain = int(self.mise * multiplier)
        user_data = self.db.select("wallet").eq("id", self.user_id).execute().data[0]
        new_wallet = user_data["wallet"] + gain
        self.db.update({"wallet": new_wallet}).eq("id", self.user_id).execute()
        return new_wallet, gain

    def embed(self, done=False, msg="", gain=0, new_bal=0):
        p_score = self.count(self.p_hand)
        d_score = self.count(self.d_hand)
        emb = discord.Embed(title="🃏 Blackjack", description=msg, color=discord.Color.blue())
        emb.set_image(url="attachment://hand.png")
        
        if not done:
            emb.add_field(name="Vos points", value=f"{p_score}", inline=True)
            emb.add_field(name="Points Croupier", value="??", inline=True)
            emb.add_field(name="⏳ Temps", value=f"<t:{int(self.expiry.timestamp())}:R>", inline=False)
        else:
            emb.add_field(name="📊 Score Final", value=f"Vous: **{p_score}** | Croupier: **{d_score}**", inline=False)
            gain_str = f"+{gain}" if gain >= 0 else f"{gain}"
            emb.add_field(name="📈 Résultat", value=f"```diff\n{gain_str} pièces\n```", inline=True)
            emb.add_field(name="💳 Nouveau Solde", value=f"```fix\n{new_bal} pièces\n```", inline=True)
        return emb

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success)
    async def hit(self, i: discord.Interaction, b: discord.ui.Button):
        self.p_hand.append(self.deck.pop())
        if self.count(self.p_hand) > 21:
            new_bal, gain = self.update_balance(-1)
            await i.response.edit_message(embed=self.embed(True, "💥 Bust ! Vous avez dépassé 21.", gain, new_bal), attachments=[generate_hand_image(self.p_hand, self.d_hand)], view=None)
        else: await i.response.edit_message(embed=self.embed(), attachments=[generate_hand_image(self.p_hand, self.d_hand)])

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.danger)
    async def stand(self, i: discord.Interaction, b: discord.ui.Button):
        for card in self.d_hand: card["hidden"] = False
        while self.count(self.d_hand) < 17: self.d_hand.append(self.deck.pop())
        p_score, d_score = self.count(self.p_hand), self.count(self.d_hand)
        
        if p_score == 21 and len(self.p_hand) == 2:
            new_bal, gain = self.update_balance(1.5)
            msg = "🌟 BLACKJACK ! Vous gagnez x1.5 !"
        elif d_score > 21 or p_score > d_score:
            new_bal, gain = self.update_balance(1)
            msg = "🏆 Victoire ! Vous gagnez x1."
        elif p_score < d_score:
            new_bal, gain = self.update_balance(-1)
            msg = "💀 Défaite... Le croupier gagne."
        else:
            new_bal, gain = self.update_balance(0)
            msg = "🤝 Égalité ! Mise remboursée."
            
        await i.response.edit_message(embed=self.embed(True, msg, gain, new_bal), attachments=[generate_hand_image(self.p_hand, self.d_hand)], view=None)

class Blackjack(commands.Cog):
    def __init__(self, bot): self.bot = bot
    
    @commands.command(name="bj")
    async def blackjack(self, ctx, mise: int):
        # Vérification du rôle requis
        role = ctx.guild.get_role(REQUIRED_ROLE_ID)
        if role not in ctx.author.roles:
            return await ctx.send(f"❌ Accès refusé. Vous devez posséder le rôle {role.mention if role else 'requis'} pour jouer au casino.")
        
        user_data = self.bot.supabase.table("users").select("wallet").eq("id", ctx.author.id).execute().data
        if not user_data or user_data[0]["wallet"] < mise: 
            return await ctx.send("❌ Solde insuffisant.")
            
        view = BJView(ctx, mise, ctx.author.id, self.bot.supabase)
        await ctx.send(embed=view.embed(msg="La partie commence !"), file=generate_hand_image(view.p_hand, view.d_hand), view=view)

async def setup(bot): await bot.add_cog(Blackjack(bot))