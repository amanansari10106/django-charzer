import requests
import json
# url = "http://127.0.0.1:8000/customer/ChargerDetail/"
url = "http://127.0.0.1:8000/host/testz/"

# data = {
#     'deviceid':'1'
# }
# json_data ='{"name":"string-value","type":"str-value","deviceid":"3","roomid":"2","perunit":"2"}'

json_data ='{"charger_id":"24324","host_id":"2334","token":"323"}'

data = {
    'charger_id':'4',
    "host_id":"2323",
    "token":"34324"
}

json_data = json.dumps(data)
r = requests.get(url = url, data=json_data)
# print("######################")
# r = requests.get(url = url, data=json_data)

print(r)
data = r.json()
print(data)