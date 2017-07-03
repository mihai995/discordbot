#!/usr/bin/python3.5

from core   import DiscordBot
from define import DefineBot
from music  import MusicBot
from simple import SimpleBot
from util import CMD_MARKER, CMD_MARKER_TEXT, PROTECTED_IDS, LOGIN_TOKEN
import asyncio, discord, re, signal, sys

bot = discord.Client()
core = None
handle = {}

async def handler():
  await bot.logout()
  for task in asyncio.Task.all_tasks():
    task.cancel()

@bot.event
async def on_ready():
  global core
  for name,SubBot in globals().items():
    if name.endswith('Bot'):
      handle.update(SubBot(bot).handlers())
  core = DiscordBot(bot)

@bot.event
async def on_message(msg):
  args = CMD_MARKER_TEXT.sub(CMD_MARKER, msg.content).split(maxsplit = 1) + ['']
  handler = handle.get(args[0].lower())
  if handler != None:
    await core.log(msg, msg.content)
    await bot.delete_message(msg)
    msg.content = args[1]
    await handler(msg)
  else:
    await core.attach_meme(msg)

@bot.event
async def on_voice_state_update(*_):
  if bot.voice_clients and len(next(x for x in bot.voice_clients).channel.voice_members) == 1:
    await handle.get('cmd_leave')(None)

@bot.event
async def on_member_update(before, after):
  if before.id in PROTECTED_IDS and before.nick != after.nick:
    await core.send_message('{} someone changed your nickname'.format(after.mention))

bot.loop.add_signal_handler(signal.SIGINT, asyncio.async, handler())
bot.run(LOGIN_TOKEN)
