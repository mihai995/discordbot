from core import DiscordBot
from urllib.request import urlopen
from datetime import timedelta
from util import BANNED_TAGS, DEFAULT_VOLUME, PLAYLIST_MAX_SIZE
from ytplayer import YtPlayer
import asyncio, bs4, collections, discord, enum, random, re, time

REJECT_MSG = 'Sorry m8, I don\'t play shit music <:pepefuckyou:268062577039376386>'

class MusicBot(DiscordBot):
  class Mode(enum.Enum):
    NONE = 0
    ONE = 1
    ALL = 2

  def __init__(self, bot):
    super().__init__(bot)
    self.players = collections.deque(maxlen = PLAYLIST_MAX_SIZE)
    self.volume = DEFAULT_VOLUME
    self.voice = None
    self.mode = MusicBot.Mode.ALL

  @property
  def top(self):
    class PlayerDummy:
      def __getattr__(self, *_):
        return lambda *_:self
      def __setattr__(self, *_):
        pass
    return self.players[0] if self.players else PlayerDummy()

  async def cmd_skip(self, msg = None):
    self.top.kill()

  def stop_handler(self, player):
    async def wrapper():
      if player.error != None:
        await self.send_message('YTDL has just crashed ... fuck this shit')
      await self.top.play(self)

    if self.mode == MusicBot.Mode.NONE:
      self.players.popleft()
    elif self.mode == MusicBot.Mode.ALL:
      self.players.rotate(-1)
    self.bot.loop.create_task(wrapper())

  async def cmd_drop(self, msg):
    mode = self.mode
    self.mode = self.Mode.NONE
    self.top.kill()
    self.mode = mode

  async def cmd_mode(self, msg):
    self.mode = self.Mode[msg.content.strip().upper()]

  async def cmd_volume(self, msg):
    self.volume = float(msg.content)
    self.top.volume(self.volume)

  async def cmd_shuffle(self, msg):
    self.top.pause()
    random.shuffle(self.players)
    self.top.play(self)

  async def cmd_purge(self, msg):
    for player in self.players:
      player.kill(True)
    self.players.clear()

  async def cmd_leave(self, msg):
    if self.voice == None:
      return
    current = self.voice.channel
    if msg == None or self.voice.channel == msg.author.voice.voice_channel:
      await self.voice.disconnect()
      self.bot.connection._remove_voice_client(self.voice.server.id)
      self.voice = None

  async def cmd_join(self, msg):
    target = msg.author.voice.voice_channel
    if not type(target) is discord.Channel:
      return await self.reply(msg, 'you are not in any voice channel')
    if self.voice != None  and self.voice.channel != target:
      await self.cmd_leave(msg)
    if self.voice == None:
      self.voice = await self.bot.join_voice_channel(target)

  async def cmd_enq(self, msg, appender = collections.deque.append):
    player = YtPlayer(msg.content, self.stop_handler)
    if not player.valid():
      await self.reply(msg, REJECT_MSG)
    else:
      appender(self.players, player)

  async def cmd_play(self, msg = None):
    await self.cmd_join(msg)
    if msg and msg.content.strip():
      self.top.pause()
      await self.cmd_enq(msg, collections.deque.appendleft)
    await self.top.play(self)

  async def cmd_pause(self, msg):
    self.top.pause()

  async def cmd_list(self, msg):
    text = ''
    for index, player in enumerate(self.players):
      if index == 0:
        text += '\n({}) {}'.format(player.symbol(), player)
      else:
        text += '\n({:>2d}) {}'.format(index + 1, player)
    text += '\n\nVolume: {:2.0f}%  Repeat{}'.format(self.volume, self.mode)
    await self.reply(msg, text)
