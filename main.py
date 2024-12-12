import discord
from discord.ext import commands
from bot_token import token
from datetime import datetime
from pycoingecko import CoinGeckoAPI
import requests
import matplotlib.pyplot as plt
import os
from discord import ui, SelectOption

cg = CoinGeckoAPI()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} ligado!")

@bot.tree.command(name="mundo", description="Olá, mundo!")
async def slash_command(interaction: discord.Interaction):
    await interaction.response.send_message("Olá, mundo!")

@bot.command(name="mundo")
async def mundo_comando(ctx):
    await ctx.send("Olá, mundo!")

@bot.command(name="hora")
async def hora_comando(ctx):
    hora_atual = datetime.now().strftime("%H:%M")
    await ctx.send(f"Agora são {hora_atual}!")

@bot.tree.command(name="hora", description="Mostra a hora atual")
async def hora_slash(interaction: discord.Interaction):
    hora_atual = datetime.now().strftime("%H:%M")
    await interaction.response.send_message(f"Agora são {hora_atual}!")

@bot.event
async def on_message(message):
    if bot.user.mention in message.content:
        await message.channel.send(f"E aí {message.author.mention}!")
    await bot.process_commands(message)

class HelpDropdown(ui.Select):
    def __init__(self):

        options = [
            SelectOption(label="General", description="Comandos gerais do bot."),
            SelectOption(label="Crypto", description="Comandos relacionados a criptomoedas."),
        ]
        super().__init__(placeholder="Escolha uma categoria...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "General":
            embed = discord.Embed(
                title="Comandos: General",
                description="`mundo`, `hora`, `ajuda`",
                color=0x0B5394
            )
        elif self.values[0] == "Crypto":
            embed = discord.Embed(
                title="Comandos: Crypto",
                description="`btc.preco`, `btc.variacao`, `btc.fandg`, `btc.volume`, `btc.grafico`",
                color=0x0B5394
            )

        await interaction.response.edit_message(embed=embed)

class HelpView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpDropdown())

@bot.command(name="ajuda")
async def ajuda_comando(ctx):
    embed = discord.Embed(
        title="Comandos: ",
        description="*Todos os comandos do Bot.*",
        color=0x0B5394
    )
    embed.add_field(
        name="**Básicos**",
        value="`mundo`, `hora`, `ajuda`",
        inline=False
    )
    embed.add_field(
        name="**Crypto**",
        value="`btc.preco`, `btc.variacao`, `btc.fandg`, `btc.volume`, `btc.grafico`",
        inline=False
    )
    embed.set_footer(text="Selecione uma categoria abaixo para mais detalhes.")

    await ctx.send(embed=embed, view=HelpView())

@bot.tree.command(name="ajuda", description="Mostra todos os comandos do Bot.")
async def ajuda_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Comandos: ",
        description="*Todos os comandos do Bot.*",
        color=0x0B5394
    )
    embed.add_field(
        name="**Básicos**",
        value="`mundo`, `hora`, `ajuda`",
        inline=False
    )
    embed.add_field(
        name="**Crypto**",
        value="`btc.preco`, `btc.variacao`, `btc.fandg`, `btc.volume`, `btc.grafico`",
        inline=False
    )
    embed.set_footer(text="Selecione uma categoria abaixo para mais detalhes.")

    await interaction.response.send_message(embed=embed, view=HelpView())

@bot.command(name="btc.preco")
async def btc_preco(ctx):
    bitcoin_preco = cg.get_price(ids='bitcoin', vs_currencies='brl')
    preco_formatado = f"{bitcoin_preco['bitcoin']['brl']:,}".replace(',', ',') + ',00'
    await ctx.send(f"**O Bitcoin está custando atualmente {preco_formatado} reais!**")

@bot.tree.command(name="btc_preco", description="Mostra o preço atual do Bitcoin em reais.")
async def btc_preco_slash(interaction: discord.Interaction):
    bitcoin_preco = cg.get_price(ids='bitcoin', vs_currencies='brl')
    preco_formatado = f"{bitcoin_preco['bitcoin']['brl']:,}".replace(',', '.') + ',00'
    await interaction.response.send_message(f"**O Bitcoin está custando atualmente {preco_formatado} reais!**")


