import requests
from bs4 import BeautifulSoup
import json
import os
import random
from time import sleep, localtime
import re

class Tool_Tanglikefree():
	def __init__(self, list_nick):
		self.ses = requests.session()
		self.list_nick = list_nick
		self.list_config = {}
		self.cout_all = {}
		self.list_nick_out = []
		self.list_nick_in = []
		self.list_nick_run = []
		self.list_idpost_error = []
		self.headers_fb = None
		self.headers_tlf = None

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

	def get_info(self, access_token):
		headers = {'Authorization': 'Bearer '+access_token}
		url = 'https://tanglikefree.com/api/auth/user'
		res = self.ses.get(url, headers=headers)
		data = res.json()
		if data['error'] == False: return data['data']

	def get_cookie_fb(self, username, idfb):
		cookie_fb = ''
		for nick in self.list_nick:
			info = nick.split('|')
			if len(info)<3: continue
			if info[0] == username:
				cookie_fb = f'c_user={idfb};xs={info[2]};'
		return cookie_fb

	def get_token_fb(self, cookie_fb):
		headers = self.get_headers_fb(cookie_fb)
		url = 'https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed'
		res = self.ses.get(url, headers=headers)
		token = re.findall(r'accessToken\\":\\"(.*?)\\', res.text)
		if token != []: token = token[0]
		else: token = ''
		return token

	def creat_backup(self, username):
		token_fb = self.list_config[username]['token_fb']
		if token_fb!='':
			params = {'access_token': token_fb}
			url = 'https://graph.facebook.com/me?feed'
			res = self.ses.get(url, params=params)
			data = res.json()
			self.list_config[username]['name_fb'] = data["name"]
			path_index = f'nicks/{username}'
			if not os.path.exists(path_index): os.mkdir(path_index)
			path_data = f'{path_index}/{data["name"]}_{data["id"]}'
			if not os.path.exists(path_data): os.mkdir(path_data)
			path_output = f'{path_data}/info.json'
			f = open(path_output, 'w', encoding='utf8')
			json.dump(data, f, ensure_ascii=False, indent=4)
			f.close()
	def check_cookie_fb(self, cookie_fb):
		token = self.get_token_fb(cookie_fb)
		if token=='': return False
		else: return True
# ////////////////////////
	def get_post(self, access_token):
		headers = self.get_headers_tlf(access_token)
		url = 'https://tanglikefree.com/api/auth/Post/getpost'
		res = self.ses.get(url, headers=headers)
		list_post = res.json()
		return list_post
# /////////////////////////
	def get_request_id(self, access_token):
		headers = self.get_headers_tlf(access_token)
		url = 'https://tanglikefree.com/api/auth/creat_request'	
		res = self.ses.get(url, headers=headers)
		data = res.json()
		request_id = data['request_id']
		return request_id
	
	def like_post(self, idpost, token_fb):
		params = {'access_token': token_fb}
		url = f'https://graph.facebook.com/{idpost}/likes'
		res = self.ses.post(url, params=params)
		data = res.json()
		if data == True: return 1
		else:
			if data['error']['code'] != 368: return 0
			else: return 2

	def submit_post(self, idpost, request_id, access_token):
		headers = self.get_headers_tlf(access_token)
		payload = {'idpost': idpost, 'request_id': request_id}
		url = 'https://tanglikefree.com/api/auth/Post/submitpost'
		res = self.ses.post(url, data=payload, headers=headers)
		data = res.json()
		if data['error']==False: return True
		else: return False
# 40 thành công, 1 thất bại, 2 lỗi link, 3 chặn like, 4 cookie die 
	def make_nv(self, idpost, access_token, cookie_fb, token_fb):
		res = self.like_post(idpost, token_fb)
		if res==0:
			check = self.check_cookie_fb(cookie_fb)
			if check==False: return 4
			else: return 2
		elif res==2:
			check = self.check_cookie_fb(cookie_fb)
			if check==False: return 4
			else: return 3
		else:
			request_id = self.get_request_id(access_token)
			check = self.submit_post(idpost, request_id, access_token)
			if check==False: return 1
			else: return 40
