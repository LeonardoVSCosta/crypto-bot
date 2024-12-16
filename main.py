import os
from datetime import datetime

import discord
import matplotlib.pyplot as plt
import requests
from discord import ui, SelectOption
from discord.ext import commands
from pycoingecko import CoinGeckoAPI

from bot_token import token

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

        options = [SelectOption(label="General", description="Comandos gerais do bot."),
                   SelectOption(label="Crypto", description="Comandos relacionados a criptomoedas."), ]
        super().__init__(placeholder="Escolha uma categoria...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "General":
            embed = discord.Embed(title="Comandos: General", description="`mundo`, `hora`, `ajuda`", color=0x0B5394)
        elif self.values[0] == "Crypto":
            embed = discord.Embed(title="Comandos: Crypto",
                                  description="`preco`, `variacao`, `fandg`, `volume`, `grafico`",
                                  color=0x0B5394)

        await interaction.response.edit_message(embed=embed)


class HelpView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpDropdown())


@bot.command(name="ajuda")
async def ajuda_comando(ctx):
    embed = discord.Embed(title="Comandos: ", description="*Todos os comandos do Bot.*", color=0x0B5394)
    embed.add_field(name="**Básicos**", value="`mundo`, `hora`, `ajuda`", inline=False)
    embed.add_field(name="**Crypto**", value="`preco`, `variacao`, `fandg`, `volume`, `grafico`",
                    inline=False)
    embed.set_footer(text="Selecione uma categoria abaixo para mais detalhes.")

    await ctx.send(embed=embed, view=HelpView())


@bot.tree.command(name="ajuda", description="Mostra todos os comandos do Bot.")
async def ajuda_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="Comandos: ", description="*Todos os comandos do Bot.*", color=0x0B5394)
    embed.add_field(name="**Básicos**", value="`mundo`, `hora`, `ajuda`", inline=False)
    embed.add_field(name="**Crypto**", value="`preco`, `variacao`, `fandg`, `volume`, `grafico`",
                    inline=False)
    embed.set_footer(text="Selecione uma categoria abaixo para mais detalhes.")

    await interaction.response.send_message(embed=embed, view=HelpView())


