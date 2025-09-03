from mcstatus import JavaServer
from concurrent.futures import ThreadPoolExecutor
from dotenv import dotenv_values as envval
from discord_webhook import DiscordWebhook, DiscordEmbed
from time import sleep as slp
from javascript import require, On, Once
mineflayer = require('mineflayer')
import re

WIP = envval('.env')['dlip']
WEBHOOK = envval('.env')['webhook']

ip = input('ip: ') or WIP
start_port = int(input('startport: '))
end_port = int(input('endport: '))


def makebot(ip, port, username, embed):
    bot = mineflayer.createBot({
        "host": ip,
        "port": port,
        "username": username
    })

    @Once(bot, 'spawn')
    def handler_spawn(_):
        bot.chat('/gamemode 1')

    @On(bot, 'messagestr')
    def handler_messagestr(_1, _2, _3, _4, _5):
        if _2 == 'Unknown or incomplete command, see below for error':
            embed.add_embed_field(name="Success", value=f'cheats:False')
            bot.quit()
        elif _2 in ('Incorrect argument for command', 'Set own game mode to Creative Mode'):
            embed.add_embed_field(name="Success", value=f'cheats:True')
            bot.quit()

    @On(bot, 'kicked')
    def handler_kicked(_1, reason, _2):
        embed.add_embed_field(name="Kicked", value=f'{reason}')


def dowebhook(port, desc, players, protocol, name):
    webhook = DiscordWebhook(
        url=WEBHOOK,
        username='archx2 scanner :D',
        content="<@NOPING&1412851881939701780>"
    )
    embed = DiscordEmbed(
        title=f'{ip}:{port}',
        description="Found a LAN Server",
        color="03b2f8"
    )
    embed.set_timestamp()
    embed.add_embed_field(name="PlayerCount", value=f"{players}/8")
    embed.add_embed_field(name="MOTD", value=f"{desc}")
    embed.add_embed_field(name="Version", value=f"{name}")

    if protocol <= 767:
        makebot(ip, port, 'nuLL', embed)
        slp(15)
    else:
        embed.add_embed_field(name="Cant check", value=f'protocol {protocol} is higher than 767, cant check')

    webhook.add_embed(embed)
    webhook.execute()


def check_port(port):
    try:
        server = JavaServer(ip, port)
        status = server.status()
        desc = status.description
        if status.players.max == 8 and " - " in desc:
            print(f'found smth on {ip}:{port}')
            dowebhook(port, desc, status.players.online, status.version.protocol, status.version.name)
        else:
            pass
    except:
        pass  # no server or timeout


with ThreadPoolExecutor(max_workers=int(envval('./.env')['maxworkers'])) as executor:
    executor.map(check_port, range(start_port, end_port + 1))

