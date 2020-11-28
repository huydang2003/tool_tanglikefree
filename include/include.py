import os
import requests
from bs4 import BeautifulSoup
import re
import json
from time import sleep, localtime

class fb_mt():
	def __init__(self):
		self.ses = requests.session()

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

	def get_token_fb(self, cookie_fb):
		headers = self.get_headers_fb(cookie_fb)
		url = 'https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed'
		res = self.ses.get(url, headers=headers)
		token = re.findall(r'accessToken\\":\\"(.*?)\\', res.text)
		if token != []: token = token[0]
		else: token = ''
		return token

	def get_cookie_fb(self, username, idfb):
		cookie_fb = ''
		for nick in self.list_nick:
			info = nick.split('|')
			if len(info)<3: continue
			if info[0] == username:
				cookie_fb = f'c_user={idfb};xs={info[2]};'
		return cookie_fb

	def get_name_fb(self, token, fbid):
		url = f'https://graph.facebook.com/{fbid}/?fields=name&access_token={token}'
		try:
			r = self.ses.get(url)
			data = r.json()
			name = data['name']
			return name
		except:
			return '?????'

	def check_cookie_fb(self, cookie_fb):
		token = self.get_token_fb(cookie_fb)
		if token=='': return False
		else: return True

	def get_save_info(self, token_fb):
		params = {'access_token': token_fb}
		url = 'https://graph.facebook.com/me?feed'
		res = self.ses.get(url, params=params)
		data = res.json()
		if 'error' not in data:
			# try:
			path_data = f'data/nicks/{data["name"]}_{data["id"]}'
			if not os.path.exists(path_data): os.mkdir(path_data)
			path_info = f'{path_data}/info.json'
			self.save_file_json(path_info, data)
			# except: pass

	def save_file_json(self, path_input, data):
		f = open(path_input, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()

	def load_file_json(self, path_input):
		f = open(path_input, 'r', encoding='utf8')
		data = json.load(f)
		f.close()
		return data


class setting_mt():
	def save_file_json(self, path_input, data):
		f = open(path_input, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()

	def load_file_json(self, path_input):
		f = open(path_input, 'r', encoding='utf8')
		data = json.load(f)
		f.close()
		return data

	def fill_cookie(self, cookie):
		try:
			cookie = cookie.split(';')
			for cookie_tp in cookie:
				if 'c_user' in cookie_tp: c_user = cookie_tp.split('=')[1]
				if 'xs' in cookie_tp: xs = cookie_tp.split('=')[1]
				if 'datr' in cookie_tp: datr = cookie_tp.split('=')[1]
			cookie = f'c_user={c_user};xs={xs};datr={datr};'
			return cookie
		except: return ''

	def show_nick(self):
		list_nick = self.load_file_json('data/nicks.json')
		print("<<<///Danh sách nick chạy:")
		cout = 0
		for nick in list_nick:
			print(f"{cout}.{list_nick[cout]['username']}|{list_nick[cout]['name_fb']}")
			cout+=1
		print("///>>>")
	
	def add_nick(self, username, password, cookie):
		list_nick = self.load_file_json('data/nicks.json')
		nick = {}
		nick['username'] = username
		nick['password'] = password
		nick['cookie'] = self.fill_cookie(cookie)
		nick['name_fb'] = '???'
		list_nick.append(nick)
		self.save_file_json('data/nicks.json', list_nick)

	def edit_nick(self, vt, cookie):
		try:
			list_nick = self.load_file_json('data/nicks.json')
			cookie = self.fill_cookie(cookie)
			if cookie != '': list_nick[vt]['cookie'] = cookie
			self.save_file_json('data/nicks.json', list_nick)
		except: pass

	def delete_nick(self, vt):
		try:
			list_nick = self.load_file_json('data/nicks.json')
			list_nick.pop(vt)
			self.save_file_json('data/nicks.json', list_nick)
		except: pass

	def time_now(self):
		h = localtime().tm_hour
		p = localtime().tm_min
		s = localtime().tm_sec
		if int(h)<10: h = f'0{h}'
		if int(p)<10: p = f'0{p}'
		if int(s)<10: s = f'0{s}'
		time_now = f'{h}:{p}:{s}'
		return time_now

	def log_current(self, username, sl=None):
		storage_nv = self.load_file_json('data/update.json')
		if username not in storage_nv: storage_nv[username] = 0
		if sl!=None: storage_nv[username] += sl
		self.save_file_json('data/update.json', storage_nv)

	def get_current(self, username):
		storage_nv = self.load_file_json('data/update.json')
		if username not in storage_nv: storage_nv[username] = 0
		sl_current = storage_nv[username]
		return sl_current

	def check_reset(self):
		check = f'{localtime().tm_mday}{localtime().tm_mon}'
		today = open('data/today.txt', 'r').read()
		if today!=check:
			open('data/update.json', 'w').write('{}')
			open('data/today.txt', 'w').write(f'{localtime().tm_mday}{localtime().tm_mon}')

	def save_name_fb(self, username, name_fb):
		list_nick = self.load_file_json('data/nicks.json')
		for cout in range(0, len(list_nick)):
			if list_nick[cout]['username'] == username:
				list_nick[cout]['name_fb'] = name_fb
				break
		self.save_file_json('data/nicks.json', list_nick)