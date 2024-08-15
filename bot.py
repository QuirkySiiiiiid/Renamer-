import logging
import logging.config
import asyncio
import datetime
import subprocess
from pyrogram import Client
from pyrogram.errors import BadMsgNotification
from config import API_ID, API_HASH, BOT_TOKEN, FORCE_SUB, PORT
from aiohttp import web
from plugins.web_support import web_server

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
                synchronize_time()  # Ensure time is synchronized before starting
                log_current_time()  # Log the current time for debugging
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
                        logging.warning("Make Sure Bot admin in force sub channel")             
                        self.force_channel = None
                app = web.AppRunner(await web_server())
                await app.setup()
                bind_address = "0.0.0.0"
                await web.TCPSite(app, bind_address, PORT).start()
                logging.info(f"{me.first_name} ✅✅ BOT started successfully ✅✅")
                break  # Exit the retry loop on success
            except BadMsgNotification as e:
                logging.error(f"Retry {attempt + 1}/{max_retries} failed with BadMsgNotification error: {e}")
                synchronize_time()  # Ensure system time is synchronized
                await asyncio.sleep(5)  # Wait before retrying
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped 🙄")


def synchronize_time():
    """Ensure system time is synchronized with NTP."""
    try:
        subprocess.run(['sudo', 'timedatectl', 'set-ntp', 'on'], check=True)
        logging.info("System time synchronized with NTP.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to synchronize time: {e}")

def log_current_time():
    """Log the current time for debugging purposes."""
    logging.info(f"Current time: {datetime.datetime.now()}")

bot = Bot()
bot.run()