@bot.command(name="preco")
async def preco(ctx, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            await ctx.send("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        moeda_encontrada = resultado_busca['coins'][0]
        id_cripto = moeda_encontrada['id']

        preco = cg.get_price(ids=id_cripto, vs_currencies='brl')

        if preco and id_cripto in preco:
            preco_formatado = f"{preco[id_cripto]['brl']:,}".replace(',', '.') + ' BRL'
            await ctx.send(f"**O preço atual de {moeda.upper()} é {preco_formatado}!**")
        else:
            await ctx.send("Desculpe, não consegui encontrar o preço dessa criptomoeda.")


    except Exception as e:
        await ctx.send(f"Erro ao buscar o preço: {str(e)}")


@bot.tree.command(name="preco", description="Mostra o preço de uma criptomoeda em reais.")
async def preco_slash(interaction: discord.Interaction, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            await interaction.response.send_message("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        moeda_encontrada = resultado_busca['coins'][0]
        id_cripto = moeda_encontrada['id']

        preco = cg.get_price(ids=id_cripto, vs_currencies='brl')

        if preco and id_cripto in preco:
            preco_formatado = f"{preco[id_cripto]['brl']:,}".replace(',', '.') + ' BRL'
            await interaction.response.send_message(f"**O preço atual de {moeda.upper()} é {preco_formatado}!**")
        else:
            await interaction.response.send_message("Desculpe, não consegui encontrar o preço dessa criptomoeda.")

    except Exception as e:
        await interaction.response.send_message(f"Erro ao buscar o preço: {str(e)}")


btc_url = "https://api.coingecko.com/api/v3/coins/bitcoin"
response = requests.get(btc_url)
fandg_btc_url = "https://api.alternative.me/fng/?limit=1"
response_fandg = requests.get(fandg_btc_url)
data = response.json()
data_fandg = response_fandg.json()
btc_variacao_24h = data['market_data']['price_change_percentage_24h']
fandg_btc_ = data_fandg['data'][0]['value']
descricao_fandgbtc = data_fandg['data'][0]['value_classification']
btc_dados = cg.get_price(ids='bitcoin', vs_currencies='brl')


@bot.command(name="variacao")
async def variacao(ctx, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            await ctx.send("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        moeda_encontrada = resultado_busca['coins'][0]
        id_cripto = moeda_encontrada['id']

        dados_cripto = cg.get_coin_by_id(id_cripto)

        if 'market_data' in dados_cripto:
            variacao_24h = dados_cripto['market_data']['price_change_percentage_24h']

            if variacao_24h is not None:
                await ctx.send(f"**A variação de {moeda.upper()} nas últimas 24 horas foi de {variacao_24h:.2f}%**")
            else:
                await ctx.send("Desculpe, não consegui obter a variação dessa criptomoeda.")
        else:
            await ctx.send("Desculpe, não consegui encontrar informações sobre essa criptomoeda.")

    except Exception as e:
        await ctx.send(f"Erro ao buscar a variação: {str(e)}")


@bot.tree.command(name="variacao", description="Mostra a variação de uma criptomoeda nas últimas 24 horas.")
async def variacao_slash(interaction: discord.Interaction, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            await interaction.response.send_message("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        moeda_encontrada = resultado_busca['coins'][0]
        id_cripto = moeda_encontrada['id']

        dados_cripto = cg.get_coin_by_id(id_cripto)

        if 'market_data' in dados_cripto:
            variacao_24h = dados_cripto['market_data']['price_change_percentage_24h']

            if variacao_24h is not None:
                await interaction.response.send_message(
                    f"**A variação de {moeda.upper()} nas últimas 24 horas foi de {variacao_24h:.2f}%**")
            else:
                await interaction.response.send_message("Desculpe, não consegui obter a variação dessa criptomoeda.")
        else:
            await interaction.response.send_message(
                "Desculpe, não consegui encontrar informações sobre essa criptomoeda.")

    except Exception as e:
        await interaction.response.send_message(f"Erro ao buscar a variação: {str(e)}")


@bot.command(name="fandg")
async def fandg(ctx, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            await ctx.send("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        moeda_encontrada = resultado_busca['coins'][0]
        id_cripto = moeda_encontrada['id']

        fandg_url = "https://api.alternative.me/fng/?limit=1"
        response_fandg = requests.get(fandg_url)
        data_fandg = response_fandg.json()

        fandg_valor = data_fandg['data'][0]['value']
        descricao_fandg = data_fandg['data'][0]['value_classification']

        await ctx.send(f"**Fear and Greed de {moeda.upper()}: {fandg_valor} ({descricao_fandg})**")

    except Exception as e:
        await ctx.send(f"Erro ao buscar o índice: {str(e)}")


@bot.tree.command(name="fandg", description="Mostra o índice Fear and Greed de uma criptomoeda.")
async def fandg_slash(interaction: discord.Interaction, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            await interaction.response.send_message("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        fandg_url = "https://api.alternative.me/fng/?limit=1"
        response_fandg = requests.get(fandg_url)
        data_fandg = response_fandg.json()

        fandg_valor = data_fandg['data'][0]['value']
        descricao_fandg = data_fandg['data'][0]['value_classification']

        await interaction.response.send_message(
            f"**Fear and Greed de {moeda.upper()}: {fandg_valor} ({descricao_fandg})**")

    except Exception as e:
        await interaction.response.send_message(f"Erro ao buscar o índice: {str(e)}")


@bot.command(name="volume")
async def volume(ctx, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            await ctx.send("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        id_cripto = resultado_busca['coins'][0]['id']

        dados_cripto = cg.get_coin_market_chart_by_id(id=id_cripto, vs_currency='brl', days=1)
        volume_cripto = dados_cripto['total_volumes'][-1][1]
        volume_formatado = f"{volume_cripto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        await ctx.send(f"**Volume das negociações de {moeda.upper()}: {volume_formatado} reais!**")

    except Exception as e:
        await ctx.send(f"Erro ao buscar o volume: {str(e)}")


@bot.tree.command(name="volume", description="Mostra o volume das negociações de uma criptomoeda em BRL.")
async def volume_slash(interaction: discord.Interaction, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            await interaction.response.send_message("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        id_cripto = resultado_busca['coins'][0]['id']

        dados_cripto = cg.get_coin_market_chart_by_id(id=id_cripto, vs_currency='brl', days=1)
        volume_cripto = dados_cripto['total_volumes'][-1][1]
        volume_formatado = f"{volume_cripto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        await interaction.response.send_message(
            f"**Volume das negociações de {moeda.upper()}: {volume_formatado} reais!**")

    except Exception as e:
        await interaction.response.send_message(f"Erro ao buscar o volume: {str(e)}")


@bot.command(name="grafico")
async def grafico(ctx, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)
        if not resultado_busca['coins']:
            await ctx.send("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        id_cripto = resultado_busca['coins'][0]['id']

        data = cg.get_coin_market_chart_by_id(id=id_cripto, vs_currency='brl', days=1)
        timestamps = [point[0] for point in data['prices']]
        prices = [point[1] for point in data['prices']]
        horas = [datetime.fromtimestamp(ts / 1000).strftime('%H:%M') for ts in timestamps]

        plt.figure(figsize=(10, 5))
        plt.plot(horas, prices, label=f"Preço de {moeda.upper()} (USD)", color="blue", linewidth=2)
        plt.title(f"Gráfico Diário de {moeda.upper()} (USD)")
        plt.xlabel("Hora")
        plt.ylabel("Preço (USD)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)

        grafico_path = f"{moeda}_daily_chart.png"
        plt.tight_layout()
        plt.savefig(grafico_path)
        plt.close()

        await ctx.send(file=discord.File(grafico_path))

        if os.path.exists(grafico_path):
            os.remove(grafico_path)

    except Exception as e:
        await ctx.send(f"Erro ao gerar o gráfico: {str(e)}")


@bot.tree.command(name="grafico", description="Mostra um gráfico diário do preço de uma criptomoeda em BRL.")
async def grafico_slash(interaction: discord.Interaction, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)
        if not resultado_busca['coins']:
            await interaction.response.send_message("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        id_cripto = resultado_busca['coins'][0]['id']

        data = cg.get_coin_market_chart_by_id(id=id_cripto, vs_currency='brl', days=1)
        timestamps = [point[0] for point in data['prices']]
        prices = [point[1] for point in data['prices']]
        horas = [datetime.fromtimestamp(ts / 1000).strftime('%H:%M') for ts in timestamps]

        plt.figure(figsize=(10, 5))
        plt.plot(horas, prices, label=f"Preço de {moeda.upper()} (BRL)", color="blue", linewidth=2)
        plt.title(f"Gráfico Diário de {moeda.upper()} (BRL)")
        plt.xlabel("Hora")
        plt.ylabel("Preço (BRL)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)

        grafico_path = f"{moeda}_daily_chart.png"
        plt.tight_layout()
        plt.savefig(grafico_path)
        plt.close()

        await interaction.response.send_message(file=discord.File(grafico_path))

        if os.path.exists(grafico_path):
            os.remove(grafico_path)

    except Exception as e:
        await interaction.response.send_message(f"Erro ao gerar o gráfico: {str(e)}")


bot.run(token)
