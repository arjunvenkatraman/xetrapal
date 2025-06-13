#coding: utf-8
'''
यहां हम फेसबुक सम्बन्धी अस्त्रों का उल्लेख करेंगे 
'''
#from .astra import *
import astra
import colored
import karma
import pandas
import datetime
import math

#Fire and Forget Astras, to be run with {'msg':'run','func':function_object,'args':(),'kwargs':{}}
def twython_check_auth(tw,logger=astra.baselogger):
    """
    Checks if the provided Twython instance is authenticated by verifying credentials.

    Args:
        tw (twython.Twython): An initialized Twython instance.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
    """
    logger.info("Trying to check if our Twython is authenticated ...")
    try:
        creds=tw.verify_credentials()
        logger.info("Twython is authenticated as " + colored.stylize(creds['name'],colored.fg("red")))
    except Exception as exception:
        logger.error("Twython auth check got..."+ repr(exception))



#Get value Astras, to be run with {'msg':'get','func':function_object,'args':(),'kwargs':{}}
#Use 

def twython_search(tw,searchstring,logger=astra.baselogger,tcount=100,maxtries=10):
    """
    Performs a Twitter search using Twython, attempting to retrieve a specific number of tweets.
    It handles pagination by using `max_id` to get older tweets until `tcount` is reached
    or `maxtries` is exceeded.

    Args:
        tw (twython.Twython): Initialized Twython instance.
        searchstring (str): The query string to search for.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
        tcount (int, optional): Desired number of tweets to retrieve. Defaults to 100.
        maxtries (int, optional): Maximum number of pagination attempts. Defaults to 10.

    Returns:
        list: A list of tweet dictionaries, up to `tcount` items.
              Returns an empty list if an error occurs or no tweets are found.
    """
    results=[]
    logger.info(f"Searching Twitter for '{searchstring}' for {tcount} tweets.")
    try:
        # Initial search
        search_results = tw.search(q=searchstring,count=min(tcount, 100),tweet_mode="extended") # Max 100 per request
        if 'statuses' not in search_results:
            logger.warning("No 'statuses' key in search results.")
            return []
        results = search_results['statuses']

        tries=0
        # Pagination if needed
        while len(results) < tcount and tries < maxtries and results:
            if 'id' not in results[-1]:
                logger.warning("Last tweet in results has no 'id', cannot paginate further.")
                break
            max_id = results[-1]['id'] - 1 # Important to avoid duplicates
            logger.info(f"Paginating search, current count: {len(results)}, max_id: {max_id}")

            remaining_needed = tcount - len(results)
            count_this_request = min(remaining_needed, 100)

            paginated_search = tw.search(q=searchstring,count=count_this_request,max_id=max_id,tweet_mode="extended")
            if 'statuses' not in paginated_search or not paginated_search['statuses']:
                logger.info("No more statuses in paginated search.")
                break
            results.extend(paginated_search['statuses'])
            karma.wait(logger=logger) # Be mindful of rate limits
            tries+=1

        logger.info(f"Got {len(results)} tweets for search query '{searchstring}' after {tries} tries.")
        return results[:tcount]
    except twython.TwythonError as e:
        logger.error(f"Twython API error during search: {e}")
        return results # Return what was gathered so far
    except Exception as e:
        logger.error(f"Unexpected error during twython_search: {e}")
        return [] # Return empty on unexpected error

		
