import requests

url = "http://127.0.0.1:8000/api/chatbot/message/"
data = {"message": "add item to cart"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)
print("Status Code:", response.status_code)
try:
    print("Response JSON:", response.json())
except Exception:
    print("Response Text:", response.text)
