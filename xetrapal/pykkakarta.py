#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 12:19:01 2018

@author: anandabhairav
"""


import pykka
class Karta(pykka.ThreadingActor):
    """
    A Pykka ThreadingActor named Karta (meaning "doer" or "agent").
    This actor is designed to execute functions asynchronously based on messages it receives.
    It is associated with a 'Jeeva' instance, using its logger.

    Messages are expected to be dictionaries, typically with:
    - 'msg': "run" (for fire-and-forget execution) or "get" (for execution that returns a value).
    - 'func': The function object to execute.
    - 'args': A list or tuple of positional arguments for the function.
    - 'kwargs': A dictionary of keyword arguments for the function.
    """
    def __init__(self,jeeva):
        """
        Initializes the Karta actor.

        Args:
            jeeva: An instance of a Jeeva-like class, which must have a `logger` attribute.
        """
        super(Karta,self).__init__()
        #threading.Thread.__init__(self)
        self.jeeva = jeeva
        self.jeeva.logger.info("Karta initialized....")
    def on_start(self):
        """
        Called when the actor is started. Logs a message.
        """
        self.jeeva.logger.info("Karta started")
        
    def on_receive(self,message):
        """
        Handles incoming messages to the actor.

        If `message['msg']` is "run", it executes `message['func']` with
        `message['args']` and `message['kwargs']`. Exceptions during execution are logged.

        If `message['msg']` is "get", it executes `message['func']` and attempts
        to return its result. If an exception occurs, a string representation of
        the exception is returned.

        Args:
            message (dict): The message dictionary containing details of the task.

        Returns:
            The result of the function if `message['msg']` is "get" and execution is successful.
            A string representation of an exception if `message['msg']` is "get" and an error occurs.
            None otherwise (for "run" messages or if an unexpected message type is received).
        """
        self.jeeva.logger.info("Received message " + str(message))
        if not isinstance(message, dict):
            self.jeeva.logger.warning(f"Received non-dict message: {message}")
            return

        msg_type = message.get('msg')
        func_to_run = message.get('func')
        args = message.get('args', [])
        kwargs = message.get('kwargs', {})

        if not callable(func_to_run):
            self.jeeva.logger.error(f"No valid function provided in message: {message}")
            if msg_type == "get":
                return "Error: No valid function provided."
            return

        if msg_type =="run":
            self.jeeva.logger.info("Trying to run " + str(func_to_run))
            try:
                func_to_run(*args,**kwargs)
            except Exception as e:
                self.jeeva.logger.error(f"Error running {func_to_run}: {repr(e)}")
        elif msg_type =="get":
            self.jeeva.logger.info("Trying to get a return value from " + str(func_to_run))
            try:
                returnvalue=func_to_run(*args,**kwargs)
                return returnvalue
            except Exception as e:
                self.jeeva.logger.error(f"Error getting value from {func_to_run}: {repr(e)}")
                return repr(e)
        else:
            self.jeeva.logger.warning(f"Unknown message type '{msg_type}' in message: {message}")