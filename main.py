import discord
import datetime
import os
import datetime
import requests

from bs4 import BeautifulSoup
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

load_dotenv()

header = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
}

url = "https://lbprate.com/"

client = discord.Bot(intents=intents, activity=discord.Activity(
    type=3, name="https://github.com/Berry-Studios/LBPRateBot"), status=discord.Status.do_not_disturb)

startTime = datetime.datetime.utcnow()

@client.event
async def on_ready():
    print(f"Bot Logged in as: {client.user.name}#{client.user.discriminator}")

@client.slash_command(
    name="ping",
    description="Bot latency"
)
async def ping(ctx):
    await ctx.respond(content=f"Pong! `{round(client.latency * 1000)}`ms, serving `{len(client.guilds)}` servers and `{len(client.users)}` users")

@client.slash_command(
    name="uptime",
    description="Bot uptime"
)
async def uptime(ctx):
    now = datetime.datetime.utcnow()
    delta = now - startTime
    uptime = ""
    if delta.days // 365 > 0:
        if delta.days // 365 == 1:
            uptime = uptime[:-2] + " year, "
        else:
            uptime += f"{delta.days // 365} years, "
    # months and week should show too
    if delta.days % 365 // 30 > 0:
        if delta.days % 365 // 30 == 1:
            uptime = uptime[:-2] + " month, "
        else:
            uptime += f"{delta.days % 365 // 30} months, "
    if delta.days % 365 % 30 // 7 > 0:
        if delta.days % 365 % 30 // 7 == 1:
            uptime = uptime[:-2] + " week, "
        else:
            uptime += f"{delta.days % 365 % 30 // 7} weeks, "
    if delta.days % 365 % 30 % 7 > 0:
        if delta.days % 365 % 30 % 7 == 1:
            uptime = uptime[:-2] + " day, "
        else:
            uptime += f"{delta.days % 365 % 30 % 7} days, "
    if delta.seconds // 3600 > 0:
        if delta.seconds // 3600 == 1:
            uptime = uptime[:-2] + " hour, "
        else:
            uptime += f"{delta.seconds // 3600} hours, "
    if delta.seconds % 3600 // 60 > 0:
        if delta.seconds % 3600 // 60 == 1:
            uptime = uptime[:-2] + " minute, "
        else:
            uptime += f"{delta.seconds % 3600 // 60} minutes, "
    if delta.seconds % 3600 % 60 > 0:
        if delta.seconds % 3600 % 60 == 1:
            uptime = uptime[:-2] + " second, "
        else:
            uptime += f"{delta.seconds % 3600 % 60} seconds, "

    if uptime.endswith(", "):
        uptime = uptime[:-2]

    await ctx.respond(content=f"Uptime: {uptime}")

@client.slash_command(
    name="lbprate",
    description="Lebanese Pound Rate"
)
@discord.commands.option(name="options", description="Options", choices=["noembed", "embed"], required=False)
async def lbprate(ctx, options: str = None):
    market_buy, market_sell, sayrafa_buy, sayrafa_volume, updated, status = get_rate()

    if status == 200:
        if options == "embed" or options == None:
                embed = discord.Embed(title="Lebanese Pound Rate", description=f"{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%H:%M:%S')} | {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%d-%m-%Y')}\n\
                                      ☞ {updated}", color=0xff0000)
                embed.add_field(name="Black Market", value=f"\
                                ☇ **BUY**: `{market_buy}`\n\
                                ☇ **SELL**: `{market_sell}`", inline=False)
                embed.add_field(name="Official Market", value=f"\
                                ☇ **BUY**: `{sayrafa_buy}`\n\
                                ☇ **VOLUME**: `{sayrafa_volume}`", inline=False)
                embed.add_field(name="Disclaimer", value="The rates provided by this bot are not official rates and are provided for informational purposes only. The rates are not guaranteed to be accurate and are subject to change without notice. The rates are provided by the Central Bank of Lebanon and LBPRate.com.")
                embed.set_footer(text="Data provided by the Central Bank of Lebanon & LBPRate.com || Made with ❤️ in Lebanon by BerryStudios")
                await ctx.respond(embed=embed)
        elif options == "noembed":
            await ctx.respond(content=f"**Lebanese Pound Rate**\n{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%H:%M:%S')} | {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%d-%m-%Y')}\n☞ {updated}\n\n**Black Market**\n☇ **BUY**: `{market_buy}`\n☇ **SELL**: `{market_sell}`\n\n**Official Market**\n☇ **BUY**: `{sayrafa_buy}`\n☇ **VOLUME**: `{sayrafa_volume}`\n\n**Disclaimer**\n> The rates provided by this bot are not official rates and are provided for informational purposes only. The rates are not guaranteed to be accurate and are subject to change without notice. The rates are provided by the Central Bank of Lebanon and LBPRate.com.\n\n*Data provided by the Central Bank of Lebanon & LBPRate.com || Made with ❤️ in Lebanon by BerryStudios*")
    else:
        await ctx.respond(content=f"Error: `{status}`")

