from core import DiscordBot
from urllib.request import urlopen
import asyncio, discord, re

VIDEO   = re.compile('/watch\\?v=[a-zA-Z0-9_]{8,100}')
YOUTUBE = re.compile('youtube\\.com|youtu.be')

class MusicBot(DiscordBot):
  def __init__(self, bot):
    super().__init__(bot)
    self.player = None
    self.volume = 0.5

  @staticmethod
  def get_youtube_link(query):
    query = query.lstrip('play').strip()
    if YOUTUBE.match(query):
      return query
    query = ''.join('%{:02X}'.format(ord(x)) for x in query)
    url = 'http://www.youtube.com/results?search_query=' + query
    vid = VIDEO.findall(urlopen(url).read().decode('utf-8'))[0]
    return 'http://www.youtube.com' + vid

  async def voice_change(self, msg, wanted):
    for voice in list(self.bot.voice_clients):
      if voice.channel == wanted:
        return voice
      try:
        await voice.disconnect()
        self.bot.connection._remove_voice_client(voice.server.id)
      except:
        pass
    return await self.bot.join_voice_channel(wanted)

  async def cmd_volume(self, msg):
    if self.player != None:
      self.volume = self.player.volume = 0.01 * float(msg.content)

  async def cmd_pause(self, msg):
    if self.player != None and self.player.is_playing():
      self.player.pause()

  async def cmd_play(self, msg):
    channel = msg.author.voice.voice_channel
    if not type(channel) is discord.Channel:
      await reply(bot, msg, 'you are not in any voice channel')
      return
    if not msg.content:
      if self.player != None and not self.player.is_playing():
        self.player.resume()
      return
    if self.player != None:
      self.player.stop()
    voice = await self.voice_change(msg, channel)
    self.player = await voice.create_ytdl_player(MusicBot.get_youtube_link(msg.content))
    self.player.volume = self.volume
    self.player.start()
