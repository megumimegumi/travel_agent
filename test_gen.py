import requests, json
payload = {
    'user_id': 'llll', 'destination': '南昌', 'origin': '上海',
    'start_date': '2026-04-05', 'days': 5, 'budget': 3000,
    'travelers_count': 1, 'pace': '适中'
}
res = requests.post('http://127.0.0.1:8000/api/plan/generate', json=payload)
print(json.dumps(res.json().get('special_tips', {}), ensure_ascii=False))
