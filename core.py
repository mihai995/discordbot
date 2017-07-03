from util import getGoogleMeme, getMemes, BOT_NAME, BOT_CHANNEL_ID, MAIN_CHANNEL_ID, CMD_MARKER, MEME_THRESHOLD
import asyncio, ahocorasick, discord, random

class DiscordBot():
  def __init__(self, bot):
    self.bot = bot
    self.server = next(x for x in self.bot.servers)
    self.main_channel = self.server.get_channel(MAIN_CHANNEL_ID)
    self.logger = self.server.get_channel(BOT_CHANNEL_ID)

  async def send_message(self, msg, arg = None):
    if arg == None:
      arg = self.main_channel
    elif type(arg) == discord.Message:
      arg = arg.channel
    await self.bot.send_message(arg, msg)

  async def log(self, query, msg):
    nick = query.author.nick if query.author.nick else query.author.name
    await self.send_message('[{}] {}'.format(nick, msg), self.logger)

  async def rename(self, name):
    await self.bot.http.change_my_nickname(self.server.id, name)

  async def reply(self, query, msg, AS = None):
    if AS:  self.rename(AS)
    await self.send_message(query.author.mention + ' ' + msg, query)
    if AS:  self.rename(BOT_NAME)

  async def attach(self, query, filename, extra_text = ''):
    if extra_text:
      extra_text = query.author.mention() + ' ' + extra_text
    if filename[0] != '/':
      filename = MEME_FOLDER + filename
    await self.bot.send_file(query.channel, filename, content = extra_text)

  async def attach_meme(self, query):
    options = getMemes(query.content)
    if len(options) > 0:
      await self.attach(query, random.choice(options)[1])
    elif random.random() < MEME_THRESHOLD:
      type,meme = getGoogleMeme(query.content)
      if type != None:
        tmp = tempfile.NamedTemporaryFile(suffix = type)
        tmp.write(meme)
        await self.attach(query, tmp.name)

  def handlers(self):
    return {x:getattr(self, x) for x in dir(self) if x.startswith(CMD_MARKER)}
