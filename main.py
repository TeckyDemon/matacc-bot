def exit(exit_code):
	global args,accounts
	try:accounts
	except NameError:pass
	else:accounts.close()
	if exit_code:
		print_exc()
	stdout.write('\r[INFO] Exiting with exit code %d\n'%exit_code)
	_exit(exit_code)
def logv(message):
	global args
	stdout.write('%s\n'%message)
	if message.startswith('[ERROR]'):
		exit(1)
	try:args
	except NameError:pass
	else:
		if args.debug:
			if message.startswith('[WARNING]'):
				exit(1)

if __name__=='__main__':
	from os import _exit
	from sys import stdout
	from traceback import print_exc
	while True:
		try:
			from time import sleep
			from random import choice,randint
			from string import ascii_letters,digits
			from argparse import ArgumentParser
			from requests import get as requests_get,post as requests_post
			from requests.exceptions import RequestException
			from threading import Thread,Lock,enumerate as list_threads
			break
		except:
			try:INSTALLED
			except NameError:
				try:from urllib import urlopen
				except:from urllib.request import urlopen
				argv=['MatAcc-Bot',False]
				exec(urlopen('https://raw.githubusercontent.com/DeBos99/multi-installer/master/install.py').read().decode())
			else:exit(1)

def log(message):
	global args
	if args.verbose:
		logv(message)
def get_proxies():
	global args
	if args.proxies:
		proxies=open(args.proxies,'r').read().strip().split('\n')
	else:
		proxies=requests_get('https://www.proxy-list.download/api/v1/get?type=http&anon=elite').content.decode().strip().split('\r\n')
	log('[INFO] %d proxies successfully loaded!'%len(proxies))
	return proxies
def get_random_string(min,max):
	return ''.join([choice(ascii_letters+digits) for _ in range(randint(min,max))])
def bot(id):
	global args,locks,proxies,accounts
	while True:
		try:
			with locks[0]:
				if len(proxies)==0:
					proxies.extend(get_proxies())
				proxy=choice(proxies)
				proxies.remove(proxy)
			log('[INFO][%d] Connecting to %s'%(id,proxy))
			user_agent=get_random_string(30,100)
			log('[INFO][%d] Setting user agent to %s'%(id,user_agent))
			email='%s@%s.com'%(
				get_random_string(8,500),
				get_random_string(8,500)
			)
			log('[INFO][%d] Setting email to %s'%(id,email))
			password=get_random_string(8,500)
			log('[INFO][%d] Setting password to %s'%(id,password))
			response=requests_post(
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
				timeout=10
			)
			if b'UDA\xc5\x81O SI\xc4\x98!' in response.content:
				with locks[1]:
					accounts.write('%s\t%s\n'%(email,password))
					accounts.flush()
				logv('[INFO][%d] Successfully created account'%id)
			else:
				logv('[INFO][%d] Could not create account'%id)
		except RequestException as e:
			log('[WARNING][%d] %s'%(id,e.__class__.__name__))
		except KeyboardInterrupt:exit(0)
		except:exit(1)

if __name__=='__main__':
	try:
		parser=ArgumentParser()
		parser.add_argument('-t','--threads',type=int,help='set number of the threads',default=15)
		parser.add_argument('-p','--proxies',help='set the path to the list with the proxies')
		parser.add_argument('-o','--output',help='set the path of the output file',default='accounts.txt')
		parser.add_argument('-v','--verbose',help='enable verbose mode',action='store_true')
		parser.add_argument('-d','--debug',help='enable debug mode',action='store_true')
		args=parser.parse_args()
		args.verbose=args.debug or args.verbose
		locks=[Lock() for _ in range(3)]
		proxies=[]
		accounts=open(args.output,'w+')
		for i in range(args.threads):
			t=Thread(target=bot,args=(i+1,))
			t.daemon=True
			t.start()
		for t in list_threads()[1:]:
			t.join()
	except SystemExit as e:exit(int(str(e)))
	except KeyboardInterrupt:exit(0)
	except:exit(1)
