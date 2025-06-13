#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 00:31:18 2018

@author: ananda
"""
import astra
import pygsheets
#Get a pygsheet to work with Google sheets
def get_googledriver(config,logger=astra.baselogger):
	"""
	Authorizes and returns a pygsheets client to interact with Google Sheets.

	Args:
		config (configparser.ConfigParser): ConfigParser object with a "Pygsheets" section
											containing 'outhfile' (path to OAuth 2.0 client secrets file)
											and 'outhstore' (path to store OAuth credentials).
		logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

	Returns:
		pygsheets.client.Client: A pygsheets client instance if authorization is successful,
								 otherwise None.
	"""
	logger.info("Trying to log into Google drive")
	try:
		gd=pygsheets.authorize(outh_file=config.get("Pygsheets",'outhfile'),outh_nonlocal=True,outh_creds_store=config.get("Pygsheets",'outhstore'))
		return gd
	except Exception as e:
		logger.error("Could not get google driver config because %s" %str(e))
		return None
