import asyncio
import csv
import os
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from datetime import datetime, timedelta, timezone

# --------- إعدادات المستخدم ---------
api_id = 23398930          # << ضع هنا API ID الخاص بك
api_hash = 'bd3e85a7aae40566f2fa8804d200d6d0'  # << ضع هنا API HASH الخاص بك

session_string = "1BJWap1sBu1wuLC0UJm6sAOZMJMt4F7lFf37wp6Klen082u0dA3Vmn0U978Y3TjUu_dGWw5OctvHhYG8Wk3X-8EEXxnnjojVqMiYwie3AD462svUjaNdYxOV-tzsAhJ9nJuvCvUGO4RkHyBi6zmw6tI_eV9KsN8w_qi403gm-tRgOsSUQkUNWGv4UDeeLP4CWsobd4Z_JZq_wt-RsCbGmszGEWtkHodeiuT3LfVpMCAgRYpFhQgQK89q8wu1zNqx2e8xuDkUx5bn03jVl08EtBDwMVAog2BIsMZcSg1Q_JLJvZ0eHKlIFH6Q_wVMEI8y7o6tK1xg1jymZVNsKCyWVbJ8_a0I5PBg="  # << ضع هنا كود الجلسة
bot_token = '7972559567:AAGEjYo766OA-rOE4F5lqaJLdu5dff16ivA'  # << توكن البوت الخاص بك
your_channel_username = '@jeijehdojdo'  # << اسم قناتك مع @

csv_file = 'sweepstakes_log.csv'

# كلمات مفتاحية تدل على المسابقات
keywords = ["УЧАСТВОВАТЬ", "جائزة", "سحب", "شحن", "ربح", "contest", "giveaway", "randomgodbot"]

# كلمات يجب تجاهلها
ignore_words = ["fee", "Bid"]

# --------- وظائف مساعدة ---------

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

# --------- إعداد عملاء تيليجرام ---------
client = TelegramClient(StringSession(session_string), api_id, api_hash)
bot = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# --------- حدث قراءة الرسائل القديمة ---------

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

# --------- حدث فحص الرسائل الجديدة ---------

@client.on(events.NewMessage)
async def handler(event):
    if event.is_group or event.is_channel:
        message_text = event.raw_text.lower()

        if any(word in message_text for word in ignore_words):
            return

        if any(word in message_text for word in ["finished", "giveaway", "Победители", "Winners", "УЧАСТВОВАТЬ"]) and any(word in message_text for word in keywords):
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

# --------- أحداث البوت ---------

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    sweepstakes = read_sweepstakes()

    if not sweepstakes:
        await event.respond("❗ لا توجد مسابقات مكتشفة حاليًا.", buttons=[Button.inline("🔄 تحديث", b"refresh")])
        return

    text = "📋 **قائمة المسابقات المكتشفة:**\n\n"
    for idx, sweep in enumerate(sweepstakes, start=1):
        name = sweep['القناة/المجموعة']
        link = sweep['رابط الرسالة']
        time = sweep['التاريخ']
        if link != "لا يوجد":
            text += f"🔹 {idx}. [{name}]({link}) — `{time}`\n"
        else:
            text += f"🔹 {idx}. {name} — `{time}`\n"

    await event.respond(
        text,
        link_preview=False,
        buttons=[
            [Button.inline("🗑️ حذف جميع المكتشفات", b"delete_all")],
            [Button.inline("🔄 تحديث القائمة", b"refresh")]
        ]
    )

@bot.on(events.CallbackQuery(data=b'delete_all'))
async def delete_all_handler(event):
    if os.path.exists(csv_file):
        os.remove(csv_file)
        await event.edit("✅ تم حذف جميع المسابقات المكتشفة بنجاح.")
    else:
        await event.edit("❗ لا يوجد شيء لحذفه.")

@bot.on(events.CallbackQuery(data=b'refresh'))
async def refresh_handler(event):
    sweepstakes = read_sweepstakes()

    if not sweepstakes:
        await event.edit("❗ لا توجد مسابقات مكتشفة حاليًا.", buttons=[Button.inline("🔄 تحديث", b"refresh")])
        return

    text = "📋 **قائمة المسابقات المكتشفة:**\n\n"
    for idx, sweep in enumerate(sweepstakes, start=1):
        name = sweep['القناة/المجموعة']
        link = sweep['رابط الرسالة']
        time = sweep['التاريخ']
        if link != "لا يوجد":
            text += f"🔹 {idx}. [{name}]({link}) — `{time}`\n"
        else:
            text += f"🔹 {idx}. {name} — `{time}`\n"

    await event.edit(
        text,
        link_preview=False,
        buttons=[
            [Button.inline("🗑️ حذف جميع المكتشفات", b"delete_all")],
            [Button.inline("🔄 تحديث القائمة", b"refresh")]
        ]
    )

# --------- بدء التشغيل ---------

def main():
    print(">> بدء تشغيل البوت...")
    client.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_old_messages(client, bot))
    client.run_until_disconnected()

if __name__ == "__main__":
    main() 
