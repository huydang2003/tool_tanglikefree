import requests
import json

class tanglikefree():
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

	
	def login_tlf(self, username, password):
		try:
			url = 'https://tanglikefree.com/api/auth/login'
			payload = {'username': username, 'password': password, 'disable': 'true'}
			res = self.ses.post(url, data = payload)
			data = res.json()
			if data['error'] != False: return False
			access_token = data['data']['access_token']
			return access_token
		except: return None
		
	def get_coin(self, access_token):
		headers = {'Authorization': 'Bearer '+access_token}
		url = 'https://tanglikefree.com/api/auth/user'
		res = self.ses.get(url, headers=headers)
		data = res.json()
		if data['error'] != False: return None
		coin = data['data']['VND']
		return coin
		
	def show_info(self, username, coin, name_fb):
		print('<==================>')
		print(f"USERNAME:{username}")
		print(f"COIN:{coin}")
		print(f"NAME FB:{name_fb}")
		print('<==================>')

	def get_post(self, access_token):
		headers = self.get_headers_tlf(access_token)
		url = 'https://tanglikefree.com/api/auth/Post/getpost'
		res = self.ses.get(url, headers=headers)
		list_post = res.json()
		return list_post

	def get_request_id(self, access_token):
		headers = self.get_headers_tlf(access_token)
		url = 'https://tanglikefree.com/api/auth/creat_request'	
		res = self.ses.get(url, headers=headers)
		data = res.json()
		request_id = data['request_id']
		return request_id

	def submit_post(self, idpost, request_id, access_token):
		headers = self.get_headers_tlf(access_token)
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