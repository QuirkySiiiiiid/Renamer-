import logging
import logging.config
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, ChatAdminRequired, ChatWriteForbidden

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
        try:
            await super().start()
            me = await self.get_me()
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

            # Try sending a message to a chat ID, with integer conversion
            try:
                chat_id = YOUR_CHAT_ID  # Replace with the valid peer ID (chat/group/channel ID)

                # Convert chat_id to integer if it is a string
                if isinstance(chat_id, str):
                    chat_id = int(chat_id)

                await self.send_message_with_workaround(chat_id, "Hello with workaround!")
            except ValueError:
                logging.error("Chat ID must be an integer.")
            except PeerIdInvalid:
                logging.error("The provided chat ID is invalid. Make sure the bot is a member of the group or channel.")
            except ChatAdminRequired:
                logging.error("Bot is not an admin in the target group or channel.")
            except ChatWriteForbidden:
                logging.error("Bot does not have permission to write in the target group or channel.")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")

            logging.info(f"{me.first_name} ✅✅ BOT started successfully ✅✅")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped 🙄")

    async def send_message_with_workaround(self, peer_id, message):
        """A workaround to handle peer ID issues."""
        try:
            chat = await self.get_chat(peer_id)
            if chat.username:
                await self.send_message(chat.username, message)
            else:
                await self.send_message(chat.id, message)
        except PeerIdInvalid:
            logging.error(f"Peer ID {peer_id} is invalid.")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

bot = Bot()
bot.run()
