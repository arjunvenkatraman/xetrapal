#coding: utf-8
import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
'''
यहां हम फेसबुक सम्बन्धी अस्त्रों का उल्लेख करेंगे 
'''
#from .astra import *
import astra
import karma

#Fire and Forget Astras, to be run with {'msg':'run','func':function_object,'args':(),'kwargs':{}}
def fb_login(browser,fbconfig,logger=astra.baselogger):
		"""
		Logs into Facebook using the provided browser instance and credentials.

		Args:
			browser: Selenium WebDriver instance.
			fbconfig (configparser.ConfigParser): ConfigParser object containing Facebook
												  credentials under the "Facebook" section
												  (fbusername, fbpassword).
			logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
		"""
		fbusr=fbconfig.get("Facebook","fbusername")
		fbpwd=fbconfig.get("Facebook","fbpassword")
		# or you can use Chrome(executable_path="/usr/bin/chromedriver")
		logger.info("Trying to log into FB in browser...")
		try:
			browser.get("http://www.facebook.com")
			assert "Facebook" in browser.title
			elem = browser.find_element_by_id("email")
			elem.send_keys(fbusr)
			elem = browser.find_element_by_id("pass")
			elem.send_keys(fbpwd)
			elem.send_keys(Keys.RETURN)
			time.sleep(10)
			browser.get("http://facebook.com/profile.php")
			time.sleep(10)
			logger.info("Successfully logged into FB")
		except Exception as exception:
			logger.error("Could not log into FB.."+ repr(exception))

def fb_search(fbbrowser,searchstring,logger=astra.baselogger):
		"""
		Performs a search on Facebook using the provided browser instance.

		Args:
			fbbrowser: Selenium WebDriver instance (should be logged into Facebook).
			searchstring (str): The string to search for on Facebook.
			logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
		"""
		logger.info("Searching FB for " + searchstring)
		searchbar=fbbrowser.find_element_by_name("q")
		searchbar.clear()
		searchbar.send_keys(searchstring)
		searchbar.send_keys(Keys.ENTER)
		time.sleep(10) # Consider using explicit waits instead of time.sleep

def fb_get_postlinks_from_timeline(fbbrowser,url="https://facebook.com",count=10,logger=astra.baselogger):
    """
    Retrieves a specified number of post links from a Facebook timeline/page.

    It navigates to the given URL, scrolls down to load posts, and extracts
    the permalinks of the posts.

    Args:
        fbbrowser: Selenium WebDriver instance (should be logged into Facebook).
        url (str, optional): The URL of the Facebook page/timeline to scrape.
                             Defaults to "https://facebook.com".
        count (int, optional): The desired number of post links to retrieve.
                               Defaults to 10.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        list: A list of unique post permalinks (strings), up to the specified count.
    """
    fbbrowser.get(url)
    karma.wait()
    postlinks=[]
    
    while len(postlinks)<count:
        posts=[]
        postcontents=[]
        posts=posts+fbbrowser.find_elements_by_class_name("userContentWrapper")
        for post in posts:
            postcontents.append(BeautifulSoup(post.get_property("innerHTML")))
        for postcontent in postcontents:
           
            pc=list(postcontent.find_all("a",{"class":"_5pcq"}))
            if len(pc)>0:
                pc=pc[0]
            else:
                continue
            url="https://facebook.com"+pc.get("href")    
            postlinks.append(url)
        logger.info("Got %s posts " %(len(postlinks)))
        postlinks=list(set(postlinks))
        if "https://facebook.com#" in postlinks:
            postlinks.pop(postlinks.index("https://facebook.com#"))
        karma.scroll_page(fbbrowser)
        karma.wait()
    return postlinks[:count]