import requests
import json


def SendSMS(part_url, payload):
    url = "http://2factor.in/API/V1/8f1dd888-03a5-11ea-9fa5-0200cd936042/"+part_url
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=payload, headers=headers)
    print(response.text)
    return json.loads(response.text)


def SubscriptionSMS(to, name, payment, subscription):
    try:
        url = "ADDON_SERVICES/SEND/TSMS"
        payload = {
            'From': 'FESTEV',
            'To': to,
            'Msg': 'Thank you '+name+' for subscribing with us. We have received your payment '+payment+' for '+subscription+' subscription'
        }
        return SendSMS(url, payload)
    except:
        return None


def TicketSMS(to, name, ticket, payment, event):
    try:
        url = "ADDON_SERVICES/SEND/TSMS"
        payload = {
            'From': 'FESTEV',
            'To': to,
            'Msg': 'Thank you '+name+', Your ticket number is '+ticket+' @ '+event+' for '+payment
        }
        return SendSMS(url, payload)
    except:
        return None


def ReferanceSMS(to, name, discount, brand, shop, refid):
    try:
        url = "ADDON_SERVICES/SEND/TSMS"
        payload = {
            'From': 'FESTEV',
            'To': to,
            'Msg': 'Thank you '+name+', Your booking for offer '+discount+' on '+brand+' at the '+shop+' is successful your ref id is '+refid
        }
        return SendSMS(url, payload)
    except:
        return None


def PushSMS(to):
    print('to', to)
    try:
        url = "ADDON_SERVICES/SEND/TSMS"
        payload = {
            'From': 'FESTEV',
            'To': to,
            'Msg': f'Thank you {to}'
        }
        print(payload)
        return SendSMS(url, payload)
    except:
        return None

# print(PushSMS('9594533197','Abhishek','150','Yearly'))
# print(TicketSMS('9594533197','Abhishek','10000101','150','Yearly'))