def twython_get_ntweets_for_search(tw,search,tcount,geocode=None,maxtries=0,logger=astra.baselogger):
    """
    Retrieves a specified number of tweets for a search query, handling pagination
    and attempting to remove duplicates based on full_text. Stores results in a Pandas DataFrame.

    Args:
        tw (twython.Twython): Initialized Twython instance.
        search (str): The search query.
        tcount (int): The desired number of unique tweets.
        geocode (str, optional): Geolocation parameter for the search (e.g., "lat,long,radius"). Defaults to None.
        maxtries (int, optional): Maximum pagination attempts. If 0, it's auto-calculated. Defaults to 0.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        pandas.DataFrame: A DataFrame containing the tweets, or an empty DataFrame if none are found or an error occurs.
    """
    logger.info(f"Getting {tcount} tweets for search: '{search}'")
    try:
        initial_search_params = {'q': search, 'count': min(tcount, 100), 'tweet_mode': "extended"}
        if geocode:
            initial_search_params['geocode'] = geocode

        search_results = tw.search(**initial_search_params)
        if 'statuses' not in search_results or not search_results['statuses']:
            logger.info("No tweets found in initial search.")
            return pandas.DataFrame()

        tweetdf = pandas.DataFrame(search_results['statuses'])
        if tweetdf.empty:
            return pandas.DataFrame()
        tweetdf = tweetdf.drop_duplicates(subset="full_text",keep="first").reset_index(drop=True)

        tries=0
        if maxtries==0: # Auto-calculate maxtries if not set
            maxtries = (tcount / 100) * 3 + 1 # Estimate based on 100 tweets per request
            maxtries = max(maxtries, 5) # Minimum tries

        while len(tweetdf) < tcount and tries < maxtries:
            logger.info(f"Currently have {len(tweetdf)} unique tweets for '{search}'. Tries: {tries+1}/{maxtries}")
            if tweetdf.empty or 'id' not in tweetdf.columns:
                logger.warning("DataFrame is empty or 'id' column missing, cannot paginate.")
                break

            max_id = tweetdf['id'].iloc[-1] - 1

            pagination_params = {'q': search, 'count': min(tcount - len(tweetdf), 100),
                                 'tweet_mode': "extended", 'max_id': max_id}
            if geocode:
                pagination_params['geocode'] = geocode

            p_search = tw.search(**pagination_params)
            if 'statuses' not in p_search or not p_search['statuses']:
                logger.info("No more tweets in paginated search.")
                break

            p_df = pandas.DataFrame(p_search['statuses'])
            if p_df.empty:
                break

            p_df = p_df.drop_duplicates(subset="full_text",keep="first")
            tweetdf = pandas.concat([tweetdf,p_df], ignore_index=True)
            tweetdf = tweetdf.drop_duplicates(subset="full_text",keep="first").reset_index(drop=True)

            logger.info("Sleeping before next pagination...")
            karma.wait(logger=logger)
            tries+=1

        logger.info(f"Finished search for '{search}'. Got {len(tweetdf)} unique tweets.")
        return tweetdf.head(tcount)

    except twython.TwythonError as e:
        logger.error(f"Twython API error in twython_get_ntweets_for_search: {e}")
        return pandas.DataFrame() # Return empty DataFrame on API error
    except Exception as e:
        logger.error(f"Unexpected error in twython_get_ntweets_for_search: {e}")
        return pandas.DataFrame()


def get_tweet_density(tw,screen_name,logger=astra.baselogger):
    """
    Calculates the tweet density for a user (tweets per hour).
    This is based on their last 100 tweets or fewer if they have less.
    Density = (Number of tweets in sample) / (Hours since the oldest tweet in sample).

    Args:
        tw (twython.Twython): Initialized Twython instance.
        screen_name (str): The Twitter screen name of the user.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        float: The calculated tweet density (tweets per hour), rounded to 3 decimal places.
               Returns 0 if no tweets are found or 'created_at' is missing.
    """
    logger.info(f"Calculating tweet density for @{screen_name}")
    try:
        last100_raw = tw.get_user_timeline(screen_name=screen_name,count=100, tweet_mode="extended")
        if not last100_raw:
            logger.warning(f"No tweets found for @{screen_name}.")
            return 0.0

        last100_df = pandas.DataFrame(last100_raw)
        if "created_at" not in last100_df.columns or last100_df.empty:
            logger.warning(f"'created_at' column missing or no tweets in DataFrame for @{screen_name}.")
            return 0.0

        last100_df['createdts'] = last100_df['created_at'].apply(get_twitter_ts)

        num_tweets = len(last100_df)
        if num_tweets == 0: # Should be caught by earlier checks, but good to be safe
            return 0.0

        oldest_tweet_ts = last100_df['createdts'].min()
        hours_since_oldest = get_age(oldest_tweet_ts)

        if hours_since_oldest == 0: # Avoid division by zero if all tweets are very recent
            logger.warning(f"Oldest tweet for @{screen_name} is too recent to calculate density (age is 0 hours).")
            # Could return a high number or handle as appropriate. For now, 0 or num_tweets.
            return float(num_tweets) # Or 0.0, depending on desired behavior for <1hr activity

        density = num_tweets / hours_since_oldest
        logger.info(f"@{screen_name}: {num_tweets} tweets over {hours_since_oldest:.2f} hours. Density: {density:.3f} tweets/hr.")
        return round(density,3)

    except twython.TwythonError as e:
        logger.error(f"Twython API error getting timeline for @{screen_name}: {e}")
        return 0.0
    except Exception as e:
        logger.error(f"Unexpected error calculating tweet density for @{screen_name}: {e}")
        return 0.0


