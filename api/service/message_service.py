from flask  import jsonify, make_response

import requests
import json

class Bot:
    def __init__(self, access_token, **kwargs):
        self.graph_url = 'https://graph.facebook.com/v10.0'
        self.access_token = access_token
    
    @property
    def auth_args(self):
        if not hasattr(self, '_auth_args'):
            auth = {
                'access_token': self.access_token
            }
            self._auth_args = auth
        return self._auth_args

    def send_message(self, recipient_id, processed_reply):
        payload = {
            'message': processed_reply,
            'recipient': {
                'id' : recipient_id
            }
        }
        request_endpoint = '{0}/me/messages'.format(self.graph_url)
        response = requests.post(
            request_endpoint,
            params=self.auth_args,
            json=payload
        )
        return response.json()
        
class MessageService:
    def __init__(self, message_dao, redis):	
        self.message_dao = message_dao
        self.redis = redis
    
    def check_verify_token(self, token_sent, VERIFY_TOKEN):
        return token_sent == VERIFY_TOKEN

    def get_covid_data(self, SERVICE_KEY):
        data = self.redis.get('data')
        if not data:
            req  = requests.get(f'https://api.corona-19.kr/korea/country/new/?serviceKey={SERVICE_KEY}', timeout='')
            self.redis.set('data', req.content)
            return data
        return json.loads(data)

    def get_next_state(self, data, sender_id, state, message):
        if state == 'INITIAL':
            return 'CASES_OR_POLICY'
        elif state == 'CASES_OR_POLICY' and '일일 확진자수 확인' == message:
            return 'COUNTRY_OR_CITY'
        elif state == 'CASES_OR_POLICY' and '사회적 거리두기 현황 확인' == message:
            return 'POLICY'  
        elif state == 'COUNTRY_OR_CITY' and '전국' == message:
            return 'COUNTRY_CASES'
        elif state == 'COUNTRY_OR_CITY' and '지역별' == message:
            return 'CHOOSE_CITIES'
        elif state == 'CHOOSE_CITIES':
            if '다른 지역도 확인할래' in message: 
                return 'CHOOSE_MORE_CITIES' 
            cities = [data[city]['countryName'] for city in list(data.keys())[3:12]]
            return 'REQUEST_ERROR' if message not in [data[city]['countryName'] for city in list(data.keys())[3:12]] else 'CITY_CASES'
        elif state == 'CHOOSE_MORE_CITIES':
            cities = [data[city]['countryName'] for city in list(data.keys())[13:20]]
            return 'REQUEST_ERROR' if message not in [data[city]['countryName'] for city in list(data.keys())[13:20]] else 'CITY_CASES'
        elif state in ['COUNTRY_CASES', 'POLICY', 'CITY_CASES'] and '아니, 없어' in message:
            return 'INITIAL'
        elif state in ['COUNTRY_CASES', 'POLICY', 'CITY_CASES'] and '처음으로 돌아갈래' in message:
            return 'CASES_OR_POLICY'
        elif state == 'REQUEST_ERROR':
            previous_state =  self.message_dao.get_previous_state(sender_id)
            if previous_state == 'REQUEST_ERROR':
                return 'INITIAL'  
            return self.get_next_state(data, sender_id, previous_state, message)        
        else:
            return 'REQUEST_ERROR'
            
    def get_current_state(self, sender_id):
        return self.message_dao.get_state(sender_id)

    def save_message(self, sender_id, message, current_state, next_state):
        return self.message_dao.create_message(sender_id, message, current_state, next_state)

    def cases_or_policy_reply(self, data, message):
        template = {
            'text': '안녕하세요! 코로나 알리미 봇입니다. \n무엇을 도와드릴까요?',
            'quick_replies' : [
            {
                "content_type":"text",
                "title":"일일 확진자수 확인",
                "payload":"<POSTBACK_PAYLOAD>",
            },{
                "content_type":"text",
                "title":"사회적 거리두기 현황 확인",
                "payload":"<POSTBACK_PAYLOAD>",
            }]
        }
        return template

    def country_or_city_reply(self, data, message):
        template = {
            'text': '전국의 일일 확진자수를 보시겠어요? 아니면 지역별로 보시겠어요?',
            'quick_replies' : [
            {
                "content_type":"text",
                "title":"전국",
                "payload":"<POSTBACK_PAYLOAD>",
            },{
                "content_type":"text",
                "title":"지역별",
                "payload":"<POSTBACK_PAYLOAD>",
            }]
        }
        return template
    
    def country_cases_reply(self, data, message):
        return {'text' : '오늘 하루 전국 확진자수는 ' + data['korea']['newCase'] + '명입니다. \n국내 발생은 ' + \
             data['korea']['newCcase'] + '명, 해외 발생은 ' + data['korea']['newFcase'] + '명입니다.'}

    def choose_cities_reply(self, data, message):
        cities = list(data.keys())[3:12]
        template = {
            'text': '지역을 골라주세요.',
            'quick_replies' : [
            {
                "content_type":"text",
                "title": data[city]['countryName'],
                "payload":"<POSTBACK_PAYLOAD>",
            } for city in cities]
        }
        template['quick_replies'].append(
            {
                "content_type":"text",
                "title": '다른 지역도 확인할래',
                "payload":"<POSTBACK_PAYLOAD>",
            }
        )
        return template
    
    def choose_more_cities_reply(self, data, message):
        cities = list(data.keys())[13:20]
        template = {
            'text': '원하는 지역이 없으셨군요! 그러면 아래의 목록에서 다른 지역을 골라주세요.',
            'quick_replies' : [
            {
                "content_type":"text",
                "title": data[city]['countryName'],
                "payload":"<POSTBACK_PAYLOAD>",
            } for city in cities]
        }
        return template
    
    def city_cases_reply(self, data, message):
        korean_english_cities = {data[city]['countryName']: city for city in list(data.keys())[3:20]}
        if message in korean_english_cities.keys():
            city = korean_english_cities[message]
            return {'text' : '오늘 ' + data[city]['countryName'] + '에서의 하루 확진자수는 ' + data[city]['newCase'] +\
                '명입니다. \n국내 발생은 ' +  data[city]['newCcase'] + '명, 해외 발생은 ' + data[city]['newFcase'] + '명입니다.'}

    def policy_reply(self, data, message):
        text = '사회적 거리두기 단계가 궁금하시다면 아래의 질병 관리청 웹사이트를 확인해주세요!'
        buttons = [
            {
                "type":"web_url",
                "url":'http://ncov.mohw.go.kr/duBoardList.do?brdId=2&brdGubun=29',
                "title":"질병 관리청 웹사이트 확인하기"
            }
        ]
        template = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": text,
                    "buttons": buttons
                }
            }
        }
        return {'text' : text, 'template' : template}

    def request_error_reply(self, data, message):
        return {'text' : '잘 못 알아들었어요. 다시 한번 말씀해주시겠어요?'}

    def initial_reply(self, data, message):
        return {'text' : '국내 코로나 바이러스 상황에 대해서 궁금한 점이 있으시다면 언제든지 저를 찾아와주세요!'}
    
    def process_automatic_reply(self):
        template = {
            'text': '혹시 더 도와드릴 것이 있나요?',
            'quick_replies' : [
            {
                "content_type":"text",
                "title":"아니, 없어",
                "payload":"<POSTBACK_PAYLOAD>",
            },{
                "content_type":"text",
                "title":"처음으로 돌아갈래",
                "payload":"<POSTBACK_PAYLOAD>",
            }]
        }
        return template
           
    def save_reply(self, message_id, reply):
        return self.message_dao.create_reply(message_id, reply) 
