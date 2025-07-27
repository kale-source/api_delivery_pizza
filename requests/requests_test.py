import requests

headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiZXhwIjoxNzU0MjYwNjg0fQ.JG9vQzl39AN4yGGrjNuO3McXuzY0cDpKrUu-TxeVQ1M'
}

request = requests.get('http://127.0.0.1:8000/auth/refresh', headers=headers)

print(request)
print(request.json())

