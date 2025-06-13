#coding: utf-8
'''

'''

#Configparser to load and read our configs
import configparser
#Time to keep time, OS to work with Linux, and Datetime to keep track of dates
import time,os,urllib2,colored
#JSON to store everything
import json
#To get some colored outputs
from pygments import highlight, lexers, formatters

from uuid import uuid4
from .aadhaar import XPAL_WAIT_TIME
import astra




def get_color_json(dictionary,logger=astra.baselogger):
	"""
	Converts a Python dictionary to a colorized JSON string for terminal output.

	Args:
		dictionary (dict): The dictionary to convert.
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

	Returns:
		str: A colorized JSON string.
	"""
	formatted_json=get_formatted_json(dictionary, logger=logger)
	colorful_json = highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
	return colorful_json

def get_formatted_json(dictionary,logger=astra.baselogger):
	"""
	Converts a Python dictionary to a standard, indented JSON string.

	Args:
		dictionary (dict): The dictionary to convert.
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

	Returns:
		str: An indented JSON string.
	"""
	formatted_json=json.dumps(dictionary,sort_keys=True, indent=4)
	return formatted_json

def load_config(configfile,logger=astra.baselogger):
	"""
	Loads a configuration file using configparser.

	Args:
		configfile (str): Path to the configuration file.
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

	Returns:
		configparser.ConfigParser: A ConfigParser object with the loaded configuration.
	"""
	config=configparser.ConfigParser()
	config.read(configfile)
	return config

def get_section(config,sectionname,logger=astra.baselogger):
	"""
	Extracts a specific section from a ConfigParser object into a new ConfigParser object.

	Args:
		config (configparser.ConfigParser): The source ConfigParser object.
		sectionname (str): The name of the section to extract.
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

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
	logger.warning(f"Section '{sectionname}' not found in config.")
	return None
		
def get_jeeva_config(name=None,datapath=None,sessionpathprefix=None,logger=astra.baselogger):
	"""
	Creates a ConfigParser object for a Jeeva instance with default or provided values.

	Args:
		name (str, optional): The name of the Jeeva. Defaults to None.
		datapath (str, optional): The data path for the Jeeva. Required. Defaults to None.
		sessionpathprefix (str, optional): The prefix for session paths.
										   Defaults to "JeevaSession".
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

	Returns:
		configparser.ConfigParser: A ConfigParser object for the Jeeva, or None if datapath is missing.
	"""
	if datapath==None:
		logger.error("Need a datapath")
		return None
	if sessionpathprefix==None:
		sessionpathprefix="JeevaSession"
	configdict={"Jeeva":{"datapath":datapath,"sessionpathprefix":sessionpathprefix}}
	if name!=None:
		configdict['Jeeva']['name']=name
	c=configparser.ConfigParser()
	c.read_dict(configdict)
	return c
	
def load_data_from_json(jsonpath,logger=astra.baselogger):
	"""
	Loads data from a JSON file.

	Args:
		jsonpath (str): Path to the JSON file.
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

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
			logger.error(f"Failed to load JSON file {jsonpath}: {e}")
	else:
		logger.warning(f"JSON file not found: {jsonpath}")
	return data
	
