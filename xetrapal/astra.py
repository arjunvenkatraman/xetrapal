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
	"""
	Converts a Python dictionary to a colorized JSON string for terminal output.

	Args:
		dictionary (dict): The dictionary to convert.

	Returns:
		str: A colorized JSON string.
	"""
	formatted_json=get_formatted_json(dictionary)
	colorful_json = highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
	return colorful_json

def get_formatted_json(dictionary):
	"""
	Converts a Python dictionary to a standard, indented JSON string.

	Args:
		dictionary (dict): The dictionary to convert.

	Returns:
		str: An indented JSON string.
	"""
	formatted_json=json.dumps(dictionary,sort_keys=True, indent=4)
	return formatted_json

def load_config(configfile):
	"""
	Loads a configuration file using configparser.

	Args:
		configfile (str): Path to the configuration file.

	Returns:
		configparser.ConfigParser: A ConfigParser object with the loaded configuration.
	"""
	config=configparser.ConfigParser()
	config.read(configfile)
	return config

def get_section(config,sectionname):
	"""
	Extracts a specific section from a ConfigParser object into a new ConfigParser object.

	Args:
		config (configparser.ConfigParser): The source ConfigParser object.
		sectionname (str): The name of the section to extract.

	Returns:
		configparser.ConfigParser: A new ConfigParser object containing only the specified section,
									or None if the section doesn't exist.
	"""
	if config.has_section(sectionname):
		p=config[sectionname]
		c=configparser.ConfigParser()
		a={sectionname:dict(p)}
		c.read_dict(a)
		return c
	return None # Added return for clarity if section not found
		
def get_jeeva_config(name=None,datapath=None,sessionpathprefix=None):
	"""
	Creates a ConfigParser object for a Jeeva instance with default or provided values.

	Args:
		name (str, optional): The name of the Jeeva. Defaults to None.
		datapath (str, optional): The data path for the Jeeva. Required. Defaults to None.
		sessionpathprefix (str, optional): The prefix for session paths.
										   Defaults to "JeevaSession".

	Returns:
		configparser.ConfigParser: A ConfigParser object for the Jeeva, or None if datapath is missing.
	"""
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
	"""
	Loads data from a JSON file.

	Args:
		jsonpath (str): Path to the JSON file.

	Returns:
		dict: The data loaded from the JSON file, or an empty dictionary if the file
			  doesn't exist or an error occurs during loading.
	"""
	data={}
	if os.path.exists(jsonpath):
		try:
	
			with open(jsonpath) as f:
				data=json.load(f)
		except Exception as e:
			print "Failed to load file because" + str(e) # Consider logging instead of printing
	return data
	
def save_data_to_jsonfile(data,filename=None,path=None,prefix=None,suffix=None):
		"""
		Saves Python data (typically a dictionary) to a JSON file.

		Args:
			data (dict): The data to save.
			filename (str, optional): The name of the file. If None, a UUID will be generated.
									 Defaults to None.
			path (str, optional): The directory path to save the file in. Defaults to current directory.
			prefix (str, optional): A prefix to add to the filename. Defaults to None.
			suffix (str, optional): A suffix to add to the filename (e.g., '.json'). Defaults to None.

		Returns:
			str: The full path to the saved JSON file.
		"""
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
		"""
		Downloads a file from a given URL.

		Args:
			url (str): The URL of the file to download.
			path (str, optional): The directory path to save the downloaded file.
								 Defaults to the current directory (".").
			filename (str, optional): The name to save the file as. If None, a UUID will be generated.
									 Defaults to None.
			prefix (str, optional): A prefix to add to the filename. Defaults to None.
			suffix (str, optional): A suffix to add to the filename. Defaults to None.

		Returns:
			str: The full path to the downloaded file, or None if the download fails.
		"""
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
		except Exception as e: # Catch specific exception if possible
			baselogger.error(f"Failed to download {url}: {e}")
			return None

#Getting a logger which keeps track of things on console
def get_xpal_logger(name):
	"""
	Creates and configures a colored logger for console output.

	Args:
		name (str): The name of the logger.

	Returns:
		logging.Logger: A configured logger instance.
	"""
	xpallogger=logging.getLogger(name)
	coloredlogs.install(level="INFO",logger=xpallogger,fmt=XPAL_CONSOLE_FORMAT,level_styles=XPAL_LEVEL_STYLES,field_styles=XPAL_FIELD_STYLES)
	return xpallogger

baselogger=get_xpal_logger("Xpal-Sutradhar")

#Getting a browser that lets us do browser based tasks
def get_browser(headless=False,logger=baselogger):
	"""
	Initializes and returns a Selenium Firefox WebDriver instance.

	Args:
		headless (bool, optional): Whether to run Firefox in headless mode.
									Defaults to False.
		logger (logging.Logger, optional): The logger instance to use for messages.
										   Defaults to `baselogger`.

	Returns:
		selenium.webdriver.firefox.webdriver.WebDriver: A Firefox WebDriver instance.
	"""
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
