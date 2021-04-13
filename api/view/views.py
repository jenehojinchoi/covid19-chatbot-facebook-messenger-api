# def ping(*args, **kwargs):
#     return 'pong'

def check_verify_token(services, facebook_credentials):
   if not services.message_service.check_verify_token(
       request.args.get('hub.verify_token'),
       facebook_credentials['VERIFY_TOKEN']
   ):
       raise Exception("INVALID_VERIFY_TOKEN")
   return request.args.get('hub.challenge')

def facebook_message(services, facebook_credentials, SERVICE_KEY):  
   try:
       payload     = request.json
       message     = payload['entry'][0]['messaging'][0]['message']['text']
       facebook_id = payload['entry'][0]['messaging'][0]['sender']['id']

       sender_id   = services.user_service.save_user(facebook_id)

       data          = services.message_service.get_covid_data(SERVICE_KEY)      
       current_state = services.message_service.get_current_state(sender_id)
       next_state    = services.message_service.get_next_state(data, sender_id, current_state, message)
       message_id    = services.message_service.save_message(sender_id, message, current_state, next_state)
       bot           = Bot(facebook_credentials['PAGE_ACCESS_TOKEN'])

       if next_state in ['CASES_OR_POLICY', 'COUNTRY_OR_CITY', 'CHOOSE_CITIES', 'CHOOSE_MORE_CITIES', \
           'COUNTRY_CASES', 'CITY_CASES', 'REQUEST_ERROR', 'LEAVE', 'INITIAL']:
           processed_reply = getattr(services.message_service, f'{next_state.lower()}_reply')(data, message)
           services.message_service.save_reply(message_id, processed_reply['text'])
           bot.send_message(facebook_id, processed_reply)
           
           if next_state == 'REQUEST_ERROR' and current_state in ['CASES_OR_POLICY', 'COUNTRY_OR_CITY', 'CHOOSE_CITIES', 'CHOOSE_MORE_CITIES']:
               processed_reply = getattr(services.message_service, f'{current_state.lower()}_reply')(data, message)
               bot.send_message(facebook_id, processed_reply)
       
           elif next_state == 'REQUEST_ERROR' and current_state in ['REQUEST_ERROR']:
               processed_reply = services.message_service.initial_reply(data, message)
               services.message_service.save_reply(message_id, processed_reply['text'])
               bot.send_message(facebook_id, processed_reply)

       elif next_state == 'POLICY':
           processed_reply = getattr(services.message_service, f'{next_state.lower()}_reply')(data, message)
           services.message_service.save_reply(message_id, processed_reply['text'])
           bot.send_message(facebook_id, processed_reply['template'])

       if (next_state in ['COUNTRY_CASES', 'POLICY', 'CITY_CASES']) or (next_state == 'REQUEST_ERROR' and current_state in ['COUNTRY_CASES', 'POLICY', 'CITY_CASES']):
           automatic_reply = services.message_service.process_automatic_reply()
           bot.send_message(facebook_id, automatic_reply)

       return make_response(jsonify(message='SUCCESS', reply=processed_reply), 200)
   
   except Exception as e:
       return make_response(jsonify(message=f'FAILED, {e}'), 500)