def save_data_to_jsonfile(data,filename=None,path=None,prefix=None,suffix=None,logger=astra.baselogger):
		"""
		Saves Python data (typically a dictionary) to a JSON file.

		Args:
			data (dict): The data to save.
			filename (str, optional): The name of the file. If None, a UUID will be generated.
									 Defaults to None.
			path (str, optional): The directory path to save the file in. Defaults to current directory.
			prefix (str, optional): A prefix to add to the filename. Defaults to None.
			suffix (str, optional): A suffix to add to the filename (e.g., '.json'). Defaults to None.
			logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

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
		try:
			with open(fname,"w") as f:
				f.write(json.dumps(data,indent=4,sort_keys=True))
			logger.info(f"Data saved to JSON file: {fname}")
		except Exception as e:
			logger.error(f"Failed to save data to JSON file {fname}: {e}")
			return None # Or re-raise the exception
		return fname

def download_file(url,path=None,filename=None,prefix=None,suffix=None,logger=astra.baselogger):
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
			logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

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
		fname=os.path.join(path,filename)
		try:
			response = urllib2.urlopen(url)
			data=response.read()
			with open(fname,"wb") as f: # Use "wb" for binary files
				f.write(data)
			logger.info(f"File downloaded successfully: {fname} from {url}")
			return fname
		except Exception as e:
			logger.error(f"Failed to download file from {url} to {fname}: {e}")
			return None
        

def scroll_page(browser,logger=astra.baselogger):
	"""
	Scrolls the given Selenium browser window to the bottom of the current page.

	Args:
		browser: Selenium WebDriver instance.
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
	"""
	logger.info("Scrolling page down.")
	browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	
def scroll_up(browser,logger=astra.baselogger):
	"""
	Scrolls the given Selenium browser window up by a fixed amount (450 pixels).

	Args:
		browser: Selenium WebDriver instance.
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
	"""
	logger.info("Scrolling page up.")
	browser.execute_script("window.scrollTo(0,window.scrollY-450);")
	
def scroll_to_bottom(browser,logger=astra.baselogger):
	"""
	Continuously scrolls the Selenium browser window to the bottom of the page
	until it reliably reaches the end.

	Args:
		browser: Selenium WebDriver instance.
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
	"""
	logger.info("Scrolling to the absolute bottom of the page.")
	ticks_at_bottom = 0
	while True:
		js_scroll_code = "if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {return true;} else {return false;}"
		if browser.execute_script(js_scroll_code):
			if ticks_at_bottom > 1000: # Increased threshold for reliability
				break
			else:
				ticks_at_bottom += 1
				time.sleep(0.01) # Small pause to allow content to load
		else:
			browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			ticks_at_bottom = 0
	logger.info("At bottom of page.")
		
def close_modal(browser,logger=astra.baselogger):
	"""
	Attempts to close a modal dialog in the Selenium browser by clicking a link
	with the text "Close".

	Args:
		browser: Selenium WebDriver instance.
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
	"""
	try:
		logger.info("Attempting to close modal dialog.")
		browser.find_element_by_link_text("Close").click()
		logger.info("Modal dialog closed.")
	except Exception as e:
		logger.warning(f"Could not close modal dialog or modal not found: {e}")
	
def wait(waittime="medium",logger=astra.baselogger):
	"""
	Pauses execution for a predefined duration based on the `waittime` key.
	Durations are fetched from `XPAL_WAIT_TIME` dictionary.

	Args:
		waittime (str, optional): The key for the desired wait duration
								 (e.g., "short", "medium", "long").
								 Defaults to "medium".
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
	"""
	wait_seconds = XPAL_WAIT_TIME.get(waittime, XPAL_WAIT_TIME["medium"]) # Default to medium if key not found
	logger.info("Waiting for a %s duration : %s seconds" %(waittime, wait_seconds))
	time.sleep(wait_seconds)

def save_config(config,filename,logger=astra.baselogger):
		"""
		Saves a ConfigParser object to a file.

		Args:
			config (configparser.ConfigParser): The ConfigParser object to save.
			filename (str): The path to the file where the configuration will be saved.
			logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
		"""
		logger.warning("Saving config file in plain text in file " + colored.stylize(filename,colored.fg("yellow")))
		try:
			with open(filename,"w") as configfile:
				config.write(configfile)
			logger.info(f"Configuration saved to {filename}")
		except Exception as e:
			logger.error(f"Failed to save configuration to {filename}: {e}")

def get_aadesh(msg,func,args=[],kwargs={}):
    """
    Creates an 'aadesh' (command/instruction) dictionary.
    This structure is likely used for queuing or dispatching function calls.

    Args:
        msg (str): A descriptive message for the aadesh.
        func (callable): The function to be executed.
        args (list, optional): A list of positional arguments for the function. Defaults to [].
        kwargs (dict, optional): A dictionary of keyword arguments for the function. Defaults to {}.

    Returns:
        dict: An aadesh dictionary containing the message, function, args, and kwargs.
    """
    aadesh={'msg':msg,'func':func,'args':args,'kwargs':kwargs}
    return aadesh
    
    