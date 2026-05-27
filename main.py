import os
import telebot
from flask import Flask
from threading import Thread

# Bot Token ကို Render ရဲ့ Environment Variable ထဲမှာ ထည့်ရမှာဖြစ်လို့ ဒါကို မပြင်ပါနဲ့
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is awake!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(func=lambda message: True)
def delete_links(message):
    # Link ပါတဲ့ စာသားတွေကို စစ်ပြီး ဖျက်ပေးမယ့်အပိုင်း
    if 'http' in message.text or 't.me' in message.text:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    keep_alive()
    print("Bot is running...")
    bot.infinity_polling()
