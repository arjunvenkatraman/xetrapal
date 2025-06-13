 #coding: utf-8

import astra
import karma
import jeeva
import fbkarmas
import twkarmas
import colored
import twastras
import gdastras
import gdkarmas
import pykkakarta
import os
#import mojomailastras
import telegramastras
import telegramkarmas
#import thespiankarta

class Xetrapal(jeeva.Jeeva):
    """
    Xetrapal is the main class representing the bot/agent.
    It inherits from Jeeva and manages various 'astras' (tools/APIs)
    and 'vaahans' (transport mechanisms/platforms).

    Key responsibilities:
    - Initializing and managing its profile and configurations.
    - Adding, removing, and updating astras (e.g., Twitter API, Google Drive API).
    - Adding and releasing vaahans.
    - Interacting with various services like Twitter, Facebook, Google Drive.
    - Starting and managing 'kartas' (actors/workers) for asynchronous tasks.
    """
    def __init__(self,*args, **kwargs):
        """
        Initializes the Xetrapal instance.

        Args:
            *args: Variable length argument list passed to the parent Jeeva class.
            **kwargs: Arbitrary keyword arguments passed to the parent Jeeva class.
        """
        super(Xetrapal,self).__init__(*args, **kwargs)
        self.vaahans={}
        self.astras={}
        self.update_astras()
        self.update_vaahans()
        self.save_profile()
    def update_astras(self):
        """
        Updates the 'astras' (tools/APIs) list in the Xetrapal's profile.
        This method serializes the types of currently loaded astras and saves them.
        """
        self.logger.info("Trying to update astras")
        astras={}
        if self.astras=={}:
            self.logger.warning("I dont seem to have any astras")
        else:
            for astraname in self.astras.keys():
                astras[astraname]=str(type(self.astras[astraname]))

        self.set_property("astras",astras)
        self.save_profile()

    def update_vaahans(self):
        """
        Updates the 'vaahans' (transport mechanisms) list in the Xetrapal's profile.
        This method serializes the types of currently loaded vaahans and saves them.
        """
        self.logger.info("Trying to update vaahans")
        vaahans={}
        if self.vaahans=={}:
            self.logger.warning("I dont seem to have any vaahans")
        else:
            for vaahanname in self.vaahans.keys():
                vaahans[vaahanname]=str(type(self.vaahans[vaahanname]))

        self.set_property("vaahans",vaahans)
        self.save_profile()


    def add_vaahan(self,vaahan):
        """
        Adds a 'vaahan' (transport mechanism) to Xetrapal.

        Args:
            vaahan: The vaahan object to add. It should have a 'name' attribute.
        """
        self.vaahans[vaahan.name]=vaahan
        self.update_vaahans()

    def release_vaahan(self,vaahanname):
        """
        Removes and returns a 'vaahan' from Xetrapal.

        Args:
            vaahanname (str): The name of the vaahan to release.

        Returns:
            The vaahan object that was removed, or None if not found.
        """
        self.logger.info("Releasing vaahan " + colored.stylize(vaahanname,colored.fg("violet")))
        vaahan=self.vaahans.pop(vaahanname)
        self.update_vaahans()
        return vaahan


    def add_astra(self,astraname,newastra):
        """
        Adds an 'astra' (tool/API) to Xetrapal.

        Args:
            astraname (str): The name to assign to this astra.
            newastra: The astra object to add.
        """
        self.astras[astraname]=newastra
        self.update_astras()

    def drop_astra(self,astraname):
        """
        Removes and returns an 'astra' from Xetrapal.

        Args:
            astraname (str): The name of the astra to drop.

        Returns:
            The astra object that was removed, or None if not found.
        """
        self.logger.info("Dropping astra " + colored.stylize(astraname,colored.fg("violet")))
        droppedastra=self.astras.pop(astraname)
        self.update_astras()
        return droppedastra
    def start_pykka_karta(self):
        """
        Starts a new Pykka-based 'karta' (actor/worker).
        Kartas are used for running tasks asynchronously.

        Returns:
            A reference to the started Pykka Karta actor.
        """
        kartaref=pykkakarta.Karta.start(jeeva=self)
        self.kartarefs.append(kartaref)
        return kartaref
   # def start_thespian_karta(self):
   #     kartaref=thespiankarta.vidhata.createActor(thespiankarta.Karta)
   #     self.kararefs.append(kartaref)
   #     return kartaref
    def get_fb_browser(self,fbconfig=None):
        """
        Initializes and returns a Facebook browser session using Selenium.
        It logs into Facebook using credentials from the configuration.
        If a browser session ('fbbrowser') isn't already an astra, it's added.

        Args:
            fbconfig (dict, optional): A dictionary containing Facebook configuration.
                                       If None, it's loaded from the Xetrapal's config.
                                       Defaults to None.

        Returns:
            A Selenium browser instance authenticated with Facebook.
        """
        if fbconfig==None:
            if "Facebook" in self.config.sections():
                fbconfig=karma.get_section(self.config,"Facebook",logger=self.logger)
                fbbrowser=astra.get_browser(logger=self.logger)
        fbkarmas.fb_login(fbbrowser,fbconfig,logger=self.logger)
        if "fbbrowser" not in self.astras.keys():
            self.add_astra('fbbrowser',fbbrowser)
        return fbbrowser
    def get_twython(self,twconfig=None):
        """
        Initializes and returns a Twython API instance for Twitter interaction.
        It authenticates using credentials from the configuration.
        If a Twython instance ('twython') isn't already an astra, it's added.

        Args:
            twconfig (dict, optional): A dictionary containing Twitter (Twython) configuration.
                                       If None, it's loaded from the Xetrapal's config.
                                       Defaults to None.

        Returns:
            A Twython API instance.
        """
        if twconfig==None:
            if "Twython" in self.config.sections():
                twconfig=karma.get_section(self.config,"Twython")
        tw=twastras.get_twython(twconfig,logger=self.logger)
        twkarmas.twython_check_auth(tw,logger=self.logger)
        tw.verify_credentials()
        if "twython" not in self.astras.keys():
            self.add_astra('twython',tw)
        return tw
    def get_tweepy(self,twconfig=None):
        """
        Initializes and returns a Tweepy API instance for Twitter interaction.
        It authenticates using credentials from the configuration.
        If a Tweepy instance ('tweepy') isn't already an astra, it's added.

        Args:
            twconfig (dict, optional): A dictionary containing Twitter (Tweepy) configuration.
                                       If None, it's loaded from the Xetrapal's config (expects "Twython" section).
                                       Defaults to None.

        Returns:
            A Tweepy API instance.
        """
        if twconfig==None:
            if "Twython" in self.config.sections(): # Assuming Tweepy uses similar config section
                twconfig=karma.get_section(self.config,"Twython")
        tweep=twastras.get_tweepy(twconfig,logger=self.logger)
        if "tweepy" not in self.astras.keys():
            self.add_astra("tweepy",tweep)
        return tweep
    def get_twython_streamer(self,twconfig=None,ofilename=None):
        """
        Initializes and returns a TwythonStreamer instance for Twitter streaming.
        If a TwythonStreamer instance ('twythonstreamer') isn't already an astra, it's added.

        Args:
            twconfig (dict, optional): A dictionary containing Twitter (Twython) configuration.
                                       If None, it's loaded from the Xetrapal's config.
                                       Defaults to None.
            ofilename (str, optional): The output filename for the streamed data.
                                       Defaults to "TwythonStreamer.json" in the session path.

        Returns:
            A TwythonStreamer instance.
        """
        if twconfig==None:
            if "Twython" in self.config.sections():
                twconfig=karma.get_section(self.config,"Twython")
        if ofilename==None:
           ofilename=os.path.join(self.sessionpath,"TwythonStreamer.json")
        tw=twastras.get_twython_streamer(twconfig,ofilename,logger=self.logger)
        if "twythonstreamer" not in self.astras.keys():
            self.add_astra('twythonstreamer',tw)
        return tw
    def get_googledriver(self,gdconfig=None):
        """
        Initializes and returns a Google Drive service instance (using Pygsheets).
        If a Pygsheets client ('pygsheet') isn't already an astra, it's added.

        Args:
            gdconfig (dict, optional): A dictionary containing Google Drive (Pygsheets) configuration.
                                       If None, it's loaded from the Xetrapal's config.
                                       Defaults to None.

        Returns:
            A Pygsheets client instance for interacting with Google Sheets.
        """
        if gdconfig==None:
            if "Pygsheets" in self.config.sections():
                gdconfig=karma.get_section(self.config,"Pygsheets")
        gd=gdastras.get_googledriver(gdconfig,logger=self.logger)
        if "pygsheet" not in self.astras.keys():
            self.add_astra('pygsheet',gd)
        return gd
    def post_tweet(self,tweet):
        """
        Posts a tweet to Twitter using the 'twython' astra.
        The tweet is posted asynchronously via a Pykka karta.

        Args:
            tweet (str): The text content of the tweet to post.
        """
        tweetmsg=karma.get_aadesh('run',self.astras['twython'].update_status,kwargs={'status':tweet})
        if self.kartarefs==[]:
            tweetkarta=self.start_pykka_karta()
        else:
            tweetkarta=self.kartarefs[0]
        tweetkarta.tell(tweetmsg)
