#!/usr/bin/python3.5

from core   import DiscordBot
from define import DefineBot
from music  import MusicBot
from simple import SimpleBot
import asyncio, discord, re, signal, sys

TOKEN  = 'MzEyNTk1NjQwMzQzNTkyOTYy.C_dbjw.2QLPK6IMxjRmxYEVTwOeUKb3tXY'
MARKER = re.compile('^[!\\`]|bot |ds |sudo ')
HANDLE = {}

bot  = discord.Client()
core = None

async def handler():
  await bot.logout()
  for task in asyncio.Task.all_tasks():
    task.cancel()

@bot.event
async def on_ready():
  global core
  for name,SubBot in globals().items():
    if name.endswith('Bot'):
      HANDLE.update(SubBot(bot).handlers())
  core = DiscordBot(bot)

@bot.event
async def on_message(msg):
  args = MARKER.sub(DiscordBot.CMD_, msg.content.lower()).split(maxsplit = 1) + ['']
  handle = HANDLE.get(args[0])
  if handle != None:
    await core.log(msg, msg.content)
    await bot.delete_message(msg)
    msg.content = args[1]
    await handle(msg)

bot.loop.add_signal_handler(signal.SIGINT, asyncio.async, handler())
bot.run(TOKEN)
