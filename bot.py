import discord
import secret
from pprint import pprint
import random

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


def parse_die_roll(s):
    i = s.find('d')
    if i == -1:
        return None
    c = s[:i]
    d = s[i+1:]
    if c == '':
        c = '1'

    neg = False

    if '+' in d:
        i = d.find('+')
        d, m = d[:i], d[i+1:]
    elif '-' in d:
        i = d.find('-')
        d, m = d[:i], d[i+1:]
        neg = True
    else:
        m = '0'

    if not c.isdigit() or not d.isdigit() or not m.isdigit():
        return None
    m = int(m)
    if neg: m = - m
    return (int(c), int(d), m)

def do_die_roll(die_roll):
        c, d, m = die_roll
        if c < 1 or c > 100:
            return
        if d < 1 or d > 1000:
            return
        rolls = []
        total = 0
        for _ in range(c):
            roll = random.randint(1, d)
            rolls.append(str(roll))
            total += roll
        total += m
        if m == 0:
            m = ''
        elif m < 0:
            m = f' - {-m}'
        else:
            m = f' + {m}'
        if c > 1:
            return f"{total} ({' + '.join(rolls)}{m})"
        elif m:
            return f"{total} ({rolls[0]}{m})"
        else:
            return str(total)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name != 'dice':
        return

    m = message.content
    die_roll = parse_die_roll(m)
    if die_roll:
        s = do_die_roll(die_roll)
        await message.reply(s)


client.run(secret.TOKEN)
