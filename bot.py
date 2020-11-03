import requests
from bs4 import BeautifulSoup
import json
import os
import random
from time import sleep
import re

class Tool_Tanglikefree():
	def __init__(self, username, password):
		self.ses = requests.session()
		self.username = username
		self.password = password
		self.cookie = None
		self.access_token = None
		self.headers_fb = None
		self.headers_tlf = None
		self.info = {}

	def login_tlf(self):
		url = 'https://tanglikefree.com/api/auth/login'
		payload = {'username': self.username, 'password': self.password, 'disable': 'true'}
		res = self.ses.post(url, data = payload)
		data = res.json()
		if data['error'] == False:
			self.access_token = data['data']['access_token']
			self.headers_tlf = {
				'Host': 'tanglikefree.com',
				'Referer': 'https://tanglikefree.com/makemoney',
				'Sec-Fetch-Dest': 'empty',
				'Sec-Fetch-Mode': 'cors',
				'Sec-Fetch-Site': 'same-origin',
				'X-Requested-With': 'XMLHttpRequest',
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
				'Authorization': 'Bearer '+ self.access_token
			}
			self.get_info()
			return True
		else: return False 
			
	def get_info(self):
		headers = {'Authorization': 'Bearer '+self.access_token}
		url = 'https://tanglikefree.com/api/auth/user'
		res = self.ses.get(url, headers=headers)
		data = res.json()
		if data['error'] == False:
			self.info = data['data']
			fb_id = self.info['idfb']
			self.cookie = self.get_cookie(fb_id)

	def get_cookie(self, fb_id):
		list_cookie = open('list_cookie.txt', 'r').read().split('\n')
		cout = 0
		for cookie in list_cookie:
			cout+=1
			if cookie=='': continue
			temp = re.findall(r'c_user=(.*?);', cookie)
			if temp == []: continue
			temp = temp[0]
			if temp==fb_id:
				print(f">>Cookie in line {cout}")
				return cookie
		return ''

	def get_token(self):
		self.headers_fb = {
			'authority': 'mbasic.facebook.com',
			'upgrade-insecure-requests': '1',
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-mode': 'navigate',
			'accept-language': 'en-US,en;q=0.9',
			'user_agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36'
		}
		self.headers_fb['cookie'] = self.cookie
		url = 'https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed'
		res = self.ses.get(url, headers=self.headers_fb)
		token = re.findall(r'accessToken\\":\\"(.*?)\\', res.text)
		if token != []: token = token[0]
		else: token = ''
		return token

	def creat_backup(self, token):
		params = {'access_token': token}
		url = 'https://graph.facebook.com/me?feed'
		res = self.ses.get(url, params=params)
		data = res.json()
		path_data = f'nicks/{data["name"]}_{data["id"]}'
		self.info['name'] = data["name"]
		if not os.path.exists(path_data): os.mkdir(path_data)
		path_output = f'{path_data}/info.json'
		f = open(path_output, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()

	def get_post(self):
		headers = self.headers_tlf
		url = 'https://tanglikefree.com/api/auth/Post/getpost'
		res = self.ses.get(url, headers=headers)
		list_post = res.json()
		return list_post

	def get_request(self):
		headers = self.headers_tlf
		url = 'https://tanglikefree.com/api/auth/creat_request'	
		res = self.ses.get(url, headers=headers)
		data = res.json()
		requests = data['request_id']
		return requests

	def submit_post(self, idpost, request_id):
		headers = self.headers_tlf
		payload = {'idpost': idpost, 'request_id': request_id}
		url = 'https://tanglikefree.com/api/auth/Post/submitpost'
		res = self.ses.post(url, data=payload, headers=headers)
		data = res.json()	
		if data['error']==False:
			return True
		else: return False

	def like_post(self, idpost):
		link = 'https://mbasic.facebook.com/reactions/picker/?is_permalink=1&ft_id='+idpost
		headers = self.headers_fb
		res = self.ses.get(link, headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.body.find(id='root')
		list_li = soup.find_all('li')
		if list_li==[]: return 0	
		url = list_li[0].a.get('href')
		link = 'https://mbasic.facebook.com' + url
		try: self.ses.get(link, headers=headers, timeout=2)
		except: pass
		return 1

	def check_cookie(self):
		token = self.get_token()
		if token=='': return False
		else: return True

# cookie die 0, hoan thanh mot vong lap 1,  het nv 2, block 3

	def run_tool(self, loop, delay):
		token = self.get_token()
		if token=='':
			print(">>>Cookie die!!!")
			return 0
		self.creat_backup(token)
		coin = self.info['VND']
		cout = 0
		cout_failed = 0
		while True:
			while True:
				list_post = self.get_post()
				if len(list_post)>0: break
				print('[Hết NV]')
				return 2

			for post in list_post:
				idpost = post['idpost']
				request_id = self.get_request()
				check = self.like_post(idpost)
				if check==0:
					print('>>>link error!!!')	
					check = self.check_cookie()
					if check == False:
						print(">>>Cookie die!!!")
						return 0

				else:
					ck = self.submit_post(idpost, request_id)
					if ck!=True:
						cout_failed+=1
						if cout_failed > 3:
							check = self.check_cookie()
							if check == True:
								print("[Block like!!!]")
								return 3
							else:
								print(">>>Cookie die!!!")
								return 0		
					else:
						cout += 1
						coin += 40
						print(f"  >{cout}<|{idpost}|>+40<|{coin} coin", end=' ')
						if cout>=loop: return 1
						s = random.randint(delay[0], delay[1])
						print(f">>> wait {s}s")
						sleep(s)

if __name__ == '__main__':
	if not os.path.exists('nicks'): os.mkdir('nicks')
	if not os.path.exists('list_nick.txt'): open('list_nick.txt', 'w').close()
	if not os.path.exists('list_cookie.txt'): open('list_cookie.txt', 'w').close()
	print('\n\t>>>TOOL AUTO TANGLIKEFREE<<<\n')
	print("Vào thư mục chứa file thiết lập!!!")
	print("[setting]")
	time_change = int(input("+Nhập thời gian chuyển nick: "))
	sl = int(input("+Giới hạn NV làm mỗi nick: "))
	loop = int(input("+Chuyển nick khi làm được: "))
	delay = input('+Thời gian mỗi nv(vd:5 10): ').split(' ')
	delay[0] = int(delay[0])
	delay[1] = int(delay[1])

	list_nick = open('list_nick.txt', 'r', encoding='utf8').read().split("\n")
	list_nick_out = []
	max_job = {}
	check_close = False
	while True:
		if check_close: break
		for nick in list_nick:
			username = nick.split('|')[0]
			if username not in max_job: max_job[username] = 0
			if username in list_nick_out: continue
			print(f"\n[Make nick: {username}]")
			password = nick.split('|')[1]
			tool = Tool_Tanglikefree(username, password)
			check = tool.login_tlf()
			if check == True:
				print(">>>Login Success!!!")
				print(f"\n>>>making: {tool.info['name']}({tool.info['idfb']})")
				check = tool.run_tool(loop, delay)

				if check==0 or check==3: list_nick_out.append(username)
				else: max_job[username] += loop
				if max_job[username] >= sl:
					print(f"\n[Nick {username} đã hoàn thành chỉ tiêu]")
					list_nick_out.append(username)

				if len(list_nick_out) >= len(list_nick):
					check_close = True
					break

				print(f"\n[Chuyển nick sau {time_change}s]")
				sleep(time_change)
			else:
				print(">>>Login Failed!!!")
	print("\nKết thúc tool!!!")