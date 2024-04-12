import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultCachedSticker
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, InlineQueryHandler
import json
from uuid import uuid4

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class MessageMapInstance:
    def __init__(self, short, type, message, index):
        self.short = short
        self.type = type
        self.message = message
        self.index = index
    

class MessageMap:
    def __init__(self):
        with open('data.json', 'r') as f:
            data = json.load(f)
            self.data: list[MessageMapInstance] = []
            for item in data['data']:
                self.data.append(MessageMapInstance(item['short'], item['type'], item['message'], item['index']))
            self.index: int = int(data['index'])
    
    def add_message(self, short, type, message):
        result = MessageMapInstance(short, type, message, self.index)
        self.data.append(result)
        self.index += 1
        with open('data.json', 'w') as f:
            data = [x.__dict__ for x in self.data]
            json.dump({'data': data, 'index': self.index}, f)
        return result.index
    
    def del_message(self, index):
        for i in range(len(self.data)):
            if self.data[i].index == index:
                self.data.pop(i)
                break
        with open('data.json', 'w') as f:
            data = [x.__dict__ for x in self.data]
            json.dump({'data': data, 'index': self.index}, f)
    
    def find_messages(self, short):
        result = []
        for i in range(len(self.data)):
            if short in self.data[i].short:
                result.append(self.data[i])
        return result

to_add_map = {}
msg_map = MessageMap()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="我是伟大菲尼克斯皇帝的卑微史官。\
若您需要，我会向您提供便捷的皇帝语录以供参考。")


async def set_inline_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = '/set_inline_message'
    text = update.message.text[len(command):].strip()
    if not text:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="请输入您要设置的内联消息！")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="收到！下面请您告诉我这句话和哪条史料相对！\
使用/empty来取消您的输入！")
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=context._user_id)
    to_add_map[context._user_id] = text


async def del_inline_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = '/set_inline_message'
    text = update.message.text[len(command):].strip()
    try:
        index = int(text)
    except:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="请输入正确的史料索引！")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="收到！真理部即将出动删除此条消息！")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=index)


async def empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="已取消！")
    if context._user_id in to_add_map:
        del to_add_map[context._user_id]


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context._user_id not in to_add_map:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="请先设置需要添加的内联消息！")
        return
    text = update.message.text
    sticker = update.message.sticker
    if not text and not sticker:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="请输入文本或使用Sticker！")
        return
    idx = None
    if text:
        idx = msg_map.add_message(to_add_map[context._user_id], 'text', text)
    else:
        idx = msg_map.add_message(to_add_map[context._user_id], 'sticker', sticker.file_id)
    if idx is not None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"添加成功！记住您的史料索引：{idx}！\
如需删除史料请使用这个索引！")
        del to_add_map[context._user_id]
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="添加失败！请联系管理员！")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query

    if not query:  # empty query should not be handled
        return
    
    results = []
    map_result = msg_map.find_messages(query)
    for result in map_result:
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
    empty_handler = CommandHandler('empty', empty)
    set_handler = CommandHandler('set_inline_message', set_inline_message)
    del_handler = CommandHandler('del_inline_message', del_inline_message)
    
    msg_handler = MessageHandler((~filters.COMMAND) & filters.ChatType.PRIVATE, on_message)
    
    application.add_handler(start_handler)
    application.add_handler(empty_handler)
    application.add_handler(set_handler)
    application.add_handler(del_handler)
    
    application.add_handler(msg_handler)
    
    application.add_handler(InlineQueryHandler(inline_query))
    
    application.run_polling()