from requests.auth import HTTPBasicAuth
import requests


token = requests.get('http://localhost:5000/login', auth=('leandro', '12345'))

print(token.json())


requisicao = requests.get('http://localhost:5000/autores', headers={'x-access-token': token.json()['token']})

print(requisicao.json())