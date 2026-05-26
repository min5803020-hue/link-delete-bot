import telebot
from telebot import types
from flask import Flask
from threading import Thread
import time

# --- CONFIGURATION ---
# ch26erry ရဲ့ Bot Token ကို တန်းထည့်ပေးထားပါတယ်ဗျာ
TELEGRAM_BOT_TOKEN = '8883099324:AAGWFQ-dP-U5sRCEZs9us97Aamp2N8PX-Zs'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "<b>LinkDeletedV1 Bot is Active on Render!</b>"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- HELPER FUNCTIONS ---
def is_admin(chat_id, user_id):
    """ ပို့တဲ့သူက Admin ဟုတ်မဟုတ် စစ်ဆေးသည် """
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except Exception as e:
        print(f"Error checking admin: {e}")
        return False

# --- BOT MESSAGE HANDLER ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'audio'])
def monitor_and_delete_links(message):
    # Admin ဆိုရင် ဘာမှမလုပ်ဘဲ ကျော်သွားမယ်
    if is_admin(message.chat.id, message.from_user.id):
        return

    text = message.text or message.caption
    has_link = False

    # 1. စာသားပါဝင်မှု ရှိပါက Link များနှင့် Username များကို စစ်ဆေးခြင်း
    if text:
        lower_text = text.lower()
        # ပုံမှန် Link ပုံစံများ
        if "http://" in lower_text or "https://" in lower_text or "www." in lower_text:
            has_link = True
        # Telegram Link များနှင့် အခြား Group/Channel ID များ
        elif "t.me/" in lower_text or "telegram.me/" in lower_text or "tg://join" in lower_text:
            has_link = True
        # @username များဖြင့် Promote လုပ်ခြင်းကို စစ်ဆေးခြင်း
        elif "@" in lower_text:
            # @ ပြီးရင် အနည်းဆုံး စာလုံး ၄ လုံးပါရင် Username အဖြစ် သတ်မှတ်ပြီး ဖျက်မယ်
            words = lower_text.split()
            for word in words:
                if word.startswith("@") and len(word) > 4:
                    has_link = True
                    break

    # 2. Telegram Entities (စာသားထဲမှာ ဝှက်ထားတဲ့ Hyperlinks သို့မဟုတ် URL) စစ်ဆေးခြင်း
    if message.entities:
        for entity in message.entities:
            if entity.type in ['url', 'text_link', 'mention']:
                has_link = True
                break
                
    # 3. Caption Entities (ပုံတွေ၊ ဗီဒီယိုတွေအောက်က စာသားထဲက Link) စစ်ဆေးခြင်း
    if message.caption_entities:
        for entity in message.caption_entities:
            if entity.type in ['url', 'text_link', 'mention']:
                has_link = True
                break

    # 4. Inline Keyboard Buttons ထဲမှာ Link (URL) ထည့်ထားခြင်း ရှိမရှိ စစ်ဆေးခြင်း (Spam Bot အများစု သုံးတတ်သည်)
    if message.reply_markup and message.reply_markup.inline_keyboard:
        for row in message.reply_markup.inline_keyboard:
            for button in row:
                if button.url:  # Button မှာ Link ချိတ်ထားရင် ဖျက်မယ်
                    has_link = True
                    break

    # Link တွေ့ရှိပါက ဖျက်ဆီးခြင်း
    if has_link:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            
            # User ကို သတိပေးစာ ပို့ရန်
            user_name = message.from_user.first_name or "User"
            warn_msg = bot.send_message(
                message.chat.id, 
                f"<b>⚠️ {user_name}! Link/Username များ မျှဝေခွင့် မရှိပါဗျာ။</b>", 
                parse_mode='HTML'
            )
            
            # သတိပေးစာကို ၃ စက္ကန့်အကြာတွင် အလိုအလျောက် ပြန်ဖျက်ရန်
            def auto_delete_warn():
                time.sleep(3)
                try:
                    bot.delete_message(message.chat.id, warn_msg.message_id)
                except Exception as e:
                    print(f"Failed to delete warning: {e}")
            
            Thread(target=auto_delete_warn).start()
            
        except Exception as e:
            print(f"Error in deleting message: {e}")

if __name__ == "__main__":
    keep_alive()
    print("LinkDeletedV1 Bot is starting on Render...")
    bot.infinity_polling()
