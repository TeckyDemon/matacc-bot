import re
import requests
from os import _exit
from sys import stdout
from time import sleep
from random import choice,randint
from string import ascii_letters,digits
from argparse import ArgumentParser
from traceback import format_exc
from threading import Thread,Lock,Event

def exit(exit_code):
	global args,accounts
	with open(args.output,'w+') as f:
		f.write('\n'.join(accounts))
	logv('[INFO] Exiting with exit code %d'%exit_code)
	_exit(exit_code)
def logv(message):
	stdout.write('%s\n'%message)
	if message.startswith('[ERROR]'):
		exit(1)
def log(message):
	global args
	if args.debug:
		logv(message)
def get_proxies():
	global args
	if args.proxies:
		proxies=open(args.proxies,'r').read().strip().split('\n')
	else:
		proxies=requests.get('https://www.proxy-list.download/api/v1/get?type=http&anon=elite').content.decode().strip().split('\r\n')
	log('[INFO] %d proxies successfully loaded!'%len(proxies))
	return proxies
def get_random_string(min,max):
	return ''.join([choice(ascii_letters+digits) for _ in range(randint(min,max))])
def bot(id):
	global args,locks,exception,exception_event,proxies
	while True:
		try:
			with locks[0]:
				if len(proxies)==0:
					proxies.extend(get_proxies())
				proxy=choice(proxies)
				proxies.remove(proxy)
			log('[INFO][%d] Connecting to %s'%(id,proxy))
			user_agent=get_random_string(10,100)
			log('[INFO][%d] Setting user agent to %s'%(id,user_agent))
			email='%s@%s'%(
				get_random_string(8,40),
				choice(['gmail.com','yahoo.com','hotmail.com','aol.com'])
			)
			log('[INFO][%d] Setting email to %s'%(id,email))
			password=get_random_string(8,40)
			log('[INFO][%d] Setting password to %s'%(id,password))
			response=requests.post(
				'http://matzoo.pl/rejestracja',
				data={
					'email1':email,
					'email2':email,
					'password1':password,
					'password2':password,
					'regulamin':'1',
					'zgoda':'1',
					'newsletter':'1',
					'kod':'cztery'
				},
				headers={
					'User-Agent':user_agent
				},
				proxies={
					'http':proxy
				},
				timeout=30
			)
			if b'UDA\xc5\x81O SI\xc4\x98!' in response.content:
				with locks[1]:
					accounts.append('%s\t%s'%(email,password))
				logv('[INFO][%d] Successfully created account'%id)
			else:
				logv('[INFO][%d] Could not create account'%id)
		except (OSError,KeyboardInterrupt):pass
		except:
			exception=format_exc()
			exception_event.set()

if __name__=='__main__':
	try:
		parser=ArgumentParser()
		parser.add_argument('-t','--threads',type=int,help='set number of the threads',default=15)
		parser.add_argument('-p','--proxies',help='set the path to the list with the proxies')
		parser.add_argument('-o','--output',help='set the path of the output file',default='accounts.txt')
		parser.add_argument('-d','--debug',help='show all logs',action='store_true')
		args=parser.parse_args()
		locks=[Lock() for _ in range(2)]
		exception_event=Event()
		proxies=[]
		accounts=[]
		for i in range(args.threads):
			t=Thread(target=bot,args=(i+1,))
			t.daemon=True
			t.start()
		exception_event.wait()
		logv('[ERROR] %s'%exception)
	except KeyboardInterrupt:exit(0)
	except:exit(1)
