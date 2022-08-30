import requests
import json
from requests import auth
from requests.auth import HTTPBasicAuth 


def payout(razorPayAccount, paymentKey,coinInRupee,upi,user , tranID, coin):
    payload = {
        "account_number": razorPayAccount.value,
        "amount":coinInRupee * 100,
        "currency":"INR",
        "mode":"UPI",
        "purpose":"refund",
        "fund_account":{
            "account_type":"vpa",
            "vpa":{
                "address":upi
            },
            "contact":{
                "name":user.name,
                "email": user.email,
                "contact":user.mobile,
                "type":"customer",
                "reference_id": str(user.id),
            }
        },
        "queue_if_low_balance":False,
        "reference_id":str(tranID),
        "narration":"FCoin redeem "+ str(coin),
    }
    url = "https://api.razorpay.com/v1/payouts"
    headers={'content-type': 'application/json',}
    params = json.dumps(payload).encode('utf8')
    response=requests.post(url, headers=headers, data=params, auth= HTTPBasicAuth(paymentKey.value,paymentKey.subvalue))
    
    return json.loads(response.text),response.status_code