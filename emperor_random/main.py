import logging
from telegram import Update, MessageOriginUser, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultCachedSticker
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, InlineQueryHandler
import json
import random
from uuid import uuid4

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class MessageInstance:
    def __init__(self, type, message):
        self.type = type
        self.message = message
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, MessageInstance):
            return False
        return self.type == value.type and self.message == value.message
    

class MessageList:
    def __init__(self):
        with open('data.json', 'r') as f:
            data = json.load(f)
            self.data: list[MessageInstance] = []
            for item in data:
                self.data.append(MessageInstance(item['type'], item['message']))
    
    def add_message(self, messageI):
        self.data.append(messageI)
        with open('data.json', 'w') as f:
            data = [x.__dict__ for x in self.data]
            json.dump(data, f)
    
    def find_messages(self, messageI):
        for i in self.data:
            if messageI == i:
                return True
        return False
    
    def find_messages_with(self, text):
        result = []
        for i in self.data:
            if text in i.message:
                result.append(i)
        return result

    def get_random(self, num=1):
        result = random.sample(self.data, num)
        if num == 1:
            return result[0]
        return result

msg_list = MessageList()
emperor_id = 'YOUR_EMPEROR'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="随机皇帝语录！")

async def send_message(bot, chat_id, messageI):
    match messageI.type:
        case 'text':
            await bot.send_message(chat_id=chat_id, text=messageI.message)
            

async def on_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=msg.forward_origin)
    if msg.forward_origin and isinstance(msg.forward_origin, MessageOriginUser):
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=msg.forward_origin.sender_user.id)
        if msg.forward_origin.sender_user.id == emperor_id:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="是皇帝！")
            text = msg.text
            if not text:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="目前只支持文字消息！")
                return
            messageI = MessageInstance('text', text)
            if msg_list.find_messages(messageI):
                await context.bot.send_message(chat_id=update.effective_chat.id, text="该语录已被记录过！")
            else:
                msg_list.add_message(messageI)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="已记录皇帝新语录！")
            return
    random_chat = msg_list.get_random()
    await send_message(context.bot, update.effective_chat.id, random_chat)

async def on_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    random_number = random.randint(0, 99)
    if random_number < 5:
        random_chat = msg_list.get_random()
        await send_message(context.bot, update.effective_chat.id, random_chat)

async def on_channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if msg.forward_origin and isinstance(msg.forward_origin, MessageOriginUser):
        if msg.forward_origin.sender_user.id == emperor_id:
            text = msg.text
            if not text:
                return
            messageI = MessageInstance('text', text)
            if not msg_list.find_messages(messageI):
                msg_list.add_message(messageI)

async def random_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    random_chat = msg_list.get_random()
    await send_message(context.bot, update.effective_chat.id, random_chat)

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""    
    query_text = update.inline_query.query
    
    results = []
    if query_text:
        msg_result = msg_list.find_messages_with(query_text)
        if not msg_result:
            msg_result = msg_list.get_random(10)
        if len(msg_result) > 10:
            msg_result = random.sample(msg_result, 10)
    else:
        msg_result = msg_list.get_random(10)
    for result in msg_result:
        if result.type == 'text':
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=f"皇帝语录：{result.message}",
                    input_message_content=InputTextMessageContent(result.message),
                ) 
            )
        else:
            results.append(
                InlineQueryResultCachedSticker(
                    id=str(uuid4()),
                    sticker_file_id=result.message
                )
            )

    await update.inline_query.answer(results)

if __name__ == '__main__':
    application = ApplicationBuilder().token('TOKEN').build()
    
    start_handler = CommandHandler('start', start)
    random_handler = CommandHandler('random', random_message)
    
    # message_handler = MessageHandler(filters.TextFilter('/empty'), del_inline_message)
    private_msg_handler = MessageHandler((~filters.COMMAND) & filters.ChatType.PRIVATE, on_private_message)
    group_msg_handler = MessageHandler((~filters.COMMAND) & filters.ChatType.GROUPS, on_group_message)
    channel_msg_handler = MessageHandler((~filters.COMMAND) & filters.ChatType.CHANNEL, on_channel_message)
    
    inline_query_handler = InlineQueryHandler(inline_query)
    
    application.add_handler(start_handler)
    application.add_handler(random_handler)
    
    application.add_handler(private_msg_handler)
    application.add_handler(group_msg_handler)
    application.add_handler(channel_msg_handler)
    
    application.add_handler(inline_query_handler)
    application.run_polling()