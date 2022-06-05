import discord
import secret
from pprint import pprint
import random
import pickle
import os
from collections import defaultdict

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
    c = int(c)
    d = int(d)
    if c < 1 or c > 100:
        return None
    if d < 1 or d > 1000:
        return None
    return (int(c), int(d), m)

def do_die_roll(die_roll):
        c, d, m = die_roll
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

def chompf(s, f):
    i = s.find(f)
    if i == -1:
        return None
    return s[:i], s[i+len(f):]

class State:
    def __init__(self):
        if os.path.exists('storage'):
            self.load()
        else:
            self.vars = defaultdict(dict)

    def load(self):
        with open('storage', 'rb') as f:
            self.vars = pickle.load(f)

    def save(self):
        with open('storage', 'wb') as f:
            pickle.dump(self.vars, f)

    def set(self, author, var, n):
        self.vars[author][var] = n
        self.save()

    def get(self, author, var):
        r = self.vars[author][var]
        if r.isdigit():
            return int(r)
        return do_die_roll(parse_die_roll(r))

    def has(self, author, var):
        return var in self.vars[author]

    def backup(self, author):
        l = [ f"set {v} {n}" for v, n in self.vars[author].items() ]
        return '\n'.join(l)

state = State()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name != 'dice':
        return

    m = message.content
    a = message.author.name
    die_roll = parse_die_roll(m)
    if die_roll:
        s = do_die_roll(die_roll)
        await message.reply(s)
    elif m.startswith('set '):
        _, m = chompf(m, 'set ')
        v, n = chompf(m, ' ')
        if not v.isalpha():
            return
        if n.isdigit():
            state.set(a, v, n)
            await message.reply(f'set {v} to {n}')
        die_roll = parse_die_roll(n)
        if die_roll:
            state.set(a, v, n)
            await message.reply(f'set {v} to {n}')
    elif state.has(a, m):
        s = state.get(a, m)
        await message.reply(s)
    elif m == 'backup':
        await message.reply(state.backup(a))
    elif m == 'help':
        await message.reply('''2d6 -- roll 2d6
2d6+10 -- roll 2d6+10
set {var} {number|roll} -- save a roll or number in a variable
{var} -- print a saved number or roll a saved die
backup -- print out all your saved variables

code at https://github.com/hcnelson99/dice
''')


if __name__ == '__main__':
    client.run(secret.TOKEN)
