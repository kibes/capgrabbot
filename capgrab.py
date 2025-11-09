import logging
import random
import json
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from dotenv import load_dotenv

# Отключаем логирование внешних библиотек
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
YOUR_CHAT_ID = '977902779'
RESPONSES_FILE = "responses.json"

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    raise ValueError("BOT_TOKEN не найден в .env файле")

if not YOUR_CHAT_ID or YOUR_CHAT_ID == "YOUR_CHAT_ID_HERE":
    raise ValueError("CHAT_ID не найден в .env файле")

CREATOR_ID = YOUR_CHAT_ID

# Минимальная настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)

def load_responses():
    try:
        if not os.path.exists(RESPONSES_FILE):
            return None
            
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
            responses = json.load(f)
            return responses
            
    except Exception:
        return None

async def get_user_info(bot, user_id):
    try:
        chat = await bot.get_chat(user_id)
        username = f"@{chat.username}" if chat.username else "нет username"
        name = chat.first_name or ""
        if chat.last_name:
            name += f" {chat.last_name}"
        return f"{name} ({username})" if name else username
    except Exception:
        return "неизвестный пользователь"

async def thank_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    
    if user_id != CREATOR_ID:
        await update.message.reply_text("Неизвестная команда")
        return
    
    if not context.args:
        await update.message.reply_text("Использование: /thank user_id [сообщение]")
        return
    
    target_user_id = context.args[0]
    
    custom_message = " ".join(context.args[1:]) if len(context.args) > 1 else ""
    
    thank_you_message = "❤️ создатель бота поблагодарил вас за отправленный код"
    
    if custom_message:
        thank_you_message += f"\n<blockquote>{custom_message}</blockquote>"
    
    try:
        target_chat_id = int(target_user_id)
        
        await context.bot.send_message(
            chat_id=target_chat_id,
            text=thank_you_message,
            parse_mode='HTML'
        )
        
        user_info = await get_user_info(context.bot, target_chat_id)
        await update.message.reply_text(f"✅ Благодарность отправлена {user_info}")
        
    except ValueError:
        await update.message.reply_text("❌ user_id должен быть числом")
    except Exception as e:
        try:
            target_chat_id = int(target_user_id)
            user_info = await get_user_info(context.bot, target_chat_id)
        except:
            user_info = f"ID {target_user_id}"
            
        error_message = f"❌ Не удалось отправить сообщение {user_info}"
        if "chat not found" in str(e).lower():
            error_message += "\nБот не может написать этому пользователю."
        
        await update.message.reply_text(error_message)

async def msg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    
    if user_id != CREATOR_ID:
        await update.message.reply_text("Неизвестная команда")
        return
    
    if not context.args:
        await update.message.reply_text("Использование: /msg user_id [сообщение]")
        return
    
    target_user_id = context.args[0]
    
    custom_message = " ".join(context.args[1:]) if len(context.args) > 1 else ""
    
    if not custom_message:
        await update.message.reply_text("❌ Необходимо указать сообщение")
        return
    
    msg_text = "❗️ создатель бота написал вам сообщение"
    msg_text += f"\n<blockquote>{custom_message}</blockquote>"
    
    try:
        target_chat_id = int(target_user_id)
        
        await context.bot.send_message(
            chat_id=target_chat_id,
            text=msg_text,
            parse_mode='HTML'
        )
        
        user_info = await get_user_info(context.bot, target_chat_id)
        await update.message.reply_text(f"✅ Сообщение отправлено {user_info}")
        
    except ValueError:
        await update.message.reply_text("❌ user_id должен быть числом")
    except Exception as e:
        try:
            target_chat_id = int(target_user_id)
            user_info = await get_user_info(context.bot, target_chat_id)
        except:
            user_info = f"ID {target_user_id}"
            
        error_message = f"❌ Не удалось отправить сообщение {user_info}"
        if "chat not found" in str(e).lower():
            error_message += "\nБот не может написать этому пользователю."
        
        await update.message.reply_text(error_message)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    responses_data = context.bot_data.get('responses', {})
    welcome_message = responses_data.get('welcome_message', 'Добро пожаловать!')
    await update.message.reply_text(welcome_message)

async def send_random_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    responses_data = context.bot_data.get('responses', {})
    random_responses = responses_data.get('random_responses', [])
    
    if random_responses:
        random_response = random.choice(random_responses)
        await update.message.reply_text(random_response)
    else:
        await update.message.reply_text("Спасибо!")

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message
        if not message:
            return

        user = message.from_user
        chat = message.chat
        
        info_text = "📩 Новое сообщение от:\n"
        info_text += f"👤 {user.first_name}"
        if user.last_name:
            info_text += f" {user.last_name}"
        info_text += f" (@{user.username})" if user.username else ""
        info_text += f"\n🆔 User ID: {user.id}"
        
        if chat.type != "private":
            info_text += f"\n💬 Чат: {chat.title} (ID: {chat.id})"
        else:
            info_text += f"\n💬 Личный чат"

        try:
            await message.forward(
                chat_id=YOUR_CHAT_ID,
                caption=info_text
            )
        except Exception:
            await context.bot.send_message(
                chat_id=YOUR_CHAT_ID,
                text=info_text
            )
            await message.forward(chat_id=YOUR_CHAT_ID)

        if not message.text or not message.text.startswith('/'):
            await send_random_response(update, context)

    except Exception:
        pass

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

def main():
    responses_data = load_responses()
    
    if responses_data is None:
        responses_data = {}
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.bot_data['responses'] = responses_data
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("thank", thank_command))
    application.add_handler(CommandHandler("msg", msg_command))
    
    application.add_handler(MessageHandler(filters.ALL, handle_all_messages))
    
    application.add_error_handler(error_handler)
    
    print("🤖 Бот-пересыльщик запущен...")
    print("📩 Бот будет пересылать все сообщения")
    print("💝 Команда /thank user_id [сообщение] - отправить благодарность")
    print("💬 Команда /msg user_id сообщение - отправить сообщение")
    
    if responses_data:
        response_count = len(responses_data.get('random_responses', []))
        print(f"🎲 Загружено {response_count} ответов из JSON")
    else:
        print("❌ Файл responses.json не загружен")
    
    application.run_polling()

if __name__ == "__main__":
    main()
