import asyncio

class DiscordBot():
  BOT_CHANNEL_ID = '312604110547451904'
  CMD_ = 'cmd_'
  MEME = '/media/Storage/Memes/{}.png'

  def __init__(self, bot):
    self.bot = bot
    self.server = next(x for x in self.bot.servers)
    self.logger = self.server.get_channel(DiscordBot.BOT_CHANNEL_ID)

  async def message(self, channel, query, msg):
    await self.bot.send_message(channel, '<@{}> {}'.format(query.author.id, msg))

  async def log(self, query, msg):
    await self.bot.send_message(self.logger, '[{}] {}'.format(query.author.nick, msg))

  async def rename(self, name):
    await self.bot.http.change_my_nickname(self.server.id, name)

  async def reply(self, query, msg):
    await self.message(query.channel, query, msg)

  async def satanicReply(self, query, msg):
    await self.rename('Satan')
    await self.reply(query, msg)
    await self.rename('Demonic Servant')

  async def attachMeme(self, query, name, msg):
    msg = '<@{}> {}'.format(query.author.id, msg)
    await self.bot.send_file(query.channel, DiscordBot.MEME.format(name), content = msg)

  def handlers(self):
    return {x:getattr(self, x) for x in dir(self) if x.startswith(DiscordBot.CMD_)}