@client.slash_command(
    name="fuelprice",
    description="Fuel Price"
)
@discord.commands.option(name="options", description="Options", choices=["noembed", "embed"], required=False)
async def fuelprice(ctx, options: str = None):
    data_fuel, updated_time, status = get_fuel_price()

    if status == 200:
        if options == "embed" or options == None:
            embed = discord.Embed(title="Fuel Price", description=f"{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%H:%M:%S')} | {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%d-%m-%Y')}\n\
                                    ☞ {updated_time}\n\n\
                                    ☇ **{data_fuel[0]['FUEL'][1][1:10]}**: `{data_fuel[5]['PRICE'][1]}`\n\
                                    ☇ **{data_fuel[1]['FUEL'][1][1:10]}**: `{data_fuel[6]['PRICE'][1]}`\n\
                                    ☇ **{data_fuel[2]['FUEL'][1][1:4]}**: `{data_fuel[7]['PRICE'][1]}`\n\
                                    ☇ **{data_fuel[3]['FUEL'][1][1:7]}**: `{data_fuel[8]['PRICE'][1]}`\n\
                                    ☇ **{data_fuel[4]['FUEL'][1][1:16]}**: `{data_fuel[9]['PRICE'][1]}`", color=0xff0000)
            embed.add_field(name="Disclaimer", value="The rates provided by this bot are not official rates and are provided for informational purposes only. The rates are not guaranteed to be accurate and are subject to change without notice. The rates are provided by the Central Bank of Lebanon and LBPRate.com.")  
            embed.set_footer(text="Data provided by the Central Bank of Lebanon || Made with ❤️ in Lebanon by BerryStudios")
            await ctx.respond(embed=embed)
        elif options == "noembed":
            await ctx.respond(content=f"**Fuel Price**\n{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%H:%M:%S')} | {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%d-%m-%Y')}\n☞ {updated_time}\n\n☇ **{data_fuel[0]['FUEL'][1][1:10].replace(' ', '_')}**: `{data_fuel[5]['PRICE'][1]}`\n☇ **{data_fuel[1]['FUEL'][1][1:10].replace(' ', '_')}**: `{data_fuel[6]['PRICE'][1]}`\n☇ **{data_fuel[2]['FUEL'][1][1:4].replace(' ', '_')}**: `{data_fuel[7]['PRICE'][1]}`\n☇ **{data_fuel[3]['FUEL'][1][1:7].replace(' ', '_')}**: `{data_fuel[8]['PRICE'][1]}`\n☇ **{data_fuel[4]['FUEL'][1][1:16].replace(' ', '_')}**: `{data_fuel[9]['PRICE'][1]}`\n\n**Disclaimer**\n> The rates provided by this bot are not official rates and are provided for informational purposes only. The rates are not guaranteed to be accurate and are subject to change without notice. The rates are provided by the Central Bank of Lebanon and LBPRate.com.\n\n*Data provided by the Central Bank of Lebanon || Made with ❤️ in Lebanon by BerryStudios*")
    else:
        await ctx.respond(content=f"Error: `{status}`")

@client.slash_command(
    name="convert",
    description="Convert Currency"
)
@discord.commands.option(name="options", description="Options", choices=["noembed", "embed"], required=False)
@discord.commands.option(name="amount", description="Amount to convert", required=True)
@discord.commands.option(name="currency", description="Currency to convert from", required=True, choices=["USD", "LBP"])
async def convert(ctx, amount: int, currency: str, options: str = None):
    result, updated_time, status = convert(amount, currency)
    
    if status == 200:
        if options == "embed" or options == None:
            embed = discord.Embed(title="Currency Converter", description=f"{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%H:%M:%S')} | {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%d-%m-%Y')}\n\
                                    ☞ {updated_time}\n\n\
                                    ☞ **{result[0]}**: `{result[1]}`\n", color=0xff0000)
            embed.add_field(name="Market", value=f"\
                                    ☇ **{result[2]}**: `{result[3]}`\n\
                                    ☇ **{result[4]}**: `{result[5]}`\n\
                                    ☇ **{result[6]}**: `{result[7]}`\n", inline=False)
            embed.add_field(name="Disclaimer", value="The rates provided by this bot are not official rates and are provided for informational purposes only. The rates are not guaranteed to be accurate and are subject to change without notice. The rates are provided by the Central Bank of Lebanon and LBPRate.com.")
            embed.set_footer(text="Data provided by the Central Bank of Lebanon || Made with ❤️ in Lebanon by BerryStudios")
            await ctx.respond(embed=embed)
        elif options == "noembed":
            await ctx.respond(content=f"**Currency Converter**\n{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%H:%M:%S')} | {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime('%d-%m-%Y')}\n☞ {result['updated_time']}\n\n☞ **{result['from']}**: `{result['amount']}`\n\n☇ **{result['to'][0]}**: `{result['result'][0]}`\n☇ **{result['to'][1]}**: `{result['result'][1]}`\n☇ **{result['to'][2]}**: `{result['result'][2]}`\n☇ **{result['to'][3]}**: `{result['result'][3]}`\n☇ **{result['to'][4]}**: `{result['result'][4]}`\n☇ **{result['to'][5]}**: `{result['result'][5]}`\n☇ **{result['to'][6]}**: `{result['result'][6]}`\n☇ **{result['to'][7]}**: `{result['result'][7]}`\n\n**Disclaimer**\n> The rates provided by this bot are not official rates and are provided for informational purposes only. The rates are not guaranteed to be accurate and are subject to change without notice. The rates are provided by the Central Bank of Lebanon and LBPRate.com.\n\n*Data provided by the Central Bank of Lebanon || Made with ❤️ in Lebanon by BerryStudios*")
    else:
        await ctx.respond(content=f"Error: `{status}`")

