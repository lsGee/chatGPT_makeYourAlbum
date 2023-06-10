import openai
import pandas as pd
import config

openai.api_key = config.SECRETE_KEYS['OPENAI']

def get_lyric(topic:str, 
              content_include=None, 
              content_except=None, 
              lang=None, 
              genre=None, 
              **kwargs):
    '''
    주어진 설정에 맞는 노래 가사 생성
    '''
    genre = '' if genre == None else genre + ' '
    request = '- 주제:' + topic
    
    if content_include != None:
        request = request + '\n- 포함할 내용:' + content_include
    if content_except != None:
        request = request + '\n- 제외할 단어:' + content_except
    if lang != None:
        lang = request + '\n- 언어:' + lang
        
    cover_concept = topic
    # 역할 설정 및 질문 작성
    messages = [
        {'role': 'system', 
            'content': '노래 가사 생성기'},
        {'role': 'user', 
            'content': f'아래 설정으로 {genre}노래 가사 만들어줘.\n{request}'}
    ]
    
    # 가사 생성
    result = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            max_tokens=800,
            n=1
        ).choices[0].message.content
        
    return result


def get_cover_concept(topic:str):
    '''
    주어진 주제에 맞는 앨범 커버 이미지 컨셉 생성
    '''
    messages = [
        {'role': 'system', 
            'content': 'DALL-E가 이해할 수 있는 설명글을 대화식 말투 없이 100자 이내로 출력하는 기계'},
        {'role': 'user', 
            'content': f'다음 내용과 어울리는 장면을 창의적이고 구체적으로 상상해서, DALL-E 2가 이해할 수 있는 100자 이내의 영어로 묘사해줘.: {topic}'}
    ]
    
    # 가사 생성
    result = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            max_tokens=200,
            # n=3
            n=1
        ).choices
    cover_concept_list = list(map(lambda x: x.message.content + ', Digital Art', result))
        
    return cover_concept_list