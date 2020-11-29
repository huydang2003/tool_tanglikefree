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
	if not os.path.exists('data/nicks'): os.mkdir('data/nicks')
	if not os.path.exists('data/nicks.json'): open('data/nicks.json', 'w').write('[]')
	if not os.path.exists('data/today.txt'): open('data/today.txt', 'w').write(f'{localtime().tm_mday}{localtime().tm_mon}')
	if not os.path.exists('data/update.json'): open('data/update.json', 'w').write('{}')
	green = '\33[32m'
	red = '\33[31m'
	yellow = '\33[33m'
	white = '\33[37m'
	blue   = '\33[34m'
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

	def like_post(self, idpost, cookie_fb):
		link = f'https://mbasic.facebook.com/reactions/picker/?is_permalink=1&ft_id={idpost}&origin_uri=https://mbasic.facebook.com'
		headers = self.fb_mt.get_headers_fb(cookie_fb)
		res = self.ses.get(link, headers=headers)
		link = res.url
		if 'login.php' in link: return 2
		else:
			soup = BeautifulSoup(res.content, 'html.parser')
			soup = soup.body.find(id='root')
			list_li = soup.find_all('li')
			if list_li!=[]:	
				url = list_li[0].a.get('href')
				link = 'https://mbasic.facebook.com' + url
				self.ses.get(link, headers=headers)
				return 1
			else: return 0

	def submit_post(self, idpost, request_id, access_token):
		headers = self.fb_mt.get_headers_tlf(access_token)
		payload = {'idpost': idpost, 'request_id': request_id}
		url = 'https://tanglikefree.com/api/auth/Post/submitpost'
		res = self.ses.post(url, data=payload, headers=headers)
		data = res.json()
		if data['error']==False: return True
		else: return False

	def finish(self, access_token, idpost):
		request_id = self.get_request_id(access_token)
		check = self.submit_post(idpost, request_id, access_token)
		if check==False: return False
		else: return True

	def process(self, list_vt, max_job, cout_stop, time_stop, delay):
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
						self.list_access_token[username] = self.login_tlf(username, password)
						access_token = self.list_access_token[username]
						if access_token == None:
							print(f'\t{self.red}[Login failed]{self.white}')
							self.list_nick_out.append(username)
							return 0
						print(f'\t{self.blue}[Login success]{self.white}')
						token_fb = self.fb_mt.get_token_fb(cookie_fb)
						if token_fb == '':
							print(f'\t{self.red}[COOKIE DIE]{self.white}')
							self.list_nick_out.append(username)
							return 0
						self.fb_mt.get_save_info(username, token_fb)
						info = self.get_info(access_token)
						info['name_fb'] = self.fb_mt.get_name_fb(token_fb, info['idfb'])
						self.setting_mt.save_name_fb(username, info['name_fb'])
						self.show_info(info)

						self.name[username] = info['name_fb']
						self.cout_coin[username] = info['VND']
						self.setting_mt.log_current(username)
						self.cout_all[username] = self.setting_mt.get_current(username)
						self.list_post[username] = []

					access_token = self.list_access_token[username]

					cout_error = 0
					cout_local = 0
					while True:
						if len(self.list_post[username])==0:
							self.list_post[username] = self.get_post(access_token)
							if len(self.list_post[username])==0:
								print(f'\t{self.red}[HẾT NV]{self.white}')
								break
						post = random.choice(self.list_post[username])
						self.list_post[username].remove(post)

						idpost = post['idpost']
						if idpost in self.list_idpost_error: continue

						res = self.like_post(idpost, cookie_fb)
						if res!=1:
							if res==0:
								self.list_idpost_error.append(idpost)
								continue
							elif res==2:
								print(f'\t{self.red}[COOKIE DIE]{self.white}')
								self.list_nick_out.append(username)
								self.setting_mt.log_current(username, cout_local)
								break
						else:
							check = self.finish(access_token, idpost)
							if check==False:
								cout_error += 1
								print('...')
								if cout_error>=5:
									check = self.fb_mt.check_cookie_fb(cookie_fb)
									if check==True: print(f'\t{self.red}[BLOCK LIKE]{self.white}')
									else: print(f'\t{self.red}[COOKIE DIE]{self.white}')
									self.list_nick_out.append(username)
									self.setting_mt.log_current(username, cout_local)
									break
							elif check==True:
								cout_local += 1
								cout_error = 0
								self.cout_all[username] += 1
								self.cout_coin[username] += 40
								time_now = self.setting_mt.time_now()
								job_current = self.cout_all[username]
								name_fb = self.name[username]
								coin = self.cout_coin[username]
								print(f'{self.yellow}[{time_now}]{self.white}', end=' ')
								print(f'{self.green}[{job_current}]|{name_fb}|+40|{coin} coin{self.white}', end=' ')
								if self.cout_all[username] >= max_job:
									print(f"\n[Nick {username} đã hoàn thành số lượng]")
									self.setting_mt.log_current(username, cout_local)
									self.list_nick_out.append(username)
									return 0

								if cout_local>=cout_stop:
									self.setting_mt.log_current(username, cout_local)
									break
								s = random.randint(delay-2, delay+2)
								print(f"{self.blue}[wait {s}s]{self.white}")
								sleep(s)
					print(f"\n\t[CHUYỂN NICK SAU {time_stop}s]")
					sleep(time_stop)
				except:	
					while True:
						print(f"{self.red}sleep 5s{self.white}")
						sleep(5)
						self.list_access_token[username] = tool.login_tlf(username, password)
						if self.list_access_token[username] != None: break

	def run(self):
		#print("<><><><><><><><><><><>")
		#print('\t+Windows(0)\n\t+Termux(1)')
		#check = input('***Chạy trên: ')
		check = "1"
		if check=='0':
			self.yellow=self.red=self.green=self.white=self.blue=''
			cl = 'cls'
		elif check=='1': cl = 'clear'
		while True:
			os.system(cl)
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
							except: break
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
							except: break
					os.system(cl)
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
						except: break
					os.system(cl)
					self.setting_mt.show_nick()
			elif check=='1':
				print('[SETTING]')
				print("\t+Giới hạn NV: 500")
				print("\t+Nghỉ khi làm được: 5")
				print("\t+Nhập thời gian nghỉ(s): 15")
				print("\t+Delay(>3s): 3 ")
				max_job = 500
				cout_stop = 5
				time_stop = 15
				delay = 3
				check = input("+Mặc định?(y/n): ")
				if check=='n':
					os.system(cl)
					self.setting_mt.show_nick()
					print('[SETTING]')
					max_job = int(input("\t+Giới hạn NV: "))
					cout_stop = int(input("\t+Nghỉ khi làm được: "))
					time_stop = int(input("\t+Nhập thời gian nghỉ(s): "))
					delay = int(input("\t+Delay(>3s): "))
				list_vt = input('>>>>>Nhập nick chạy: ').split(' ')
				print('[START]')
				self.setting_mt.check_reset()
				self.list_nick = self.setting_mt.load_file_json('data/nicks.json')
				self.process(list_vt, max_job, cout_stop, time_stop, delay)
				print("[Kết thúc tool]")
				return 0

if __name__ == '__main__':
	tool = Tool_Tanglikefree()
	tool.run()
