from __future__ import print_function
import requests
from os import _exit,path,devnull
from sys import stdout
from time import sleep
from random import seed,choice,randint
from string import ascii_letters,digits
from colorama import Fore
from argparse import ArgumentParser
from traceback import format_exc,print_exc
from threading import Thread,Lock
from user_agent import generate_user_agent

def exit(exit_code):
	if exit_code==1:
		print_exc()
	_exit(exit_code)
def print(message):
	if message.startswith('[ERROR]'):
		colour=Fore.RED
	elif message.startswith('[WARNING]'):
		colour=Fore.YELLOW
	elif message.startswith('[INFO]'):
		colour=Fore.GREEN
	else:
		colour=Fore.RESET
	stdout.write('%s%s%s\n'%(colour,message,Fore.RESET))
def get_proxies():
	global args
	if args.proxies:
		proxies=open(args.proxies,'r').read().strip().split('\n')
	else:
		proxies=requests.get('https://www.proxy-list.download/api/v1/get?type=http&anon=elite').content.decode().strip().split('\r\n')
	print('[INFO][0] %d proxies successfully loaded!'%len(proxies))
	return proxies
def bot(id):
	global locks,user_agents,proxies
	while True:
		try:
			with locks[0]:
				if len(proxies)==0:
					proxies.extend(get_proxies())
				proxy=choice(proxies)
				proxies.remove(proxy)
			print('[INFO][%d] Connecting to %s'%(id,proxy))
			user_agent=choice(user_agents) if args.user_agent else user_agents()
			print('[INFO][%d] Setting user agent to %s'%(id,user_agent))
			email=''.join([choice(ascii_letters+digits) for _ in range(randint(1,20))])
			print('[INFO][%d] Setting email to %s@gmail.com'%(id,email))
			password=''.join([choice(ascii_letters+digits) for _ in range(randint(8,20))])
			print('[INFO][%d] Setting password to %s'%(id,password))
			response=requests.post('http://matzoo.pl/rejestracja',data={
				'email1':'%s@gmail.com'%email,
				'email2':'%s@gmail.com'%email,
				'password1':password,
				'password2':password,
				'regulamin':'1',
				'zgoda':'1',
				'newsletter':'1'
			},headers={
				'User-Agent':user_agent
			},proxies={
				'http':proxy
			})
			if b'UDA\xc5\x81O SI\xc4\x98! Twoje konto zosta\xc5\x82o utworzone.' in response.content:
				print('[INFO][%d] Successfully created account!'%id)
			else:
				print('[ERROR][%d] Could not create account!'%id)
		except KeyboardInterrupt:pass
		except:
			with locks[1]:exception=format_exc()

if __name__=='__main__':
	try:
		seed()
		parser=ArgumentParser()
		parser.add_argument('-t','--threads',type=int,help='set number of the threads',default=15)
		parser.add_argument('-p','--proxies',help='set the path of the proxies list')
		parser.add_argument('-us','--user-agent',help='set the user agent/set the path of to the list of user agents')
		args=parser.parse_args()
		if args.user_agent:
			if path.isfile(args.user_agent):
				user_agents=open(args.user_agent,'r').read().strip().split('\n')
			else:
				user_agents=[args.user_agent]
		else:
			user_agents=generate_user_agent
		locks=[Lock() for _ in range(2)]
		proxies=[]
		for i in range(args.threads):
			t=Thread(target=bot,args=(i+1,))
			t.daemon=True
			t.start()
		while True:
			try:exception
			except:pass
			else:
				print(exception)
				exit(2)
			sleep(0.25)
	except KeyboardInterrupt:exit(0)
	except:exit(1)