#To move into Xetrapal
def get_twitter_ts(string):
    """
    Converts a Twitter API 'created_at' string to a UTC datetime object.

    Args:
        string (str): The 'created_at' string from Twitter API
                      (e.g., "Wed Jun 06 00:25:58 +0000 2018").

    Returns:
        datetime.datetime: A datetime object representing the timestamp in UTC.
                           Returns None if parsing fails.
    """
    try:
        return datetime.datetime.strptime(string.replace("+0000","UTC"),"%a %b %d %H:%M:%S %Z %Y")
    except ValueError as e:
        astra.baselogger.error(f"Error parsing Twitter timestamp string '{string}': {e}")
        return None


#To move into Xetrapal
def get_age(createdts):
    """
    Calculates the age in hours from a given datetime object to now.

    Args:
        createdts (datetime.datetime): The past datetime object.

    Returns:
        float: The age in hours, rounded up to the nearest whole hour (ceiling).
               Returns 0.0 if createdts is None or in the future.
    """
    if createdts is None:
        return 0.0
    now = datetime.datetime.utcnow() # Use UTC now for consistency if createdts is UTC
    age_delta = now - createdts

    if age_delta.total_seconds() < 0: # Future timestamp
        return 0.0

    return math.ceil(age_delta.total_seconds() / 3600.0)


#To =move into Xetrapal
def get_mention_density(tw,screen_name,logger=astra.baselogger):
    """
    Calculates the mention density for a user (mentions per hour).
    This is based on the last 100 mentions of the user or fewer.
    Density = (Number of mentions in sample) / (Hours since the oldest mention in sample).

    Args:
        tw (twython.Twython): Initialized Twython instance.
        screen_name (str): The Twitter screen name of the user to search mentions for.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        float: The calculated mention density (mentions per hour), rounded to 3 decimal places.
               Returns 0 if no mentions are found or 'created_at' is missing.
    """
    logger.info(f"Calculating mention density for @{screen_name}")
    search_query = f"@{screen_name}"

    # Using twython_get_ntweets_for_search to get mentions
    last100_mentions_df = twython_get_ntweets_for_search(tw, search_query, tcount=100, logger=logger)

    if last100_mentions_df.empty or "created_at" not in last100_mentions_df.columns:
        logger.warning(f"No mentions found or 'created_at' column missing for @{screen_name}.")
        return 0.0

    last100_mentions_df['createdts'] = last100_mentions_df['created_at'].apply(get_twitter_ts)

    num_mentions = len(last100_mentions_df)
    if num_mentions == 0:
        return 0.0

    oldest_mention_ts = last100_mentions_df['createdts'].min()
    hours_since_oldest_mention = get_age(oldest_mention_ts)

    if hours_since_oldest_mention == 0:
        logger.warning(f"Oldest mention for @{screen_name} is too recent to calculate density.")
        return float(num_mentions) # Or 0.0

    density = num_mentions / hours_since_oldest_mention
    logger.info(f"@{screen_name}: {num_mentions} mentions over {hours_since_oldest_mention:.2f} hours. Density: {density:.3f} mentions/hr.")
    return round(density,3)
    