btc_url="https://api.coingecko.com/api/v3/coins/bitcoin"
response = requests.get(btc_url)
fandg_btc_url = "https://api.alternative.me/fng/?limit=1"
response_fandg = requests.get(fandg_btc_url)
data = response.json()
data_fandg = response_fandg.json()
btc_variacao_24h=data['market_data']['price_change_percentage_24h']
fandg_btc_ = data_fandg['data'][0]['value']
descricao_fandgbtc = data_fandg['data'][0]['value_classification']
btc_dados= cg.get_price(ids='bitcoin', vs_currencies='brl')

@bot.command(name="btc.variacao")
async def btc_variacao(ctx):
    await ctx.send(f"**Variação do Bitcoin em 24 horas: {btc_variacao_24h}%**")

@bot.tree.command(name="btc_variacao", description="Mostra a variação do Bitcoin nas últimas 24 horas.")
async def btc_variacao_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f"**Variação do Bitcoin em 24 horas: {btc_variacao_24h}%**")

@bot.command(name="btc.fandg")
async def btc_fandg(ctx):
    await ctx.send(f"**Fear and Greed: {fandg_btc_} ({descricao_fandgbtc})**")

@bot.tree.command(name="btc_fandg", description="Mostra o índice Fear and Greed do Bitcoin.")
async def btc_fandg_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f"**Fear and Greed: {fandg_btc_} ({descricao_fandgbtc})**")

@bot.command(name="btc.volume")
async def btc_volume(ctx):
    dados_btc = cg.get_coin_market_chart_by_id(id='bitcoin', vs_currency='brl', days=1)
    volume_btc = dados_btc['total_volumes'][-1][1]
    volume_formatado = volume_formatado = f"{volume_btc:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    await ctx.send(f"**Volume das negociações: {volume_formatado} reais!**")

@bot.tree.command(name="btc_volume", description="Mostra o volume das negociações do Bitcoin em BRL.")
async def btc_volume_slash(interaction: discord.Interaction):
    dados_btc = cg.get_coin_market_chart_by_id(id='bitcoin', vs_currency='brl', days=1)
    volume_btc = dados_btc['total_volumes'][-1][1]
    volume_formatado = f"{volume_btc:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    await interaction.response.send_message(f"**Volume das negociações: {volume_formatado} reais!**")


@bot.command(name="btc.grafico")
async def btc_grafico(ctx):
    data = cg.get_coin_market_chart_by_id(id='bitcoin', vs_currency='usd', days=1)
    timestamps = [point[0] for point in data['prices']]
    prices = [point[1] for point in data['prices']]
    horas = [datetime.fromtimestamp(ts / 1000).strftime('%H:%M') for ts in timestamps]

    plt.figure(figsize=(10, 5))
    plt.plot(horas, prices, label="Preço (USD)", color="blue", linewidth=2)
    plt.title("Gráfico Diário do Bitcoin (USD)")
    plt.xlabel("Hora")
    plt.ylabel("Preço (USD)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)

    grafico_path = "btc_daily_chart.png"
    plt.tight_layout()
    plt.savefig(grafico_path)
    plt.close()

    await ctx.send(file=discord.File(grafico_path))

    if os.path.exists(grafico_path):
        os.remove(grafico_path)

@bot.tree.command(name="btc_grafico", description="Mostra um gráfico diário do preço do Bitcoin em USD.")
async def btc_grafico_slash(interaction: discord.Interaction):
    data = cg.get_coin_market_chart_by_id(id='bitcoin', vs_currency='usd', days=1)
    timestamps = [point[0] for point in data['prices']]
    prices = [point[1] for point in data['prices']]
    horas = [datetime.fromtimestamp(ts / 1000).strftime('%H:%M') for ts in timestamps]

    plt.figure(figsize=(10, 5))
    plt.plot(horas, prices, label="Preço (USD)", color="blue", linewidth=2)
    plt.title("Gráfico Diário do Bitcoin (USD)")
    plt.xlabel("Hora")
    plt.ylabel("Preço (USD)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)

    grafico_path = "btc_daily_chart.png"
    plt.tight_layout()
    plt.savefig(grafico_path)
    plt.close()

    await interaction.response.send_message(file=discord.File(grafico_path))

    if os.path.exists(grafico_path):
        os.remove(grafico_path)


bot.run(token)
