import discord
from discord.ext import commands, tasks
import os
import traceback
from flask import Flask
import threading
import sys
import aiohttp
import requests
from dotenv import load_dotenv

# ================= FLASK (para mantener el bot activo) =================
app = Flask(__name__)
bot_name = "PETER LIKE BOT"

@app.route('/')
def home():
    return f"✅ {bot_name} está activo!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    if os.name == 'nt':
        from waitress import serve
        serve(app, host="0.0.0.0", port=port)
    else:
        app.run(host='0.0.0.0', port=port)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# ================= CONFIGURACIÓN =================
# ⚠️ TU TOKEN DE DISCORD (ya incluido)
TOKEN = "MTUzMTQzNjk3MDc0NjU4MTA0Mg.GkMGYn.CBZT2ho7jrP7-GFFc54fZNv8dJoQexQzzX_0Ko"

# URL de tu API (la que desplegaste en Vercel)
API_URL = "https://peterlikeapi.vercel.app/api/like"
INFO_API = "https://player-info-ob54.vercel.app/player-info?uid={uid}"
OWNER_KEY = "YOUR_SECRET_OWNER_KEY"  # Cámbiala si usas key en tu API

# ================= BOT =================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= EVENTOS =================
@bot.event
async def on_ready():
    print(f"🔗 Conectado como {bot.user}")
    print(f"🌐 Servidores: {len(bot.guilds)}")
    await bot.tree.sync()
    print("✅ Comandos slash sincronizados")
    activity = discord.Game(name="❤️ Free Fire Likes")
    await bot.change_presence(activity=activity)

# ================= COMANDOS SLASH =================
@bot.tree.command(name="like", description="Envía likes a un perfil de Free Fire")
async def like(interaction: discord.Interaction, uid: str, region: str = "IND"):
    await interaction.response.defer()

    try:
        params = {"uid": uid, "region": region.upper()}
        if OWNER_KEY and OWNER_KEY != "YOUR_SECRET_OWNER_KEY":
            params["key"] = OWNER_KEY

        response = requests.get(API_URL, params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                embed = discord.Embed(
                    title="✅ Likes Enviados",
                    description=f"**{data['likes_given']}** likes añadidos a **{data['name']}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="👤 Jugador", value=data['name'], inline=True)
                embed.add_field(name="🆔 UID", value=uid, inline=True)
                embed.add_field(name="🌍 Región", value=data['region'], inline=True)
                embed.add_field(name="👍 Antes", value=data['likes_before'], inline=True)
                embed.add_field(name="🚀 Después", value=data['likes_after'], inline=True)
                embed.set_footer(text="PETER LIKE BOT")
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="❌ Error",
                    description=data.get("message", "Error desconocido"),
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
        else:
            error_text = response.json().get("message", f"HTTP {response.status_code}")
            embed = discord.Embed(
                title="❌ Error de API",
                description=error_text,
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Error: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="info", description="Obtén información de un jugador")
async def info(interaction: discord.Interaction, uid: str):
    await interaction.response.defer()

    try:
        url = INFO_API.format(uid=uid)
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            info = data.get("basicInfo", {})

            embed = discord.Embed(
                title="📊 Información del Jugador",
                color=discord.Color.blue()
            )
            embed.add_field(name="👤 Nickname", value=info.get("nickname", "N/A"), inline=True)
            embed.add_field(name="🆔 UID", value=uid, inline=True)
            embed.add_field(name="🌍 Región", value=info.get("region", "N/A"), inline=True)
            embed.add_field(name="🎮 Nivel", value=info.get("level", "N/A"), inline=True)
            embed.add_field(name="🏅 Rango", value=info.get("rank", "N/A"), inline=True)
            embed.add_field(name="❤️ Likes", value=info.get("liked", 0), inline=True)
            embed.set_footer(text="PETER LIKE BOT")
            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="Jugador no encontrado",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=str(e),
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

# ================= COMANDO PING =================
@bot.tree.command(name="ping", description="Verifica que el bot está activo")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! Bot activo.", ephemeral=True)

# ================= INICIO =================
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ Token de Discord inválido")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido.")
        sys.exit(0)
    except Exception as e:
        print(f"⚠️ Error: {e}")
        traceback.print_exc()
        sys.exit(1)
