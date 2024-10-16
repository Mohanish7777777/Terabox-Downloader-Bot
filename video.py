import re
import requests
import aria2p
from datetime import datetime
from status import format_progress_bar
import asyncio
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)

options = {
    "max-tries": "50",
    "retry-wait": "3",
    "continue": "true"
}

aria2.set_global_options(options)

async def download_video(url, reply_msg, user_mention, user_id):
    # Extract the ID from the URL
    match = re.search(r'/s/([a-zA-Z0-9_-]+)', url)
    if not match:
        await reply_msg.edit_text("Invalid Terabox link. Please provide a valid URL.")
        return None, None, None
    
    video_id = match.group(1)
    
    # Make the request to the new API
    response = requests.get(f"https://apis.forn.fun/tera/data.php?id={video_id}")
    response.raise_for_status()
    data = response.json()

    if "download" not in data:
        await reply_msg.edit_text("Failed to get download link from API. Please try again later.")
        return None, None, None

    download_link = data["download"]
    video_title = data.get("name", "Downloaded Video")
    thumbnail_url = data.get("thumbnail", None)  # Thumbnail might not always be present

    try:
        # Start download using aria2
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

            await reply_msg.edit_text("ᴜᴘʟᴏᴀᴅɪɴɢ...")

            return file_path, thumbnail_path, video_title

    except Exception as e:
        logging.error(f"Error handling message: {e}")
        buttons = [
            [InlineKeyboardButton("🚀 Direct Download", url=download_link)]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await reply_msg.reply_text(
            "Failed to download the video. You can try downloading it manually using the link below:",
            reply_markup=reply_markup
        )
        return None, None, None
