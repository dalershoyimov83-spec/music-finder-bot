import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from shazamio import Shazam
from aiohttp import web

# Tokenni Render settingsdan olamiz
API_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
shazam = Shazam()

# --- Render uchun Keep-alive qismi ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_webhook():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render beradigan PORT orqali ulanadi
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()

# --- Bot funksiyalari ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Salom! Menga musiqa nomini yozing yoki ovozli xabar yuboring. Men uni 2 soniyada topaman! ✨")

@dp.message_handler(content_types=['voice', 'audio'])
async def handle_audio(message: types.Message):
    msg = await message.answer("Qidirilmoqda... 🔍")
    
    # Audio faylni yuklab olish
    file_id = message.voice.file_id if message.voice else message.audio.file_id
    file = await bot.get_file(file_id)
    file_path = f"{file_id}.ogg"
    await bot.download_file(file.file_path, file_path)
    
    # Shazam orqali aniqlash
    out = await shazam.recognize_song(file_path)
    
    if out.get('track'):
        track = out['track']
        title = track.get('title')
        artist = track.get('subtitle')
        await msg.edit_text(f"✅ Topildi!\n\n🎵 Nomi: {title}\n👤 Ijrochi: {artist}")
    else:
        await msg.edit_text("Afsuski, bu musiqani topa olmadim 😔")
    
    # Faylni tozalash
    if os.path.exists(file_path):
        os.remove(file_path)

# --- Ishga tushirish ---
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # Render o'chirib qo'ymasligi uchun portni ochamiz
    loop.create_task(start_webhook())
    print("Bot ishga tushdi...")
    executor.start_polling(dp, skip_updates=True)
  
