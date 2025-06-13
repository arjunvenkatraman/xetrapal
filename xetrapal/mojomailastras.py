#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 00:31:18 2018

@author: ananda
"""
import astra
import sys
sys.path.append("/opt/mojomailman/mojomail")
from mojomailGMail import *


def get_mojogmail(configfile,logger=astra.baselogger):
    """
    Initializes and returns a MojoGMail object for interacting with Gmail.

    Args:
        configfile (str): Path to the configuration file required by MojoGMail.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        MojoGMail: An instance of the MojoGMail class.
    """
    logger.info("Getting a GMail driver")
    m=MojoGMail(configfile=configfile,logger=logger)
    return m
