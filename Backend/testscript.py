import pytest
import flask
import requests

#This testscript can be used to test POST requests to the /login route
url = 'http://127.0.0.1:5000/login'
userdata = {'username': "asdf", 'password': "asdf"}
x = requests.post(url, json = userdata)

print(x.text)

x = requests.get('http://127.0.0.1:5000/users/asdf')
print(x.text)
