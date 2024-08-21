import logging
import logging.config
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.errors import BadMsgNotification
from config import API_ID, API_HASH, BOT_TOKEN, FORCE_SUB, PORT
from aiohttp import web
from plugins.web_support import web_server

# Configure logging
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

class Bot(Client):

    def __init__(self):
        super().__init__(
            name="WebX-Renamer",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        max_retries = 3  # Number of retry attempts
        for attempt in range(max_retries):
            try:
                self.log_current_time()  # Log the current time for debugging
                await super().start()
                me = await self.get_me()
                self.mention = me.mention
                self.username = me.username
                self.force_channel = FORCE_SUB
                if FORCE_SUB:
                    try:
                        link = await self.export_chat_invite_link(FORCE_SUB)
                        self.invitelink = link
                    except Exception as e:
                        logging.warning(e)
                        logging.warning("Make sure the bot is an admin in the force-sub channel")
                        self.force_channel = None
                app = web.AppRunner(await web_server())
                await app.setup()
                bind_address = "0.0.0.0"
                await web.TCPSite(app, bind_address, PORT).start()
                logging.info(f"{me.first_name} ✅✅ BOT started successfully ✅✅")
                break  # Exit the retry loop on success
            except BadMsgNotification as e:
                logging.error(f"Retry {attempt + 1}/{max_retries} failed with BadMsgNotification error: {e}")
                self.log_current_time()  # Log the time before retrying
                await asyncio.sleep(5)  # Wait before retrying
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped 🙄")

    @staticmethod
    def log_current_time():
        """Log the current system time for debugging purposes."""
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logging.info(f"Current system time (UTC): {current_time}")

# Define a new instance of Client
bot = Bot()

# Define a message handler for private messages
@bot.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from Pyrogram!")

# Start the bot
if __name__ == "__main__":
    bot.run()
