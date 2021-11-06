import pytest
import flask
import requests

url = 'http://127.0.0.1:5000/login'
userdata = {'username': "admin", 'password': "pass"}
x = requests.post(url, data = userdata)


if(x.text == "1"):
    print("Success")
else:
    print("Failure")

print(x.text)

