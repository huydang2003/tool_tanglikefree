import requests
from bs4 import BeautifulSoup
import json
import os
import random
from time import sleep, localtime
import re

class Tool_Tanglikefree():
	if not os.path.exists('data'): os.mkdir('data')
	if not os.path.exists('data/nicks'): os.mkdir('data/nicks')
	if not os.path.exists('data/today.txt'): open('data/today.txt', 'w').write(f'{localtime().tm_mday}{localtime().tm_mon}')
	if not os.path.exists('data/update.json'): open('data/update.json', 'w').write('{}')
	if not os.path.exists('list_nick.txt'): open('list_nick.txt', 'w', encoding='utf8').write("###Định dạng: username|password|cookie_xs")
	def __init__(self):
		self.ses = requests.session()
		self.list_nick = None

	def get_headers_tlf(self, access_token):
		headers_tlf = {
				'Host': 'tanglikefree.com',
				'Referer': 'https://tanglikefree.com/makemoney',
				'Sec-Fetch-Dest': 'empty',
				'Sec-Fetch-Mode': 'cors',
				'Sec-Fetch-Site': 'same-origin',
				'X-Requested-With': 'XMLHttpRequest',
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
				'Authorization': 'Bearer '+ access_token
			}
		return headers_tlf

	def get_headers_fb(self, cookie_fb):
		headers_fb = {
			'authority': 'mbasic.facebook.com',
			'upgrade-insecure-requests': '1',
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-mode': 'navigate',
			'accept-language': 'en-US,en;q=0.9',
			'user_agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36',
			'cookie': cookie_fb
		}
		return headers_fb

	def login_tlf(self, username, password):
		try:
			url = 'https://tanglikefree.com/api/auth/login'
			payload = {'username': username, 'password': password, 'disable': 'true'}
			res = self.ses.post(url, data = payload)
			data = res.json()
			if data['error'] == False:
				if self.list_config[username]==None:
					self.list_config[username] = {}
				self.list_config[username]['access_token'] = data['data']['access_token']
				access_token = self.list_config[username]['access_token']
				self.list_config[username]['info'] = self.get_info(access_token)	
				idfb = self.list_config[username]['info']['idfb']
				self.list_config[username]['cookie_fb'] = self.get_cookie_fb(username, idfb)
				cookie_fb = self.list_config[username]['cookie_fb']
				self.list_config[username]['token_fb'] = self.get_token_fb(cookie_fb)
				return True
			else: return False
		except: return False


if __name__ == '__main__':
	tool = Tool_Tanglikefree()