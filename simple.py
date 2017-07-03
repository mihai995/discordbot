from core import DiscordBot
from urllib.request import Request, urlretrieve, urlopen
from util import MEME_FOLDER, memeifiers, read_all_memes, getMemes
import asyncio, inflect, os, random, sys

intToText = inflect.engine().number_to_words

class SimpleBot(DiscordBot):
  async def cmd_restart(self, msg):
    await self.bot.logout()
    os.execv(sys.argv[0], sys.argv)

  async def cmd_roll(self, msg):
    if not msg.content:
      filename = 'dieroll{}'.format(intToText(random.randrange(1, 7)))
      await self.attachMeme(msg, filename, 'Behold the result of the demonic dice roll')
      return
    rng = [int(x) for x in msg.content.split(':')]
    rng[max(1, len(rng) - 1)] += 1
    await self.reply(msg, 'I have drawn {} out of my demonic hat'.format(random.randrange(*rng)))

  async def cmd_meme(self, msg):
    await self.attach_meme(msg)

  async def cmd_memeify(self, msg):
    if msg.author.id not in memeifiers:
      return await self.reply(msg, 'You are not allowed to create memes my friend')
    meme_folder = MEME_FOLDER + memeifiers[msg.author.id] + '/'
    if len(msg.attachments) == 1:
      pic = msg.attachments[0]['proxy_url']
      react = msg.content
    else:
      pic,react = msg.content.rsplit(':', maxsplit=1)

    if pic.startswith('http'):
      name = pic.rsplit('/', maxsplit=1)[-1]
      if len(name) < 2 or name.find('.') == -1:
        return await self.reply(msg, 'I could not infer a good meme name: ' + name)
      while os.path.exists(meme_folder + name):
        name = name.replace('.', '.1.')
      print(pic, meme_folder + name)
      H = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}
      with open(meme_folder + name, 'wb') as file:
        file.write(urlopen(Request(pic, headers = H)).read())
    else:
      name = getMemes(pic)[0][1]
    if react != None:
      with open(meme_folder + 'react.txt', 'a') as file:
        file.write(name + ': ' + react)
    read_all_memes()
