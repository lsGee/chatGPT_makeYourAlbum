import openai
import urllib.request
import os
import config

openai.api_key = config.SECRETE_KEYS['OPENAI']
IMG_LOCATION = config.IMG_LOCATION

def get_image_url(text:str):
    '''text to image'''
    response = openai.Image.create(
        prompt = text,
        n=1,
        # size='256x256'
        size='512x512'
    )
    image_url = response['data'][0]['url']
    
    return image_url

def save_image(chat_id:str, url:str):
    global IMG_LOCATION
    if str(chat_id) not in os.listdir(IMG_LOCATION):
        os.makedirs(IMG_LOCATION+'/'+str(chat_id))
    file_list = os.listdir(IMG_LOCATION+'/'+str(chat_id))
    img_path = f'{IMG_LOCATION}/{chat_id}/img_{len(file_list)}.png'
    urllib.request.urlretrieve(url, img_path)
    print('Image is downloaded at:', img_path)
    
    return img_path