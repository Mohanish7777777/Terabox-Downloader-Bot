from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import logging
import asyncio
from datetime import datetime
from pyrogram.enums import ChatMemberStatus
from dotenv import load_dotenv
import os
from video import download_video, upload_video
from web import keep_alive

# Load environment variables
load_dotenv('config.env', override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Retrieve environment variables
api_id = os.environ.get('TELEGRAM_API')
api_hash = os.environ.get('TELEGRAM_HASH')
bot_token = os.environ.get('BOT_TOKEN')
dump_id = int(os.environ.get('DUMP_CHAT_ID', '0'))
fsub_id = int(os.environ.get('FSUB_ID', '0'))

# Validate environment variables
if not all([api_id, api_hash, bot_token, dump_id, fsub_id]):
    logging.error("One or more required environment variables are missing! Exiting now.")
    exit(1)

# Initialize the bot
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAEYonplzwrczhVu3I6HqPBzro3L2JU6YAACvAUAAj-VzAoTSKpoG9FPRjQE")
    await asyncio.sleep(2)
    await sticker_message.delete()
    user_mention = message.from_user.mention
    reply_message = (
        f"ᴡᴇʟᴄᴏᴍᴇ, {user_mention}.\n\n"
        "🌟 ɪ ᴀᴍ ᴀ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ. sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ ɪ ᴡɪʟʟ ᴅᴏᴡɴʟᴏᴀᴅ ᴡɪᴛʜɪɴ ғᴇᴡ sᴇᴄᴏɴᴅs ᴀɴᴅ sᴇɴᴅ ɪᴛ ᴛᴏ ʏᴏᴜ ✨."
    )
    join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/MohanishX")
    developer_button = InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ ⚡️", url="https://t.me/Mohanish7777777")
    reply_markup = InlineKeyboardMarkup([[join_button, developer_button]])

    video_file_id = "/app/Jet-Mirror.mp4"
    if os.path.exists(video_file_id):
        await client.send_video(
            chat_id=message.chat.id,
            video=video_file_id,
            caption=reply_message,
            reply_markup=reply_markup
        )
    else:
        await message.reply_text(reply_message, reply_markup=reply_markup)

async def is_user_member(client, user_id):
    try:
        member = await client.get_chat_member(fsub_id, user_id)
        logging.info(f"User {user_id} membership status: {member.status}")
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        logging.error(f"Error checking membership status for user {user_id}: {e}")
        return False

@app.on_message(filters.text)
async def handle_message(client, message: Message):
    if message.from_user is None:
        logging.error("Message does not contain user information.")
        return

    user_id = message.from_user.id
    user_mention = message.from_user.mention
    is_member = await is_user_member(client, user_id)

    if not is_member:
        join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/MohanishX")
        reply_markup = InlineKeyboardMarkup([[join_button]])
        await message.reply_text("ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ.", reply_markup=reply_markup)
        return

    valid_domains = [
        'terabox.com', 'nephobox.com', '4funbox.com', 'mirrobox.com', 
        'momerybox.com', 'teraboxapp.com', '1024tera.com', 
        'terabox.app', 'gibibox.com', 'goaibox.com', 
        'terasharelink.com', 'teraboxlink.com'
    ]

    terabox_link = message.text.strip()
    
    if not any(domain in terabox_link for domain in valid_domains):
        await message.reply_text("ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ.")
        return

    reply_msg = await message.reply_text("sᴇɴᴅɪɴɢ ʏᴏᴜ ᴛʜᴇ ᴍᴇᴅɪᴀ...🤤")

    try:
        file_path, thumbnail_path, video_title = await download_video(terabox_link, reply_msg, user_mention, user_id)
        await upload_video(client, file_path, thumbnail_path, video_title, reply_msg, dump_id, user_mention, user_id, message)
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        await reply_msg.edit_text("Api has given a Broken Download Link. Don't contact the Owner for this issue.")

if __name__ == "__main__":
    keep_alive()
    app.run()
