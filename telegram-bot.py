import os
import config, script
import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
# import asyncio
import pandas as pd
import json
import lyricMaker as lm
import imgMaker as im

COMMAND_STATUS = dict()
CONTENT = dict()

btn1 = telegram.InlineKeyboardButton(text='커버 만들기', callback_data='getcover')
btn1_1 = telegram.InlineKeyboardButton(text='커버 다시 만들기', callback_data='getcover_remake')
btn2 = telegram.InlineKeyboardButton(text='가사 다시 만들기', callback_data='newtopic')
markup1 = telegram.InlineKeyboardMarkup(inline_keyboard=[[btn1, btn2]])
markup2 = telegram.InlineKeyboardMarkup(inline_keyboard=[[btn1_1, btn2]])

def start(update, context):
    '''Send a greeting message'''
    global COMMAND_STATUS, CONTENT
    chat_id = update.message.chat_id
    
    COMMAND_STATUS[chat_id] = 'start'
    context.bot.send_message(chat_id=chat_id, text=script.intro)
    
def newtopic(update, context):
    '''Initailize and get a new topic'''
    global COMMAND_STATUS, CONTENT
    chat_id = update.message.chat_id
    
    COMMAND_STATUS[chat_id] = 'newtopic'
    if chat_id in CONTENT.keys():
        CONTENT.pop(chat_id)
    context.bot.send_message(chat_id=chat_id, text=script.new_topic)

def getcover(update, context):
    '''Create an album cover'''
    global COMMAND_STATUS, CONTENT
    callback_data = update.callback_query.data
    chat_id = update.callback_query.message.chat.id
    
    if chat_id not in COMMAND_STATUS.keys():
            context.bot.send_message(chat_id=chat_id, text=script.invalid_status)
    elif COMMAND_STATUS[chat_id] in ['lyric_created']:
        if callback_data == 'getcover':  # 앨범 커버 생성 버튼 클릭 시
            context.bot.send_message(chat_id=chat_id, text=script.creating_cover)
            
            cover_concept_list = lm.get_cover_concept(CONTENT[chat_id]['topic'])
            CONTENT[chat_id]['cover_concept'] = cover_concept_list
            # 이미지 저장
            image_url = im.get_image_url(cover_concept_list[0])
            print('Image is created at:', image_url)
            # 질문과 이미지 저장
            img_path = im.save_image(chat_id, image_url)
            CONTENT[chat_id]['cover_path'] = img_path
            # 저장된 이미지를 사용자에게 전송
            bot.send_photo(chat_id=chat_id, photo=open(img_path, 'rb'))
            # 결과물 최종 저장
            logs['data'].append(CONTENT[chat_id])
            with open(config.LOG_LOCATION+'/logs.json', 'w') as outfile:
                json.dump(logs, outfile, ensure_ascii=False)
            
            COMMAND_STATUS[chat_id] = 'cover_created'
            context.bot.send_message(chat_id=chat_id, text=script.feedback)
        elif callback_data == 'newtopic':  # 가사 다시 생성 버튼 클릭 시
            COMMAND_STATUS[chat_id] = 'newtopic'
            context.bot.send_message(chat_id=chat_id, text=script.new_topic)
        else:
            COMMAND_STATUS[chat_id] = ''
            context.bot.send_message(chat_id=chat_id, text=script.invalid_status)
            
    else:
        context.bot.send_message(chat_id=chat_id, text=script.invalid_status)

def handler(update, context):
    global COMMAND_STATUS, CONTENT, btn1, btn2, markup1
    
    # 사용자로부터 수신된 메시지
    user_text = update.message.text
    chat_id = update.message.chat_id
    username = update.message.chat.username
    
    if user_text != None:
        if chat_id not in COMMAND_STATUS.keys():
            context.bot.send_message(chat_id=chat_id, text=script.invalid_status)
        elif COMMAND_STATUS[chat_id] in ['start', 'newtopic']:
            CONTENT[chat_id] = dict()
            CONTENT[chat_id]['chat_id'] = chat_id
            CONTENT[chat_id]['username'] = username
            CONTENT[chat_id]['topic'] = user_text
            COMMAND_STATUS[chat_id] = 'topic_entered'
            context.bot.send_message(chat_id=chat_id, text=script.add_detail)
            
        elif COMMAND_STATUS[chat_id] == 'topic_entered':
            if user_text != '0':
                CONTENT[chat_id]['content_include'] = user_text
            COMMAND_STATUS[chat_id] = 'detail_entered'
            context.bot.send_message(chat_id=chat_id, text=script.add_except)
        
        elif COMMAND_STATUS[chat_id] == 'detail_entered':
            if user_text != '0':
                CONTENT[chat_id]['content_except'] = user_text
            COMMAND_STATUS[chat_id] = 'except_entered'
            # context.bot.send_message(chat_id=chat_id, text=script.add_genre)
            context.bot.send_message(chat_id=chat_id, text=script.add_lang)
                
        # elif COMMAND_STATUS[chat_id] == 'except_entered':
        #     if user_text != '0':
        #         CONTENT[chat_id]['genre'] = user_text
        #     COMMAND_STATUS[chat_id] = 'genre_entered'
        #     context.bot.send_message(chat_id=chat_id, text=script.add_lang)
            
        elif COMMAND_STATUS[chat_id] == 'except_entered':
            if user_text != '0':
                CONTENT[chat_id]['lang'] = user_text
            context.bot.send_message(chat_id=chat_id, text=script.creating_lyric)
            print(CONTENT[chat_id])
            
            # create lyric
            lyric = lm.get_lyric(**CONTENT[chat_id])
            context.bot.send_message(chat_id=chat_id, text=lyric)
            context.bot.send_message(chat_id=chat_id, text=script.continue_cover, reply_markup=markup1)
            CONTENT[chat_id]['lyric'] = lyric
            COMMAND_STATUS[chat_id] = 'lyric_created'
        
    else:
        print('No user text')


if __name__ == '__main__':
    # log 파일 로드
    if len(os.listdir(config.LOG_LOCATION)) == 0:
        logs = {'data': []}
    else:
        with open(config.LOG_LOCATION+'/logs.json', "r") as json_file:
            logs = json.load(json_file)
    
    bot = telegram.Bot(config.SECRETE_KEYS['BOT_TOKEN'])
    updater = Updater(config.SECRETE_KEYS['BOT_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher
    updater.start_polling()
    
    # create command
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('newtopic', newtopic))
    dispatcher.add_handler(CallbackQueryHandler(getcover))
    # reponse
    echo_handler = MessageHandler(Filters.text, handler)
    dispatcher.add_handler(echo_handler)
