from core import DiscordBot
import asyncio, os, random, sys

class SimpleBot(DiscordBot):
  async def cmd_restart(self, msg):
#    await self.satanicReply(msg, 'brb')
    await self.bot.logout()
    os.execv(sys.argv[0], sys.argv)

  async def cmd_roll(self, msg):
    if not msg.content:
      await self.attachMeme(msg, 'die{}'.format(random.randrange(1, 7)), 'Behold the result of the demonic dice roll')
      return
    rng = [int(x) for x in msg.content.split(':')]
    rng[max(1, len(rng) - 1)] += 1
    await self.reply(msg, 'I have drawn {} out of my demonic hat'.format(random.randrange(*rng)))
