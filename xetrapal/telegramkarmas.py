"""
Created on Wed Jun  6 00:31:18 2018

@author: ananda
"""

import astra,karma,os
import sys
import telegram

def poll(botname,botstop):
    """
    Continuously polls for new Telegram updates for the given bot.

    This function runs in a loop, periodically calling `botname.get_latest_updates()`.
    If updates are received, they are processed by `botname.updater.dispatcher.process_update()`.
    The loop can be stopped by creating a file specified by the `botstop` path.

    Args:
        botname (XetrapalTelegramBot): An instance of the XetrapalTelegramBot class (or a similar
                                     class with `logger`, `name`, `get_latest_updates`, and
                                     `updater.dispatcher.process_update` attributes/methods).
        botstop (str): Path to a "stop file". If this file exists, the polling loop will terminate.
    """
    while True:
        if not os.path.exists(botstop):
            botname.logger.info(u"{} waiting for messages. Touch {} to stop".format(botname.name,botstop))
            karma.wait(waittime="medium",logger=botname.logger) # Consider making wait time configurable
            try:
                updates = botname.get_latest_updates()
                botname.logger.info(u"{} got {} messages".format(botname.name,len(updates)))
                if len(updates)>0:
                    for update in updates:
                        botname.updater.dispatcher.process_update(update)
                        # If direct parsing and handling is needed uncomment below:
                        # messageparser(botname, update, handler_function, logger=botname.logger)
            except Exception as e:
                botname.logger.warning("Error during polling or processing updates: {}".format(repr(e)))
        else:
            botname.logger.info(u"Stopfile {} found, {} exiting bot update loop".format(botstop, botname.name))
            break

def messageparser(bot,update,handler=None,logger=astra.baselogger):
    """
    Parses a Telegram update object to extract common message components.

    It can handle both regular messages and callback queries.
    Extracted information includes:
    - `source_message`: The text of the message being replied to (if any).
    - `response`: The text of the current message or callback data.
    - `location`: Location data (as JSON string) if present in the message.
    - `reply_id`: The chat ID to which a reply should be sent.

    If a `handler` function is provided, it is called with the bot, original update,
    the parsed update dictionary, and the logger. Otherwise, the parsed dictionary is returned.

    Args:
        bot (telegram.Bot): The Telegram Bot instance.
        update (telegram.Update): The update object received from Telegram.
        handler (callable, optional): A function to call with the parsed data.
                                      It should accept (bot, update, parsed_update, logger).
                                      Defaults to None.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        dict or None: A dictionary with parsed update information if no handler is provided.
                      Returns None if a handler is provided and executed.
                      Returns None if the update type is neither a message nor a callback query.
    """
    source_message = None
    response = None
    location = None
    reply_id = None

    if update.message:
        logger.info(u"Parsing a direct message.")
        reply_id = update.message.chat_id
        if update.message.reply_to_message:
            source_message = update.message.reply_to_message.text

        if update.message.text:
            response = update.message.text

        if update.message.location:
            location = update.message.location.to_json()

        logger.info(u"Parsed Direct Message - ID: {}\nSource Message: {}\nResponse: {}\nLocation: {}".format(reply_id,source_message,response,location))

    elif update.callback_query:
        logger.info(u"Parsing a callback query.")
        reply_id = update.callback_query.message.chat_id
        source_message = update.callback_query.message.text # Text of the message the button was attached to
        response = update.callback_query.data # Data from the button
        # Location is not typically part of a callback_query itself
        logger.info(u"Parsed Callback Query - ID: {}\nSource Message: {}\nResponse: {}\nLocation: {}".format(reply_id, source_message,response,location))

    else:
        logger.info(u"Update type not recognized for direct parsing (not a message or callback query).")
        return None

    parsed_update={"source_message":source_message,"response":response,"location":location,"reply_id":reply_id}

    if handler is not None and callable(handler):
        try:
            handler(bot,update,parsed_update,logger)
        except Exception as e:
            logger.error(f"Error in provided handler function: {e}")
        return None # Assuming handler manages further actions
    else:
        return parsed_update