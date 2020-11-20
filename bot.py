import requests
from bs4 import BeautifulSoup
import json
import os
import random
from time import sleep, localtime
import re
from include.include import fb_mt, setting_mt

class Tool_Tanglikefree():
	if not os.path.exists('data'): os.mkdir('data')
	# if not os.path.exists('data/nicks'): os.mkdir('data/nicks')
	if not os.path.exists('data/nicks.json'): open('data/nicks.json', 'w').write('[]')
	if not os.path.exists('data/today.txt'): open('data/today.txt', 'w').write(f'{localtime().tm_mday}{localtime().tm_mon}')
	if not os.path.exists('data/update.json'): open('data/update.json', 'w').write('{}')
	def __init__(self):
		self.ses = requests.session()
		self.fb_mt = fb_mt()
		self.setting_mt = setting_mt()
		self.list_nick = None
		self.list_access_token = {}
		self.list_nick_out = []
		self.list_idpost_error = []
		self.cout_all = {}
		self.cout_coin = {}
		self.name = {}
		self.list_post = {}

	def login_tlf(self, username, password):
		try:
			url = 'https://tanglikefree.com/api/auth/login'
			payload = {'username': username, 'password': password, 'disable': 'true'}
			res = self.ses.post(url, data = payload)
			data = res.json()
			if data['error'] != False: return None
			access_token = data['data']['access_token']
			return access_token	
		except:
			return None

	def get_info(self, access_token):
		try:
			headers = {'Authorization': 'Bearer '+access_token}
			url = 'https://tanglikefree.com/api/auth/user'
			res = self.ses.get(url, headers=headers)
			data = res.json()
			if data['error'] != False: return None
			info = data['data']
			return info
		except:
			return None

	def show_info(self, info):
		acc = info['username']
		idfb = info['idfb']
		vnd = info['VND']
		name_fb = info['name_fb']
		print('<==================>')
		print(f"ACC:{acc}")
		print(f"VND:{vnd}")
		print(f"FBID:{idfb}")
		print(f"NAME FB:{name_fb}")
		print('<==================>')

	def get_post(self, access_token):
		headers = self.fb_mt.get_headers_tlf(access_token)
		url = 'https://tanglikefree.com/api/auth/Post/getpost'
		res = self.ses.get(url, headers=headers)
		list_post = res.json()
		return list_post

	def get_request_id(self, access_token):
		headers = self.fb_mt.get_headers_tlf(access_token)
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
			if data['error']['code'] == 368: return 2 # block
			elif data['error']['code'] == 190: return 3 #Cookie die
			else: return 0 #Loi link

	def submit_post(self, idpost, request_id, access_token):
		headers = self.fb_mt.get_headers_tlf(access_token)
		payload = {'idpost': idpost, 'request_id': request_id}
		url = 'https://tanglikefree.com/api/auth/Post/submitpost'
		res = self.ses.post(url, data=payload, headers=headers)
		data = res.json()
		if data['error']==False: return True
		else: return False

	def make_nv(self, idpost, access_token, token_fb):
		request_id = self.get_request_id(access_token)
		res = self.like_post(idpost, token_fb)
		if res==0: return 0
		elif res==2: return 2
		elif res==3: return 3
		else:
			check = self.submit_post(idpost, request_id, access_token)
			if check==False: return 1
			else: return 40

	def process(self, list_vt, max_job, cout_stop, time_stop, delay, st, en):
		while True:
			for vt in list_vt:
				vt = int(vt)

				username = self.list_nick[vt]['username']
				password = self.list_nick[vt]['password']
				cookie_fb = self.list_nick[vt]['cookie']

				if username in self.list_nick_out:
					if len(self.list_nick_out) >= len(list_vt): return 0
					continue

				try:
					if username not in self.list_access_token:
						self.list_access_token[username] = tool.login_tlf(username, password)
						access_token = self.list_access_token[username]
						if access_token == None:
							print('\t[Login failed]')
							self.list_nick_out.append(vt)
							continue
						print('\t[Login success]')
						token_fb = self.fb_mt.get_token_fb(cookie_fb)
						if token_fb == '':
							print("\t[COOKIE DIE]")
							self.list_nick_out.append(vt)
							continue
						info = tool.get_info(access_token)
						info['name_fb'] = self.fb_mt.get_name_fb(token_fb, info['idfb'])
						self.setting_mt.save_name_fb(username, info['name_fb'])
						self.show_info(info)

						self.name[username] = info['name_fb']
						self.cout_coin[username] = info['VND']
						self.setting_mt.log_current(username)
						self.cout_all[username] = self.setting_mt.get_current(username)
						self.list_post[username] = []

					access_token = self.list_access_token[username]
					token_fb = self.fb_mt.get_token_fb(cookie_fb)

					cout_local = 0
					while True:
						while True:
							if len(self.list_post[username]) > 1: break
							self.list_post[username] = self.get_post(access_token)
						post = random.choice(self.list_post[username])
						self.list_post[username].remove(post)

						idpost = post['idpost']
						if idpost in self.list_idpost_error: continue

						res = self.make_nv(idpost, access_token, token_fb)
						if res==0 or res==1:
							self.list_idpost_error.append(idpost)
							continue
						elif res==2 or res==3:
							if res==2: print("\t[BLOCK LIKE]")
							elif res==3: print("\t[COOKIE DIE]")
							self.list_nick_out.append(username)
							self.setting_mt.log_current(username, cout_local)
							break
						else:
							cout_local += 1
							self.cout_all[username] += 1
							self.cout_coin[username] += 40
							time_now = self.setting_mt.time_now()
							job_current = self.cout_all[username]
							name_fb = self.name[username]
							coin = self.cout_coin[username]
							print(f'[{time_now}] [{job_current}]|{name_fb}|+40|{coin} coin')
							if self.cout_all[username] >= max_job:
								print(f"\n[Nick {username} đã hoàn thành số lượng]")
								self.setting_mt.log_current(username, cout_local)
								self.list_nick_out.append(username)
								return 0

							if cout_local>=cout_stop:
								self.setting_mt.log_current(username, cout_local)
								break
							s = random.randint(st, en)
							sleep(s)

					print(f"[CHUYỂN NICK SAU {time_stop}s]")
					sleep(time_stop)
				except:
					while True:
						print("Loi mang")
						sleep(5)
						self.list_access_token[username] = tool.login_tlf(username, password)
						if self.list_access_token[username] != None: break

	def run(self):
		while True:
			print("\n<><><><><>=========<><><><><><>\n")
			# os.system('clear')
			# os.system('cls')
			self.setting_mt.show_nick()
			print('[OPTION]')
			print('\t1.Chạy\n\t2.Chỉnh sửa\n\t3.Thêm\n\t4.Xóa\n<><><><><><><>')
			check = input("***Nhập lựa chọn: ")
			if check!='1':
				if check!='2':
					if check=='4':
						while True:
							try:
								vt = int(input("+Chọn nick cần xóa: "))
								self.setting_mt.delete_nick(vt)
								print("\t[Xóa thành công!!!]")
								op = input('Xóa nữa không(y/n):')
								if op!='y': break
							except: pass
					elif check=='3':
						while True:
							try:
								username = input("+username: ")
								password = input("+password: ")
								cookie = input("+cookie: ")
								tool.setting_mt.add_nick(username, password, cookie)
								print("\t[Thêm thành công!!!]")
								op = input('Thêm nữa không(y/n):')
								if op!='y': break
							except: pass
					# os.system('clear')
					# os.system('cls')
					self.setting_mt.show_nick()
				elif check=='2':
					while True:
						try:
							vt = int(input("+Chọn nick cần sửa: "))
							cookie = input("Cookie: ")
							self.setting_mt.edit_nick(vt, cookie)
							print("\t[Sửa thành công!!!]")
							op = input('Có muốn sửa nữa không(y/n):')
							if op!='y': break
						except: pass
					# os.system('clear')
					# os.system('cls')
					self.setting_mt.show_nick()
			elif check=='1':
				list_vt = input('>>>>>Nhập nick chạy: ').split(' ')
				print('[SETTING]')
				max_job = int(input("\t+Giới hạn NV: "))
				cout_stop = int(input("\t+Nghỉ khi làm được: "))
				time_stop = int(input("\t+Nhập thời gian nghỉ(s): "))
				delay = input("\t+Delay(vd:5 10): ").split(' ')
				st = int(delay[0])
				en = int(delay[1])
				print('[START]')
				self.setting_mt.check_reset()
				self.list_nick = json.load(open('data/nicks.json'))
				self.process(list_vt, max_job, cout_stop, time_stop, delay, st, en)
				print("[Kết thúc tool]")
				return 0

if __name__ == '__main__':
	tool = Tool_Tanglikefree()
	tool.run()
