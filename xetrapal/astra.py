#coding: utf-8
#from .karma import *
#for colored logs
import coloredlogs, logging
#For google sheets
DEBUG=False
#For twitter
import os
#For youtube 
#Selenium to automate browser work
from selenium import webdriver
from pygments import highlight, lexers, formatters
#from selenium.webdriver.common.action_chains import ActionChains
#BeautifulSoup to make sense of what we got
#from BeautifulSoup import BeautifulSoup
import json
import configparser
#To make copies of files
#from shutil import copyfile
from uuid import uuid4
import urllib2 #time,os
#Getting our basics
from .aadhaar import  XPAL_CONSOLE_FORMAT,XPAL_LEVEL_STYLES,XPAL_FIELD_STYLES



def get_color_json(dictionary):
	formatted_json=get_formatted_json(dictionary)
	colorful_json = highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
	return colorful_json

def get_formatted_json(dictionary):
	formatted_json=json.dumps(dictionary,sort_keys=True, indent=4)
	return formatted_json

def load_config(configfile):
	config=configparser.ConfigParser()
	config.read(configfile)
	return config

def get_section(config,sectionname):
	if config.has_section(sectionname):
		p=config[sectionname]
		c=configparser.ConfigParser()
		a={sectionname:dict(p)}
		c.read_dict(a)
		return c
		
def get_jeeva_config(name=None,datapath=None,sessionpathprefix=None):
	if datapath==None:
		baselogger.error("Need a datapath")
		return None
	if sessionpathprefix==None:
		sessionpathprefix="JeevaSession"
	configdict={"Jeeva":{"datapath":datapath,"sessionpathprefix":sessionpathprefix}}
	if name!=None:
		configdict['Jeeva']['name']=name
	c=configparser.ConfigParser()
	c.read_dict(configdict)
	return c
def load_data_from_json(jsonpath):
	data={}
	if os.path.exists(jsonpath):
		try:
	
			with open(jsonpath) as f:
				data=json.load(f)
		except Exception as e:
			print "Failed to load file because" + str(e)
	return data
	
def save_data_to_jsonfile(data,filename=None,path=None,prefix=None,suffix=None):
		if path==None:
			path=""
		if filename==None:
			filename=str(uuid4())
		if prefix != None:
			filename=prefix+filename
		if suffix != None:
			filename=filename+suffix
		fname=os.path.join(path,filename)
		with open(fname,"w") as f:
			f.write(json.dumps(data,indent=4,sort_keys=True))
		return fname

def download_file(url,path=None,filename=None,prefix=None,suffix=None):
		if path==None:
			path="."
		if filename==None:
			filename=str(uuid4())
		if prefix != None:
			filename=prefix+filename
		if suffix != None:
			filename=filename+suffix
		try:
			response = urllib2.urlopen(url)
			data=response.read()
			fname=os.path.join(path,filename)
			f=open(fname,"w")
			f.write(data)
			f.close()
			
			return fname
		except:
			return None

#Getting a logger which keeps track of things on console
def get_xpal_logger(name):
	xpallogger=logging.getLogger(name)
	coloredlogs.install(level="INFO",logger=xpallogger,fmt=XPAL_CONSOLE_FORMAT,level_styles=XPAL_LEVEL_STYLES,field_styles=XPAL_FIELD_STYLES)
	return xpallogger

baselogger=get_xpal_logger("Xpal-Sutradhar")

#Getting a browser that lets us do browser based tasks
def get_browser(headless=False,logger=baselogger):
	logger.info("Launching a browser....")
	if headless==True:
		logger.info("...which has no head")
		os.environ['MOZ_HEADLESS'] = '1'
	
	firefox_profile = webdriver.FirefoxProfile()
	firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
	#firefox_profile.set_preference("browser.download.dir", self.sessiondownloadpath);
	firefox_profile.set_preference("browser.download.folderList", 2);
	firefox_profile.set_preference("browser.download.manager.showWhenStarting", False);
	firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain, text/csv",)
	driver = webdriver.Firefox(firefox_profile=firefox_profile)
	return driver
