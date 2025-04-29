import asyncio
import csv
import os
from fastapi import FastAPI
import uvicorn
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from datetime import datetime, timedelta, timezone

# --------- إعدادات المستخدم ---------
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
session_string = os.getenv('SESSION_STRING')
bot_token = os.getenv('BOT_TOKEN')
your_channel_username = os.getenv('YOUR_CHANNEL')

csv_file = 'sweepstakes_log.csv'

# الكلمات المفتاحية
keywords = ["УЧАСТВОВАТЬ", "جائزة", "سحب", "شحن", "ربح", "contest", "giveaway", "randomgodbot"]
ignore_words = ["fee", "Bid"]

# --------- وظائف ---------
def update_csv(data):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["التاريخ", "القناة/المجموعة", "رابط الرسالة", "نص الرسالة"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    print("[+] تم تحديث ملف CSV")

def read_sweepstakes():
    sweepstakes = []
    if os.path.isfile(csv_file):
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sweepstakes.append(row)
    return sweepstakes

async def send_alert(bot, chat_name, message_link, text_snippet, time_detected):
    text = f"""📢 **مسابقة جديدة مكتشفة!**

🏷️ **القناة:** [{chat_name}]({message_link})  
🕒 **التاريخ:** {time_detected}

📝 **التفاصيل:**  
{text_snippet}
"""
    await bot.send_message(your_channel_username, text, link_preview=False)

# --------- إعداد تيليجرام ---------
client = TelegramClient(StringSession(session_string), api_id, api_hash)
bot = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

async def fetch_old_messages(client, bot):
    print("[*] جاري فحص الرسائل القديمة...")
    dialogs = await client.get_dialogs()
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    for dialog in dialogs:
        entity = dialog.entity
        if hasattr(entity, 'megagroup') or hasattr(entity, 'broadcast'):
            try:
                async for message in client.iter_messages(entity.id, limit=50):
                    if message.text:
                        message_text = message.text.lower()
                        if any(word in message_text for word in ignore_words + ["finished"]):
                            continue
                        if any(word in message_text for word in keywords) and message.date > since:
                            chat_name = getattr(entity, 'title', 'مجهول')
                            now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                            message_link = None
                            if hasattr(entity, 'username') and entity.username:
                                message_link = f"https://t.me/{entity.username}/{message.id}"

                            data = {
                                "التاريخ": now,
                                "القناة/المجموعة": chat_name,
                                "رابط الرسالة": message_link if message_link else "لا يوجد",
                                "نص الرسالة": message.text[:500]
                            }

                            update_csv(data)
                            await send_alert(bot, chat_name, message_link or "بدون رابط", message.text[:300], now)
                            print(f"[OLD] مسابقة قديمة مكتشفة في {chat_name}")
            except Exception as e:
                print(f"[!] خطأ أثناء قراءة {entity.id}: {e}")

@client.on(events.NewMessage)
async def handler(event):
    if event.is_group or event.is_channel:
        message_text = event.raw_text.lower()
        if any(word in message_text for word in ignore_words):
            return
        if any(word in message_text for word in keywords):
            chat = await event.get_chat()
            chat_name = getattr(chat, 'title', 'مجهول')
            now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            message_link = None
            if hasattr(chat, 'username') and chat.username:
                message_link = f"https://t.me/{chat.username}/{event.id}"

            data = {
                "التاريخ": now,
                "القناة/المجموعة": chat_name,
                "رابط الرسالة": message_link if message_link else "لا يوجد",
                "نص الرسالة": event.raw_text[:500]
            }

            update_csv(data)
            await send_alert(bot, chat_name, message_link or "بدون رابط", event.raw_text[:300], now)
            print(f"[NEW] مسابقة جديدة في {chat_name}")

# --------- إضافة سيرفر ويب ---------
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "The bot is running!"}

async def main():
    print(">> بدء تشغيل البوت...")
    await client.start()
    await fetch_old_messages(client, bot)
    await client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())

    # نأخذ المتغير PORT الذي تطلبه Render
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
