from core import DiscordBot
import asyncio

class DefineBot(DiscordBot):
  async def cmd_whatis(self, msg):
    await self.reply(msg, 'functionality not yet implemented')
