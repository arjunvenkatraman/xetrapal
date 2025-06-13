#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 00:25:58 2018

@author: ananda
"""

import twython
import astra
import colored
import json
import os
from datetime import datetime
import tweepy

class XpalTwitterStreamer(twython.TwythonStreamer):
    """
    A custom TwythonStreamer that buffers incoming Twitter data and periodically
    flushes it to a JSON file.

    Attributes:
        ofile (str): Path to the output JSON file where streamed data is stored.
        buffer (list): A list to temporarily hold incoming tweet data.
        logger (logging.Logger): Logger instance for logging messages.
    """
    def __init__(self,ofile,logger,*args, **kwargs):
        """
        Initializes the XpalTwitterStreamer.

        Args:
            ofile (str): Path to the output JSON file.
            logger (logging.Logger): Logger instance.
            *args: Positional arguments to pass to the TwythonStreamer parent class.
            **kwargs: Keyword arguments to pass to the TwythonStreamer parent class.
                      These typically include Twitter API credentials.
        """
        super(XpalTwitterStreamer,self).__init__(*args, **kwargs)
        self.ofile=ofile
        self.buffer=[]
        self.logger=logger
    def flush_buffer(self):
        """
        Appends the contents of the internal buffer to the output JSON file.
        If the output file exists, its contents are loaded, new data is appended,
        and the file is overwritten. If it doesn't exist, a new file is created.
        The buffer is cleared after flushing.
        """
        ofilejson=[]
        try:
            if os.path.exists(self.ofile):
                with open(self.ofile,"r") as f:
                    content = f.read()
                    if content: # Ensure content is not empty
                        ofilejson=json.loads(content)
            ofilejson+=self.buffer
            with open(self.ofile,"w") as f:
                f.write(json.dumps(ofilejson, indent=4)) # Added indent for readability
            self.buffer=[]
            self.logger.info(f"Flushed tweet buffer to {self.ofile}")
        except (IOError, ValueError) as e:
            self.logger.error(f"Error flushing buffer to {self.ofile}: {e}")

    def on_success(self, data):
        """
        Called when a new piece of data (usually a tweet) is successfully received
        from the Twitter stream. The data is added to the buffer. If the buffer size
        exceeds 10 items, `flush_buffer` is called.

        Args:
            data (dict): The tweet data received from Twitter.
        """
        #self.logger.info(data) # Can be verbose
        self.buffer.append(data)
        if len(self.buffer)>10: # Consider making buffer size configurable
            self.flush_buffer()
    def on_error(self, status_code, data):
        """
        Called when an error occurs in the stream. Logs the status code.

        Args:
            status_code (int): The HTTP status code of the error.
            data: The data associated with the error.
        """
        self.logger.error(f"Twitter stream error: {status_code}, Data: {data}")
		# print(status_code) # Original print statement


        # Want to stop trying to get data because of the error?
        # Uncomment the next line!
        # self.disconnect()

class XpalTwitterSheeter(XpalTwitterStreamer):
    """
    (Incomplete/Placeholder) A class intended to extend XpalTwitterStreamer,
    possibly to stream Twitter data directly into a spreadsheet.
    The `__init__` method is incomplete.
    """
    def __init__(self,sheetname,logger,*args, **kwargs):
        """
        Initializes the XpalTwitterSheeter. (Currently incomplete)

        Args:
            sheetname (str): The name of the target spreadsheet.
            logger (logging.Logger): Logger instance.
            *args: Arguments for the parent class.
            **kwargs: Keyword arguments for the parent class.
        """
        super(XpalTwitterStreamer,self).__init__(*args, **kwargs) # Should be XpalTwitterSheeter
        self.logger = logger
        self.sheetname = sheetname
        self.logger.info(f"XpalTwitterSheeter initialized for sheet: {sheetname}")
        #self. # Remainder of initialization is missing
def get_twython_streamer(config,ofilename=None,logger=astra.baselogger):
    """
    Creates and returns an instance of XpalTwitterStreamer.

    Args:
        config (configparser.ConfigParser): ConfigParser object with a "Twython" section
                                            containing Twitter API credentials
                                            (app_key, app_secret, oauth_token, oauth_token_secret).
        ofilename (str, optional): Path to the output JSON file for storing streamed tweets.
                                   If None, a default filename with a timestamp is generated
                                   in "/tmp/". Defaults to None.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        XpalTwitterStreamer: An initialized XpalTwitterStreamer instance, or None on error.
    """
    
    if ofilename==None:
        ts=datetime.now()
        ofilename="/tmp/TwythonStreamer-"+ts.strftime("%Y%b%d-%H%M%S"+".json")
    logger.info("Trying to get a twython streamer to work with twitter streams")
    try:
        app_key=config.get("Twython",'app_key')
        app_secret=config.get("Twython",'app_secret')
        oauth_token=config.get("Twython",'oauth_token')
        oauth_token_secret=config.get("Twython",'oauth_token_secret')
    except configparser.NoSectionError:
        logger.error("Config section 'Twython' not found.")
        return None
    except configparser.NoOptionError as e:
        logger.error(f"Missing option in 'Twython' config section: {e}")
        return None

    try:
        t=XpalTwitterStreamer(ofilename,logger,app_key,app_secret,oauth_token,oauth_token_secret)
        logger.info("Streamer logging at "  + colored.stylize(t.ofile,colored.fg("yellow")))
        return t
    except Exception as e:
        logger.error("Could not get twython streamer because %s" %repr(e))
        return None

#Get a Twython to work with twitter
def get_twython(config,logger=astra.baselogger):
    """
    Creates and returns a Twython instance for general Twitter API interaction.

    Args:
        config (configparser.ConfigParser): ConfigParser object with a "Twython" section
                                            containing Twitter API credentials.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        twython.Twython: An initialized Twython instance, or None on error.
    """
    logger.info("Trying to get a twython to work with twitter")
    try:
        app_key=config.get("Twython",'app_key')
        app_secret=config.get("Twython",'app_secret')
        oauth_token=config.get("Twython",'oauth_token')
        oauth_token_secret=config.get("Twython",'oauth_token_secret')
    except configparser.NoSectionError:
        logger.error("Config section 'Twython' not found.")
        return None
    except configparser.NoOptionError as e:
        logger.error(f"Missing option in 'Twython' config section: {e}")
        return None

    try:
        t=twython.Twython(app_key,app_secret,oauth_token,oauth_token_secret)
        return t
    except Exception as e:
        logger.error("Could not get twython config because %s" %repr(e))
        return None

def get_tweepy(twconfig,logger=astra.baselogger):
    """
    Creates and returns a Tweepy API instance.

    Args:
        twconfig (configparser.ConfigParser): ConfigParser object with a "Twython" section
                                              (note: uses "Twython" section, might be a typo
                                              and should be "Tweepy" or a generic Twitter section)
                                              containing API credentials.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        tweepy.API: An initialized Tweepy API instance, or None on error.
    """
    logger.info("Trying to get a tweepy to work with twitter")
    try:
        # Assuming "Twython" section is used for Tweepy as per original code
        app_key=twconfig.get("Twython",'app_key')
        app_secret=twconfig.get("Twython",'app_secret')
        oauth_token=twconfig.get("Twython",'oauth_token')
        oauth_token_secret=twconfig.get("Twython",'oauth_token_secret')
    except configparser.NoSectionError:
        logger.error("Config section 'Twython' (for Tweepy) not found.")
        return None
    except configparser.NoOptionError as e:
        logger.error(f"Missing option in 'Twython' (for Tweepy) config section: {e}")
        return None

    auth=tweepy.OAuthHandler(app_key,app_secret)
    auth.set_access_token(oauth_token,oauth_token_secret)
    try:
        tweep=tweepy.API(auth)
        logger.info("Tweepy API instance created successfully.")
        return tweep
    except Exception as e:
        logger.error("Could not get a tweepy because %s" %repr(e))
        return None # Added return None for clarity on failure
        