# /////////////////////////
	def time_now(self):
		time_now = f'{localtime().tm_hour}:{localtime().tm_min}:{localtime().tm_sec}'
		return time_now

	def log_current(self, username, sl=None):
		f = open('update.json', 'r')
		storage_nv = json.load(f)
		f.close()
		f = open('update.json', 'w')
		if username not in storage_nv: storage_nv[username] = 0
		if sl!=None: storage_nv[username] += sl
		json.dump(storage_nv, f, indent=4)
		f.close()

	def get_current(self, username):
		f = open('update.json', 'r')
		storage_nv = json.load(f)
		sl_current = storage_nv[username]
		f.close()
		return sl_current

	def check_reset(self):
		check = f'{localtime().tm_mday}{localtime().tm_mon}'
		today = open('today.txt', 'r').read()
		if today!=check:
			open('update.json', 'w').write('{}')
			open('today.txt', 'w').write(f'{localtime().tm_mday}{localtime().tm_mon}')

	def show_nick(self):
		print("<<<<<///Danh sách nick:")
		cout = 1
		for nick in self.list_nick:
			if '###' in nick: continue
			nick = nick.split('|')[0]
			self.list_config[nick] = {}
			self.cout_all[nick] = {'nv':0, 'coin':0}
			print(f"\t{cout}.{nick}")
			cout+=1
		print("///>>>>>")

	def show_info(self, username):
		acc = self.list_config[username]['info']['username']
		idfb = self.list_config[username]['info']['idfb']
		vnd = self.list_config[username]['info']['VND']
		print('<==================>')
		print(f"ACC:{acc}")
		print(f"FBID:{idfb}")
		print(f"VND:{vnd}")
		print('<==================>')

	def run_tool(self):
		self.show_nick()
		self.check_reset()

		try: 
			option = input('->>Nhập nick chạy: ').split(" ")
			for op in option: self.list_nick_run.append(self.list_nick[int(op)])
		except:
			return 0
		
		print("[SETTING]")
		sl = int(input("\t+Giới hạn NV: "))
		loop = int(input("\t+Nghỉ khi làm được: "))
		time_stop = int(input("\t+Nhập thời gian nghỉ(s): "))
		delay = input('\t+Thời gian mỗi nv(vd:5 10): ').split(' ')
		delay[0] = int(delay[0])
		delay[1] = int(delay[1])

		while True:
			for nick in self.list_nick_run:
				nick = nick.split('|')
				username = nick[0]
				password = nick[1]
				print(f"\n==================\n[Make nick: {username}]")

				if username not in self.list_nick_in: 
					self.list_nick_in.append(username)
					self.log_current(username)
					self.cout_all[username]['nv'] = self.get_current(username)
					check = self.login_tlf(username, password)
					if check==True:
						print("\t[Login Success!!!]")
						cookie_fb = self.list_config[username]['cookie_fb']
						check = self.check_cookie_fb(cookie_fb)
						if check==True:
							self.creat_backup(username)
							self.show_info(username)
						else:
							print("\t[COOKIE DIE]")
							self.list_nick_out.append(username)
					else:
						print("\t[Login Failed!!!]")
						self.list_nick_out.append(username)

				if username in self.list_nick_out:
					if len(self.list_nick_out) >= len(self.list_nick_run): return 0
					continue

				print(f">>>making: {self.list_config[username]['name_fb']}")

				access_token = self.list_config[username]['access_token']
				cookie_fb = self.list_config[username]['cookie_fb']
				token_fb = self.list_config[username]['token_fb']
				cout_loop = 0
				check_close = False
				while True:
					try:
						list_post = self.get_post(access_token)
						if list_post==[]:
							print("[Hết NV]") 
							continue
						for post in list_post:
							idpost = post['idpost']
							if idpost in self.list_idpost_error: continue
							res = self.make_nv(idpost, access_token, cookie_fb, token_fb)
							if res==1 or res==2: self.list_idpost_error.append(idpost)
							elif res==3 or res==4:
								if res==3: print("\t[BLOCK LIKE]")
								else: print("\t[COOKIE DIE]")
								self.log_current(username, cout_loop)
								self.list_nick_out.append(username)
								check_close = True
								break
							else:
								cout_loop += 1
								self.cout_all[username]['block'] = 0
								self.list_config[username]['info']['VND'] += res
								self.cout_all[username]['nv'] += 1
								coin = self.list_config[username]['info']['VND']
								nv = self.cout_all[username]['nv']
								time_now = self.time_now()
								print(f"[{time_now}]><[{nv}]|{idpost}|>+40<|{coin} coin", end=' ')

								if nv >= sl:
									print(f"\n[Nick {username} đã hoàn thành chỉ tiêu]")
									self.log_current(username, cout_loop)
									self.list_nick_out.append(username)
									check_close = True
									break
								if cout_loop>=loop:
									self.log_current(username, cout_loop)
									check_close = True
									break

								s = random.randint(delay[0], delay[1])
								print(f"[wait {s}s]")
								sleep(s)
						if check_close==True: break
					except:
						while True:
							self.log_current(username, cout_loop)
							print("!!!Login after 5s")
							sleep(5)
							check = self.login_tlf(username, password)
							if check==True: break
					
				if len(self.list_nick_out) >= len(self.list_nick_run): return 0
				print(f"\n[Nghỉ ngơi {time_stop}s]")
				sleep(time_stop)			

	def close_tool(self):
		self.ses.close()
		print("\nKết thúc tool!!!")

if __name__ == '__main__':
	if not os.path.exists('nicks'): os.mkdir('nicks')
	if not os.path.exists('today.txt'): open('today.txt', 'w').write(f'{localtime().tm_mday}{localtime().tm_mon}')
	if not os.path.exists('update.json'): open('update.json', 'w').write('{}')
	if not os.path.exists('list_nick.txt'): open('list_nick.txt', 'w', encoding='utf8').write("###Định dạng: username|password|cookie_xs")
	os.system('clear')
	print('\n\t>>>TOOL AUTO TANGLIKEFREE<<<\n')
	list_nick = open('list_nick.txt', 'r', encoding='utf8').read().split("\n")
	tool = Tool_Tanglikefree(list_nick)
	tool.run_tool()
	tool.close_tool()