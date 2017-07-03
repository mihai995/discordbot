from core import DiscordBot
from urllib.request import urlopen
from datetime import timedelta
from util import BANNED_TAGS, DEFAULT_VOLUME, PLAYLIST_MAX_SIZE
import asyncio, bs4, collections, discord, enum, random, re, time

YOUTUBE_URL = re.compile('.*(youtube\\.com|youtu\\.be)')
VIDEO = re.compile('/watch\\?v=[a-zA-Z0-9_]{8,100}')
YT = 'https://www.youtube.com'

class YtPlayer:
  def getURL(link):
    if not YOUTUBE_URL.match(link):
      query = '/results?search_query=' + ''.join("%{:02X}".format(ord(x)) for x in link)
      link = YT + VIDEO.findall(urlopen(YT + query).read().decode('utf-8'))[0]
    return link

  def __init__(self, query, stop_handler):
    self.url = YtPlayer.getURL(query)
    self.title = query
    self.player = None
    self._play_time = None
    self._remaining = None
    self.stop_handler = stop_handler

  def volume(self, volume):
    if self.player != None:
      self.player.volume = 0.01 * volume

  async def play(self, bot):
    if not self.valid():
      return
    if self.player == None or self.player.is_done():
      self.player = await bot.voice.create_ytdl_player(self.url, after = self.stop_handler)
      self._remaining = self.player.duration
      self.title = self.player.title
    self.volume(bot.volume)
    if not self.player.is_alive():
      self.player.start()
    elif not self.player.is_playing():
      self.player.resume()
    else:
      return
    self._play_time = time.time()

  def is_playing(self):
    return self.player != None and self.player.is_playing()

  def symbol(self):
    return '►' if self.is_playing() else '❚❚'

  def pause(self):
    if self.player != None and self.player.is_playing():
      self.player.pause()
      self._remaining -= time.time() - self._play_time

  def kill(self, gently = False):
    if self.player != None:
      if gently:
        self.player._after = None
      self.player.stop()
      self.player = None

  def __str__(self):
    if self.player == None:
      return self.title
    remaining = self._remaining
    if self.player.is_playing():
      remaining -= time.time() - self._play_time
    return '{:40.40s} {}'.format(self.title, timedelta(seconds = int(remaining)))

  def valid(self):
    soup = bs4.BeautifulSoup(urlopen(self.url), 'lxml')
    for meta in soup.find_all('meta'):
      if meta.get('name') == 'keywords' and BANNED_TAGS.search(meta['content'].lower()):
        return False
    for div in soup.find_all('div'):
      if div.get('id') == 'watch-description-text' and BANNED_TAGS.search(str(div).lower()):
        return False
    return True
