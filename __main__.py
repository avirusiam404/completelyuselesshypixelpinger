from mcstatus import JavaServer
from concurrent.futures import ThreadPoolExecutor
from dotenv import dotenv_values as envval
from discord_webhook import DiscordWebhook, DiscordEmbed
from time import sleep as slp
from javascript import require, On, Once
import nbtlib
from nbtlib import String, Compound, Byte, List
import queue
mineflayer = require('mineflayer')
import re

WIP = envval('.env')['dlip']
WEBHOOK = envval('.env')['webhook']


ip = input('ip: ') or WIP
start_port = int(input('startport: '))
end_port = int(input('endport: '))

def run_script(bot):
    with open('commands.Ax2Bs', 'r') as f:
        lines=[line.strip() for line in f if line.strip()]

    for line in lines:
        if line.startswith('x'):
            parts = line.split(maxsplit=2)
            if len(parts) >= 3 and parts[1] == 'chat':
                count = int(parts[0][1:])
                msg = parts[2]
                for _ in range(count):
                    bot.chat(msg)
        # handle normal chat: chat msg
        elif line.startswith('chat '):
            msg = line[5:]
            bot.chat(msg)
        # handle sleep: slp N
        elif line.startswith('slp '):
            seconds = float(line[4:])
            slp(seconds)
        else:
            print(f"Unknown command: {line}")

def makebot(ip, port, username, q):
    bot = mineflayer.createBot({
        "host": ip,
        "port": port,
        "username": username
    })

    @Once(bot, 'spawn')
    def handler_spawn(_):
        bot.chat('/gamemode 1')

    @On(bot, 'messagestr')
    def handler_messagestr(_1, _2, _3, _4, _5,*args):
        if _2 == 'Unknown or incomplete command, see below for error':
            q.put({"name":"Cheats","value":f'<@&1413150268266254336>'})
            bot.quit()
        elif _2 in ('Incorrect argument for command', 'Set own game mode to Creative Mode'):
            q.put({"name":"Cheats","value":f'<@&1413150208727973998>'})
            run_script(bot)
            bot.quit()


    @On(bot, 'kicked')
    def handler_kicked(_1, reason, _2):
        q.put({"name":"Kicked","value":f'<@&1413150345684848713> {reason}'})


def run_bot(ip,port,username):
    q = queue.Queue()
    makebot(ip,port,username,q)
    return q

def getcontent(result):
    if result.get('name')=="Kicked": return "<@&1412851881939701780>\n<@&1413150345684848713>"
    elif result=={"name":"Cheats","value":f'<@&1413150208727973998>'}: return "<@&1412851881939701780>\n<@&1413150208727973998>"
    elif result=={"name":"Cheats","value":f'<@&1413150268266254336>'}: return "<@&1412851881939701780>\n<@&1413150268266254336>"
    else: print(result)



def dowebhook(port, desc, players, protocol, name):
    if protocol <= 767:
        q=run_bot(ip, port, 'nuLL')
        try:
            result = q.get(timeout=30)
            
            webhook = DiscordWebhook(
                url=WEBHOOK,
                username='archx2 scanner :D',
                content=getcontent(result,)
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
            embed.set_thumbnail(url=f"https://ping.cornbread2100.com/favicon?ip={ip}&port={port}&errors=false")

            embed.add_embed_field(name=result.get('name'), value=result.get('value'))
        except queue.Empty:
            return
    else:
        webhook = DiscordWebhook(
            url=WEBHOOK,
            username='archx2 scanner :D',
            content='<@&1412851881939701780>\n<@&1413392210271014953>'
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
        embed.set_thumbnail(url=f"https://ping.cornbread2100.com/favicon?ip={ip}&port={port}&errors=false")

        embed.add_embed_field(name="Error",value="<@&1413392210271014953>")


        
    webhook.add_embed(embed)
    webhook.execute()


def check_port(port):
    try:
        server = JavaServer(ip, port)
        status = server.status()
        desc = status.description
        if status.players.max == 8 and " - " in desc:
            print(f'found smth on {ip}:{port}\n')
            dowebhook(port, desc, status.players.online, status.version.protocol, status.version.name)
        else:
            pass
    except:
        pass  # no server or timeout


with ThreadPoolExecutor(max_workers=int(envval('./.env')['maxworkers'])) as executor:
    executor.map(check_port, range(start_port, end_port + 1))