#To Do
    def save_tweet_search_to_gdrive(self,searchstring,tcount=100,sheet_name=None):
        """
        (TODO) Searches Twitter for a given string and saves the results to Google Drive.
        This method is currently a placeholder.

        Args:
            searchstring (str): The string to search for on Twitter.
            tcount (int, optional): The number of tweets to retrieve. Defaults to 100.
            sheet_name (str, optional): The name of the Google Sheet to save results to.
                                        Defaults to None.
        """
        gd=self.astras['pygsheet']
        tw=self.astras['twython']
    def get_mojogmail(self):
        """
        Initializes and returns a MojoMail instance for email operations.
        If a MojoMail instance ('mojomail') isn't already an astra, it's added.

        Returns:
            A MojoMail instance.
        """
         mm=mojomailastras.get_mojogmail(configfile=self.configfile,logger=self.logger)
         if "mojomail" not in self.astras.keys():
             self.add_astra("mojomail",mm)
         return mm
    def get_tg_bot(self):
        """
        Initializes and returns a Telegram Bot instance.
        If the Telegram bot instance isn't already an astra, it's added.

        Returns:
            An XetrapalTelegramBot instance.
        """
        tg_bot=telegramastras.XetrapalTelegramBot(self.config,logger=self.logger)
        if tg_bot.name not in self.astras.keys():
            self.add_astra(tg_bot.name,tg_bot)
        return tg_bot
