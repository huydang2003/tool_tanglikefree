import os
import random
from time import sleep
from include.setting import setting
from include.fb import fb
from include.tanglikefree import tanglikefree
 
class Auto_tanglikefree():
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
		self.tlf = tanglikefree()
		self.fb = fb()
		self.st = setting()
		self.list_nick_running = []
		self.list_nick = None
		self.list_nick_out = []
		self.list_idpost_error = []
		self.cout_all = {}
		self.list_post = {}

	def check_accout(self, username, password, cookie_fb):
		print(f"[Chạy nick: {username}]")
		access_token = self.tlf.login_tlf(username, password)
		if access_token==False:
			print(f'{self.red}[Login failed]{self.white}', end=' -> ')
			return None
		print(f'{self.blue}[Login success]{self.white}', end=' -> ')
		token_fb = self.fb.get_token_fb(cookie_fb)
		if token_fb=='':
			print(f'{self.red}[COOKIE DIE]{self.white}')
			return None
		print(f'{self.blue}[COOKIE LIVE]{self.white}')
		coin = self.tlf.get_coin(access_token)
		name_fb = self.fb.get_name_fb(token_fb)
		self.st.save_name_fb(username, name_fb)
		path_folder = f'data/nicks/{username}'
		self.fb.get_save_info(token_fb, path_folder)
		self.tlf.show_info(username, coin, name_fb)
		return access_token

	def operations(self, list_vt, max_job, cout_stop, time_stop, delay):
		st = delay-2
		en = delay+2
		self.st.check_reset()
		self.list_nick = self.st.load_file_json('data/nicks.json')
		while True:
			for vt in list_vt:
				vt = int(vt)
				username = self.list_nick[vt]['username']
				password = self.list_nick[vt]['password']
				cookie_fb = self.list_nick[vt]['cookie']
				name_fb = self.list_nick[vt]['name_fb']

				if username in self.list_nick_out:
					if len(self.list_nick_out) >= len(list_vt): return 0
					continue

			try:
				if username not in self.list_nick_running:
					self.list_nick_running.append(username)
					self.list_post[username] = []
					access_token = self.check_accout(username, password, cookie_fb)
					if access_token == None: return 0
					self.cout_all[username] = self.st.get_current(username)
				else:
					access_token = self.tlf.login_tlf(username, password)

				cout_error = 0
				cout_local = 0
				while True:
						if len(self.list_post[username])==0:
							print('[Đang lấy NV]', end=' -> ')
							coin = self.tlf.get_coin(access_token)
							self.list_post[username] = self.tlf.get_post(access_token)
							if len(self.list_post[username])==0:
								print(f'{self.red}[HẾT NV]{self.white}')
								break
							print(f'{len(self.list_post[username])}')
						post = random.choice(self.list_post[username])
						self.list_post[username].remove(post)

						idpost = post['idpost']
						if idpost in self.list_idpost_error: continue

						check = self.fb.like_post(idpost, cookie_fb)
						if check!=1:
							if check==0:
								self.list_idpost_error.append(idpost)
								continue
							elif check==2:
								print(f'\t{self.red}[COOKIE DIE]{self.white}')
								self.list_nick_out.append(username)
								self.st.log_current(username, cout_local)
								break
						else:
							check = self.tlf.finish(access_token, idpost)
							if check==False:
								cout_error += 1
								print(f'{self.red}...{self.white}')
								if cout_error>=9:
									check = self.fb.check_cookie_fb(cookie_fb)
									if check==True: print(f'\t{self.red}[BLOCK LIKE]{self.white}')
									else: print(f'\t{self.red}[COOKIE DIE]{self.white}')
									self.list_nick_out.append(username)
									self.st.log_current(username, cout_local)
									break
							else:
								cout_local += 1
								cout_error = 0
								self.cout_all[username] += 1
								job_current = self.cout_all[username]
								coin += 40
								time_now = self.st.time_now()
								print(f'{self.yellow}[{time_now}]{self.white}', end=' ')
								print(f'{self.green}[{job_current}]|{name_fb}|+40|{coin} coin{self.white}', end=' ')
								if self.cout_all[username] >= max_job:
									print(f"\n[Nick {username} đã hoàn thành số lượng]")
									self.st.log_current(username, cout_local)
									self.list_nick_out.append(username)
									return 0

								if cout_local>=cout_stop:
									self.st.log_current(username, cout_local)
									break
								s = random.randint(st, en)
								print(f"{self.blue}[wait {s}s]{self.white}")
								sleep(s)
				print(f"\n\t[CHUYỂN NICK SAU {time_stop}s]")
				sleep(time_stop)
			except:
				while True:
					print(f'\t{self.red}lỗi mạng đợi 15s{self.white}')
					sleep(15)
					access_token = self.tlf.login_tlf(username, password)
					if access_token!=None: break


	def run(self):
		check = "1"
		if check=='0':
			self.yellow=self.red=self.green=self.white=self.blue=''
			cl = 'cls'
		elif check=='1': cl = 'clear'
		while True:
			os.system(cl)
			self.st.show_nick()
			print('[OPTION]')
			print('\t1.Chạy\n\t2.Chỉnh sửa\n\t3.Thêm\n\t4.Xóa\n<><><><><><><>')
			check = input("***Nhập lựa chọn: ")
			if check!='1':
				if check!='2':
					if check=='4':
						while True:
							try:
								vt = int(input("+Chọn nick cần xóa: "))
								self.st.delete_nick(vt)
								os.system(cl)
								self.st.show_nick()
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
								tool.st.add_nick(username, password, cookie)
								os.system(cl)
								self.st.show_nick()
								print("\t[Thêm thành công!!!]")
								op = input('Thêm nữa không(y/n):')
								if op!='y': break
							except: break
					os.system(cl)
					self.st.show_nick()
				elif check=='2':
					while True:
						try:
							vt = int(input("+Chọn nick cần sửa: "))
							cookie = input("Cookie: ")
							self.st.edit_nick(vt, cookie)
							print("\t[Sửa thành công!!!]")
							op = input('Có muốn sửa nữa không(y/n):')
							if op!='y': break
						except: break
					os.system(cl)
					self.st.show_nick()
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
					self.st.show_nick()
					print('[SETTING]')
					max_job = int(input("\t+Giới hạn NV: "))
					cout_stop = int(input("\t+Nghỉ khi làm được: "))
					time_stop = int(input("\t+Nhập thời gian nghỉ(s): "))
					delay = int(input("\t+Delay(>3s): "))
				list_vt = input('>>>>>Nhập nick chạy: ').split(' ')
				print('[START]')
				self.operations(list_vt, max_job, cout_stop, time_stop, delay)
				print("[Kết thúc tool]")
				return 0

if __name__ == '__main__':
	tool = Auto_tanglikefree()
	tool.run()