def get_rate():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=100,
        pool_maxsize=100)
    session.mount('https://', adapter)
    response = session.get(url, headers=header)
    soup = BeautifulSoup(response.content, 'html5lib')

    if response.status_code == 200:
        for market in BeautifulSoup(str(soup.find('div', class_='row h-100', id='marketRate')), 'html5lib'):
                marketdiv_buy = market.find('div', class_='col-md-4 offset-md-2 text-center')
                marketspan_buy = marketdiv_buy.find_all('span', class_='text-white')[1].text
                marketdiv_sell = market.find('div', class_='col-md-4 text-center')
                marketspan_sell = marketdiv_sell.find_all('span', class_='text-white')[1].text

        for sayrafa in BeautifulSoup(str(soup.find('div', class_='row h-100 d-none', id='sayrafaRate')), 'html5lib'):
                sayrafadiv_buy = sayrafa.find(
                    'div', class_='col-md-4 offset-md-2 text-center')
                sayrafaspan_buy = sayrafadiv_buy.find_all(
                    'span', class_='text-white')[1].text
                sayrafadiv_volume = sayrafa.find(
                    'div', class_='col-md-4 text-center')
                sayrafaspan_volume = sayrafadiv_volume.find_all(
                    'span', class_='text-white')[1].text

        for update in BeautifulSoup(str(soup.find('div', class_='container')), 'html5lib'):
                updated_time = update.find(
                    'label', class_='ml-auto text-white').text

        return marketspan_buy, marketspan_sell, sayrafaspan_buy, sayrafaspan_volume, updated_time, response.status_code
    else:
        return None, None, None, None, None, response.status_code

def get_fuel_price():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=100,
        pool_maxsize=100)
    session.mount('https://', adapter)
    response = session.get(url, headers=header)
    soup = BeautifulSoup(response.content, 'html5lib')

    if response.status_code == 200:
        for fuel in BeautifulSoup(str(soup.find('div', class_='row h-100 d-none', id='fuelRate')), 'html5lib'):
                fuel_1 = fuel.find_all(
                    'h5', class_='col-6 col-sm-4 offset-sm-2 col-md-3 offset-md-3 text-left')
                fuel_2 = fuel.find_all(
                    'h5', class_='col-6 col-sm-4 col-md-3 text-right')
        data_fuel = []
        for i in fuel_1:
            data_fuel.append({
                "FUEL": [d.text for d in i]
            })

        for i in fuel_2:
            data_fuel.append({
                "PRICE": [d.text for d in i]
            })

        for update in BeautifulSoup(str(soup.find('div', class_='container')), 'html5lib'):
                updated_time = update.find(
                    'label', class_='ml-auto text-white').text
        

        return data_fuel, updated_time, response.status_code
    else:
        return None, None, None, response.status_code
    
def convert(amount, from_currency):
    market_buy, market_sell, sayrafa_buy, sayrafa_volume, updated_time, status = get_rate()

    # Honestly, this is a pain in the ass to fix, so do ignore the poor method I used here.
    if status == 200:
        if from_currency == 'USD':
            amount = [
                'USD', amount,
                'MARKET_BUY', amount * float(market_buy[10:30].replace("LBP", "").replace(" ", "").replace(",", "")),
                'MARKET_SELL', amount * float(market_sell[10:30].replace("LBP", "").replace(" ", "").replace(",", "")),
                'SAYRAFA', amount * float(sayrafa_buy[10:30].replace("LBP", "").replace(" ", "").replace(",", ""))
            ]
            return amount, updated_time, status

        elif from_currency == 'LBP':
            amount = [
                'LBP', amount,
                'MARKET_BUY', amount / float(market_buy[10:30].replace("LBP", "").replace(" ", "").replace(",", "")),
                'MARKET_SELL', amount / float(market_sell[10:30].replace("LBP", "").replace(" ", "").replace(",", "")),
                'SAYRAFA', amount / float(sayrafa_buy[10:30].replace("LBP", "").replace(" ", "").replace(",", ""))
            ]
            return amount, updated_time, status
    else:
        return None, None, status
     
client.run(os.getenv("TOKEN"))