import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from koharu import GenerateImage

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="下头小春！")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if len(text) > 5:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="太长了！死刑！死刑！")
        return
    for char in text:
        await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=GenerateImage(char))

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    command_with_at = '/gen@KoharuSignBot'
    if text.startswith(command_with_at):
        text = text[len(command_with_at):].strip()
    else:
        text = update.message.text[4:].strip()
    if not text:
        return
    if len(text) > 5:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="太长了！死刑！死刑！")
        return
    for char in text:
        await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=GenerateImage(char))

if __name__ == '__main__':
    application = ApplicationBuilder().token('TOKEN').build()
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    gen_handler = CommandHandler('gen', gen)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(gen_handler)
    
    application.run_polling()