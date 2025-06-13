#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 00:31:18 2018

@author: ananda
"""

import astra
import sys,os,json
import pandas
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, CommandHandler
import karma
class XetrapalTelegramBot:
    """
    A class to manage interactions with a Telegram Bot.
    It handles updating the bot's state (offset and known users),
    saving/loading this state to a file, and fetching the latest messages.

    Attributes:
        name (str): The name of the bot, retrieved from configuration.
        statefile (str): Path to the JSON file used to store the bot's state.
        logger (logging.Logger): Logger instance for logging messages.
        updater (telegram.ext.Updater): The Updater instance for the bot.
        state (dict): In-memory dictionary holding the bot's state (offset, users).
        offset (int): The offset for `get_updates` to avoid processing old messages.
        users (list): A list of user dictionaries for users who have interacted with the bot.
    """
    def __init__(self,config,logger=astra.baselogger):
        """
        Initializes the XetrapalTelegramBot.

        Args:
            config (configparser.ConfigParser): A ConfigParser object with a "TelegramBot"
                                                section containing 'name', 'statefile',
                                                and 'tokenfile' keys.
            logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
        """
        self.name=config.get("TelegramBot","name")
        self.statefile=config.get("TelegramBot","statefile")
        self.logger=logger
        tokenfile=config.get("TelegramBot","tokenfile")
        with open(tokenfile,"r") as f:
            token=f.read().strip()
        self.updater=Updater(token)
        self.load_state()
        if self.state=={}:
            self.users=[]
            self.offset=0
            self.save_state()


    def save_state(self):
        """
        Saves the current bot state (offset and users) to the state file.
        The state is saved as a JSON object.
        """
        self.state['offset']=self.offset
        self.state['users']=self.users
        try:
            with open(self.statefile,"w") as f:
                f.write(json.dumps(self.state, indent=4)) # Added indent for readability
            self.logger.info(f"Bot state saved to {self.statefile}")
        except IOError as e:
            self.logger.error(f"Could not save bot state to {self.statefile}: {e}")

    def load_state(self):
        """
        Loads the bot state (offset and users) from the state file.
        If the state file does not exist, an empty state is initialized.
        """
        if os.path.exists(self.statefile):
            try:
                with open(self.statefile,"r") as f:
                    self.state=json.loads(f.read().strip())
                self.offset=int(self.state.get('offset', 0)) # Use .get for safety
                self.users=self.state.get('users', [])     # Use .get for safety
                self.logger.info(f"Bot state loaded from {self.statefile}")
            except (IOError, ValueError, KeyError) as e: # Catch more specific errors
                self.logger.error(f"Could not load or parse bot state from {self.statefile}: {e}. Initializing empty state.")
                self.state={}
                self.offset = 0
                self.users = []
        else:
            self.logger.info(f"State file {self.statefile} not found. Initializing empty state.")
            self.state={}
            self.offset = 0
            self.users = []


    def get_latest_updates(self):
        """
        Fetches the latest updates (messages, callback queries) for the bot.

        It uses the current `self.offset` to get only new updates.
        If new messages are received, it logs them and updates the list of known users.
        The `self.offset` is updated to the `update_id` of the last processed message plus one.
        The new state (offset and users) is then saved.

        Returns:
            list: A list of `telegram.Update` objects, or an empty list if no new updates.
        """
        self.logger.info("Trying to get latest updates for bot "+self.name)
        try:
            p=self.updater.bot.get_updates(offset=self.offset)
        except Exception as e:
            self.logger.error(f"Error getting updates from Telegram: {e}")
            return []

        if len(p)>0:
            for update in p:
                self.logger.info(u"Got message {}".format(update.to_json()))
                
                uids = [user['id'] for user in self.users]
                if update.message!=None:
                    if update.message.from_user.id not in uids:
                        self.logger.info("Adding user to user list")
                        self.users.append(json.loads(update.message.from_user.to_json()))
                    else:
                        self.logger.info("User in list already")
                else:
                    if update.callback_query:
                        self.logger.info("Callback query received")
                    else:
                        self.logger.info("Special Message")
            self.offset=p[-1].update_id+1
            self.save_state()
        else:
            self.logger.info("No new messages received for bot " + self.name)
        return p
