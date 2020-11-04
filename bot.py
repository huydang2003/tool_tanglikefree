import requests
from bs4 import BeautifulSoup
import json
import os
import random
from time import sleep
import re

class Tool_Tanglikefree():
	def __init__(self, list_nick, list_cookie):
		self.ses = requests.session()
		self.list_nick = list_nick
		self.list_cookie = list_cookie
		self.list_config = {}
		self.cout_all = {}
		self.list_nick_out = []
		self.list_nick_in = []
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
		url = 'https://tanglikefree.com/api/auth/login'
		payload = {'username': username, 'password': password, 'disable': 'true'}
		res = self.ses.post(url, data = payload)
		data = res.json()
		if data['error'] == False:
			self.list_config[username]['access_token'] = data['data']['access_token']
			access_token = self.list_config[username]['access_token']
			self.list_config[username]['info'] = self.get_info(access_token)	
			idfb = self.list_config[username]['info']['idfb']
			self.list_config[username]['cookie_fb'] = self.get_cookie_fb(idfb)
			cookie_fb = self.list_config[username]['cookie_fb']
			self.list_config[username]['token_fb'] = self.get_token_fb(cookie_fb)
			self.creat_backup(username)
			return True
		else: return False

	def get_info(self, access_token):
		headers = {'Authorization': 'Bearer '+access_token}
		url = 'https://tanglikefree.com/api/auth/user'
		res = self.ses.get(url, headers=headers)
		data = res.json()
		if data['error'] == False: return data['data']

	def get_cookie_fb(self, idfb):
		cout = 0
		for cookie in self.list_cookie:
			cout+=1
			if cookie=='': continue
			temp = re.findall(r'c_user=(.*?);', cookie)
			if temp == []: continue
			temp = temp[0]
			if temp==idfb:
				print(f">>Cookie in line {cout}")
				return cookie
		return ''

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
		token = self.get_headers_fb(cookie_fb)
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

	def like_post(self, idpost, cookie_fb):
		headers = self.get_headers_fb(cookie_fb)
		link = 'https://mbasic.facebook.com/reactions/picker/?is_permalink=1&ft_id='+idpost
		res = self.ses.get(link, headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.body.find(id='root')
		list_li = soup.find_all('li')
		if list_li==[]: return 0	
		url = list_li[0].a.get('href')
		link = 'https://mbasic.facebook.com' + url
		self.ses.get(link, headers=headers)
		return 1

	def submit_post(self, idpost, request_id, access_token):
		headers = self.get_headers_tlf(access_token)
		payload = {'idpost': idpost, 'request_id': request_id}
		url = 'https://tanglikefree.com/api/auth/Post/submitpost'
		res = self.ses.post(url, data=payload, headers=headers)
		data = res.json()
		if data['error']==False: return True
		else: return False

	def make_nv(self, idpost, access_token, cookie_fb):
		res = self.like_post(idpost, cookie_fb)
		if res==0: return False
		request_id = self.get_request_id(access_token)
		check = self.submit_post(idpost, request_id, access_token)
		if check==False: return False
		return 40
# /////////////////////////
	def start(self, username, password):
		if self.list_config[username] == {}:
			check = self.login_tlf(username, password)
			if check!=True:
				print("\t[Login Failed!!!]")
				return False
		token_fb = self.list_config[username]['token_fb']
		if token_fb=='':
			print("\t[COOKIE DIE]")
			return False
		print("\t[Login Success!!!]")
		return True

	def show_nick(self):
		print("<<<<<///Danh sách nick:")
		for cout in range(0, len(self.list_nick)):
			nick = self.list_nick[cout].split('|')[0]
			self.list_config[nick] = {}
			self.cout_all[nick] = {'nv':0, 'coin':0, 'failed':0}
			print(f"\t{cout}.{nick}")
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

		print("[SETTING]")
		check = input('->>Chạy 1 nick[stt], chạy nhiều nick[enter]: ')
		if check!='':
			stt = int(check)
			print(f"!!!Chỉ làm nick: {self.list_nick[stt].split('|')[0]}")
			self.list_nick = [self.list_nick[stt]]

		sl = int(input("\t+Giới hạn NV: "))
		loop = int(input("\t+Nghỉ khi làm được: "))
		time_stop = int(input("\t+Nhập thời gian nghỉ(s): "))
		delay = input('\t+Thời gian mỗi nv(vd:5 10): ').split(' ')
		delay[0] = int(delay[0])
		delay[1] = int(delay[1])

		while True:
			for nick in self.list_nick:
				nick = nick.split('|')
				username = nick[0]
				password = nick[1]
				print(f"\n[Make nick: {username}]")

				if username not in self.list_nick_in: 
					check = self.start(username, password)
					if check!=True: self.list_nick_out.append(username)
					self.show_info(username)
					self.list_nick_in.append(username)

				if username in self.list_nick_out:
					if len(self.list_nick_out) >= len(self.list_nick): return 0
					continue

				print(f">>>making: {self.list_config[username]['name_fb']}")

				access_token = self.list_config[username]['access_token']
				cookie_fb = self.list_config[username]['cookie_fb']
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
							try: res = self.make_nv(idpost, access_token, cookie_fb)
						    except: res = False
							if res==False:
								self.cout_all[username]['failed']+=1
								if self.cout_all[username]['failed']>10:
									check = self.check_cookie_fb(cookie_fb)
									if check==True: print("\t[BLOCK LIKE]")
									else: print("\t[COOKIE DIE]")
									self.list_nick_out.append(username)
									check_close = True
									break
							else:
								cout_loop += 1
								self.list_config[username]['info']['VND'] += res
								self.cout_all[username]['nv'] += 1
								self.cout_all[username]['failed'] = 0
								coin = self.list_config[username]['info']['VND']
								nv = self.cout_all[username]['nv']
								failed = self.cout_all[username]['failed']

								print(f"  >{nv}<|{idpost}|>+40<|{coin} coin", end=' ')
								if nv >= sl:
									print(f"\n[Nick {username} đã hoàn thành chỉ tiêu]")
									self.list_nick_out.append(username)
									check_close = True
									break

								if cout_loop>=loop:
									check_close = True
									break

								s = random.randint(delay[0], delay[1])
								print(f">>> wait {s}s")
								sleep(s)
						if check_close==True: break
					except: sleep(3)
				if len(self.list_nick_out) >= len(self.list_nick): return 0
				print(f"\n[Nghỉ ngơi {time_stop}s]")
				sleep(time_stop)			

	def close_tool(self):
		self.ses.close()
		print("\nKết thúc tool!!!")

if __name__ == '__main__':
	if not os.path.exists('nicks'): os.mkdir('nicks')
	if not os.path.exists('list_nick.txt'): open('list_nick.txt', 'w').close()
	if not os.path.exists('list_cookie.txt'): open('list_cookie.txt', 'w').close()
	os.system('clear')
	print('\n\t>>>TOOL AUTO TANGLIKEFREE<<<\n')
	list_nick = open('list_nick.txt', 'r', encoding='utf8').read().split("\n")
	list_cookie = open('list_cookie.txt', 'r', encoding='utf8').read().split("\n")
	tool = Tool_Tanglikefree(list_nick, list_cookie)
	tool.run_tool()
	tool.close_tool()
	os.system('exit')