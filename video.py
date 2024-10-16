import re
import requests
import aria2p
from datetime import datetime
from status import format_progress_bar
import asyncio
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Initialize aria2 API client
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)

# Set global options for aria2
options = {
    "max-tries": "50",
    "retry-wait": "3",
    "continue": "true"
}
aria2.set_global_options(options)

async def download_video(url, reply_msg, user_mention, user_id):
    match = re.search(r'/s/([a-zA-Z0-9_-]+)', url)
    if not match:
        await reply_msg.edit_text("Invalid Terabox link. Please provide a valid URL.")
        return None, None, None
    
    video_id = match.group(1)
    
    # Request to API to get download link
    response = requests.get(f"https://apis.forn.fun/tera/data.php?id={video_id}")
    response.raise_for_status()
    data = response.json()

    if "download" not in data:
        await reply_msg.edit_text("Failed to get download link from API. Please try again later.")
        return None, None, None

    download_link = data["download"]
    video_title = data.get("name", "Downloaded Video")
    thumbnail_url = data.get("thumbnail", None)

    try:
        download = aria2.add_uris([download_link])
        start_time = datetime.now()

        while not download.is_complete:
            download.update()
            percentage = download.progress
            done = download.completed_length
            total_size = download.total_length
            speed = download.download_speed
            eta = download.eta
            elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
            progress_text = format_progress_bar(
                filename=video_title,
                percentage=percentage,
                done=done,
                total_size=total_size,
                status="Downloading",
                eta=eta,
                speed=speed,
                elapsed=elapsed_time_seconds,
                user_mention=user_mention,
                user_id=user_id,
                aria2p_gid=download.gid
            )
            await reply_msg.edit_text(progress_text)
            await asyncio.sleep(2)

        if download.is_complete:
            file_path = download.files[0].path

            # Download thumbnail if available
            thumbnail_path = None
            if thumbnail_url:
                thumbnail_path = "thumbnail.jpg"
                thumbnail_response = requests.get(thumbnail_url)
                with open(thumbnail_path, "wb") as thumb_file:
                    thumb_file.write(thumbnail_response.content)

            await reply_msg.edit_text("ᴜᴘʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ᴠɪᴅᴇᴏ...🎥")
            return file_path, thumbnail_path, video_title
    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        await reply_msg.edit_text("An error occurred while downloading the video. Please try again later.")
        return None, None, None

async def upload_video(client, file_path, thumbnail_path, video_title, reply_msg, dump_id, user_mention, user_id, message):
    try:
        await client.send_video(
            chat_id=dump_id,
            video=file_path,
            caption=f"Video uploaded by {user_mention}\nTitle: {video_title}",
            thumb=thumbnail_path,
            reply_to_message_id=message.message_id
        )
        await reply_msg.edit_text("Video uploaded successfully! 🎉")
    except Exception as e:
        logging.error(f"Error uploading video: {e}")
        await reply_msg.edit_text("An error occurred while uploading the video. Please try again later.")
    finally:
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

