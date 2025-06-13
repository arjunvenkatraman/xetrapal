#coding: utf-8
'''
यहां हम फेसबुक सम्बन्धी अस्त्रों का उल्लेख करेंगे 
'''
#from .astra import *
import astra
import urllib2,json
#Fire and Forget Astras, to be run with {'msg':'run','func':function_object,'args':(),'kwargs':{}}

#Get value Astras, to be run with {'msg':'get','func':function_object,'args':(),'kwargs':{}}
#Use 

        
def lookup_ssheet(gc,sheetdict,logger=astra.baselogger):
    """
    Looks up a Google Spreadsheet information dictionary from a list of available spreadsheets.
    It tries to match by 'id' first, then by 'name'.

    Args:
        gc: pygsheets client instance.
        sheetdict (dict): A dictionary containing 'id' and/or 'name' of the spreadsheet to find.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        dict: The matching spreadsheet information dictionary from gc.list_ssheets(),
              or the original sheetdict if no match is found.
    """
    logger.info("Looking up sheetdict")
    try:
        for ssheet in gc.list_ssheets():
            if 'id' in sheetdict and sheetdict['id']==ssheet['id']:
                logger.info("Found by ID")
                return ssheet
            if 'name' in sheetdict and sheetdict['name']==ssheet['name']:
                logger.info("Found by name")
                return ssheet
    except Exception as e:
        logger.error(f"Error looking up spreadsheet: {e}")
    return sheetdict
    
def get_ssheet(gd,key=None,name=None,logger=astra.baselogger):
    """
    Opens a Google Spreadsheet by its key (ID) or name.

    Args:
        gd: pygsheets client instance.
        key (str, optional): The ID (key) of the spreadsheet. Defaults to None.
        name (str, optional): The name (title) of the spreadsheet. Defaults to None.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        pygsheets.Spreadsheet: The opened Spreadsheet object, or None if not found or an error occurs.
    """
    if key==None and name==None:
        logger.error("Either key or name must be provided to get a spreadsheet.")
        return None
    if key!=None:
        return get_ssheet_by_key(gd,key,logger=logger)
    if name!=None:
        return get_ssheet_by_name(gd,name,logger=logger)
    return None # Should not be reached if logic is correct

def create_new_ssheet(gc,title,folderid=None,logger=astra.baselogger):
    """
    Creates a new Google Spreadsheet.

    Args:
        gc: pygsheets client instance.
        title (str): The title for the new spreadsheet.
        folderid (str, optional): The ID of the Google Drive folder to create the spreadsheet in.
                                 Defaults to None (root folder).
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        pygsheets.Spreadsheet: The newly created Spreadsheet object, or None if a sheet
                               with the same title already exists or an error occurs.
    """
    try:
        for ssheet in gc.list_ssheets():
            if ssheet['name']==title:
                logger.info(f"Sheet '{title}' already exists...try a different name or open existing.")
                return None # Or gc.open_by_key(ssheet['id']) if opening existing is desired
        gc.create(title,parent_id=folderid)
        logger.info(f"Spreadsheet '{title}' creation initiated.")
        # Re-list and open to confirm creation, as gc.create might not return the object directly
        for ssheet in gc.list_ssheets(): # This might be slow for many sheets
            if ssheet['name']==title:
                logger.info(f"Sheet '{title}' created successfully with ID: {ssheet['id']}")
                return gc.open_by_key(ssheet['id'])
        logger.error(f"Failed to confirm creation of spreadsheet '{title}'.")
        return None
    except Exception as e:
        logger.error(f"Error creating new spreadsheet '{title}': {e}")
        return None
    
def get_ssheet_by_name(gc,title,logger=astra.baselogger):
    """
    Opens a Google Spreadsheet by its name (title).

    Args:
        gc: pygsheets client instance.
        title (str): The name/title of the spreadsheet.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        pygsheets.Spreadsheet: The opened Spreadsheet object, or None if not found.
    """
    try:
        logger.info(f"Trying to fetch sheet by name: '{title}'")
        return gc.open(title) # pygsheets.Client.open() can open by title
    except pygsheets.exceptions.SpreadsheetNotFound:
        logger.error(f"Sheet with name '{title}' does not exist.")
        return None
    except Exception as e:
        logger.error(f"Error opening sheet by name '{title}': {e}")
        return None

def get_ssheet_by_key(gc,key,logger=astra.baselogger):
    """
    Opens a Google Spreadsheet by its key (ID).

    Args:
        gc: pygsheets client instance.
        key (str): The ID (key) of the spreadsheet.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        pygsheets.Spreadsheet: The opened Spreadsheet object, or None if not found or an error occurs.
    """
    try:
        logger.info(f"Trying to fetch sheet by key: {key}")
        return gc.open_by_key(key)
    except pygsheets.exceptions.SpreadsheetNotFound:
        logger.error(f"Sheet with key '{key}' not found.")
        return None
    except Exception as e:
        logger.error(f"Error opening sheet by key '{key}': {e}")
        return None

def get_sheet_last_row(ssheet,sheetname):
    """
    Retrieves the last non-empty row from a specific worksheet within a spreadsheet.
    It assumes the first row is headers and starts checking from the second row.

    Args:
        ssheet (pygsheets.Spreadsheet): The spreadsheet object.
        sheetname (str): The title of the worksheet to check.

    Returns:
        list: The last non-empty row as a list of cell values, or None if the sheet is empty
              or an error occurs.
    """
    try:
        sheet = ssheet.worksheet_by_title(sheetname)
        # This method is fragile. pygsheets might have a better way to get last row.
        # For example, sheet.rows gives the number of rows with content.
        # However, to replicate the original logic:
        rownum = 2
        while True:
            rowval = sheet.get_row(rownum, returnas='cells', include_tailing_empty=False)
            # Check if all cells in rowval are empty or just one empty string if row is truly empty
            if not any(cell.value for cell in rowval):
                if rownum == 2: # First data row is empty
                    return None
                return sheet.get_row(rownum - 1) # Previous row was the last non-empty
            rownum += 1
            if rownum > sheet.rows + 5: # Safety break to avoid infinite loops on strange sheets
                # If many empty rows at the end, this might be needed.
                # Fallback to sheet.get_all_values() and find last non-empty might be more robust.
                all_vals = sheet.get_all_values(include_tailing_empty=False, include_empty_rows=False)
                if all_vals:
                    return all_vals[-1]
                return None


    except pygsheets.exceptions.WorksheetNotFound:
        astra.baselogger.error(f"Worksheet '{sheetname}' not found in spreadsheet '{ssheet.title}'.")
        return None
    except Exception as e:
        astra.baselogger.error(f"Error getting last row from sheet '{sheetname}': {e}")
        return None
        
def get_json_feed(feedurl):
    """
    Fetches and parses JSON data from a given URL.

    Args:
        feedurl (str): The URL of the JSON feed.

    Returns:
        dict: The parsed JSON data as a dictionary, or None if an error occurs.
    """
    try:
        response=urllib2.urlopen(feedurl)
        data=json.load(response)
        return data
    except urllib2.URLError as e:
        astra.baselogger.error(f"URL error fetching JSON feed {feedurl}: {e}")
        return None
    except ValueError as e: # For json.load errors
        astra.baselogger.error(f"JSON decoding error for feed {feedurl}: {e}")
        return None
    except Exception as e:
        astra.baselogger.error(f"Unexpected error fetching JSON feed {feedurl}: {e}")
        return None
    
def goto_sheet_by_key(browser,sheetkey):
    """
    Navigates the given Selenium browser to a Google Spreadsheet URL using its key.

    Args:
        browser: Selenium WebDriver instance.
        sheetkey (str): The key (ID) of the Google Spreadsheet.
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheetkey}"
    astra.baselogger.info(f"Navigating browser to sheet: {url}")
    browser.get(url)

def goto_sheet_tab(browser,sheetname):
    """
    Attempts to click on a sheet tab by its name within an open Google Spreadsheet
    in a Selenium browser.

    Note: This relies on specific class names and might be fragile if Google changes its UI.

    Args:
        browser: Selenium WebDriver instance (should have a Google Spreadsheet open).
        sheetname (str): The name of the sheet tab to click.
    """
    try:
        astra.baselogger.info(f"Attempting to navigate to sheet tab: '{sheetname}'")
        for sheettab in browser.find_elements_by_class_name("docs-sheet-tab-name"):
            # print sheettab.get_property("innerHTML") # For debugging
            if sheettab.get_property("innerHTML") == sheetname:
                sheettab.click()
                astra.baselogger.info(f"Clicked on sheet tab: '{sheetname}'")
                return
        astra.baselogger.warning(f"Sheet tab '{sheetname}' not found.")
    except Exception as e:
        astra.baselogger.error(f"Error navigating to sheet tab '{sheetname}': {e}")


def build_cube(gc,sheetname=None,key=None,logger=astra.baselogger):
    """
    (Placeholder/Incomplete) Opens a Google Spreadsheet intended to be a 'cube'.
    The function seems to prioritize opening by name if both name and key are provided.

    Args:
        gc: pygsheets client instance.
        sheetname (str, optional): The name of the spreadsheet. Defaults to None.
        key (str, optional): The key (ID) of the spreadsheet. Defaults to None.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.

    Returns:
        pygsheets.Spreadsheet: The opened spreadsheet object, or None if identifiers are missing
                               or the sheet cannot be opened.
    """
    if sheetname==None and key==None:
        logger.error("No remote identifier specified for cube, cannot open.")
        return None

    cubesheet = None
    if sheetname != None:
        logger.info(f"Trying to build cube from sheet name: '{sheetname}'")
        cubesheet = get_ssheet_by_name(gc, sheetname, logger=logger) # Changed to use gc
    elif key != None: # Only use key if sheetname is not provided or failed
        logger.info(f"Trying to build cube from sheet key: '{key}'")
        cubesheet = get_ssheet_by_key(gc, key, logger=logger) # Changed to use gc

    if not cubesheet:
        logger.error("Could not open the cube spreadsheet with provided identifiers.")

    return cubesheet

def generate_graph(gd,sheetname=None,key=None,logger=astra.baselogger,outfile=None):
    """
    Generates a graph data structure (nodes and links) from a Google Spreadsheet.
    The spreadsheet is expected to have two worksheets: "Nodes" and "Links",
    with specific column headers (e.g., 'Group', 'Radius', 'Color', 'Label', 'ID' for nodes;
    'Source', 'Target', 'Value' for links).

    Args:
        gd: pygsheets client instance.
        sheetname (str, optional): The name of the Google Spreadsheet.
        key (str, optional): The key (ID) of the Google Spreadsheet.
                             Either sheetname or key must be provided.
        logger (logging.Logger, optional): Logger instance. Defaults to astra.baselogger.
        outfile (str, optional): Path to a JSON file where the graph data will be saved.
                                 If None, the graph dictionary is returned but not saved to a file.
                                 Defaults to None.

    Returns:
        dict: A dictionary representing the graph (with "nodes" and "links" keys),
              or None if the spreadsheet or required worksheets are not found or an error occurs.
    """

    networksheet=get_ssheet(gd,key=key,name=sheetname,logger=logger) # Corrected to pass name
    if not networksheet:
        logger.error("Could not open the network spreadsheet.")
        return None

    try:
        nodesheet=networksheet.worksheet_by_title("Nodes")
        linksheet=networksheet.worksheet_by_title("Links")
    except pygsheets.exceptions.WorksheetNotFound as e:
        logger.error(f"Required worksheet not found in '{networksheet.title}': {e}")
        return None
    except Exception as e:
        logger.error(f"Error accessing worksheets in '{networksheet.title}': {e}")
        return None

    nodedf=nodesheet.get_as_df()
    linkdf=linksheet.get_as_df()
    # Transpose().to_dict() might not be the most standard way to get list of dicts
    # df.to_dict(orient='records') is usually preferred.
    nodedict_list = nodedf.to_dict(orient='records')
    linkdict_list = linkdf.to_dict(orient='records')

    networkgraph={"links":[],"nodes":[{"group": 1,"id": "root","radius":2,"label": "","color": "#F5F5F5"}]} # Root node

    for value in nodedict_list:
        nodeitem={}
        nodeitem['details']=value # Keep original data
        nodeitem['group']=value.get('Group')
        nodeitem['radius']=value.get('Radius')
        nodeitem['color']=value.get("Color")
        nodeitem['label']=value.get('Label')
        nodeitem['id']=value.get('ID')
        if nodeitem['id'] is None:
            logger.warning(f"Node missing ID: {value}, skipping.")
            continue
        networkgraph['nodes'].append(nodeitem)

    for value in linkdict_list:
        linkitem={}
        linkitem['source']=value.get('Source')
        linkitem['target']=value.get('Target')
        linkitem['value']=value.get('Value')
        if linkitem['source'] is None or linkitem['target'] is None:
            logger.warning(f"Link missing source or target: {value}, skipping.")
            continue
        networkgraph['links'].append(linkitem)

    if outfile==None:
        logger.warning("No output file specified, returning graph dictionary.")
    else:
        try:
            with open(outfile,"w") as f:
                json.dump(networkgraph, f, indent=4) # Use json.dump for writing to file
            logger.info(f"Graph data saved to {outfile}")
        except IOError as e:
            logger.error(f"Could not write graph data to outfile {outfile}: {e}")
            return None # Indicate failure if file write fails

    return networkgraph
    
    linksheet=networksheet.worksheet_by_title("Links")
    nodedf=nodesheet.get_as_df()
    linkdf=linksheet.get_as_df()
    nodedict=nodedf.transpose().to_dict()
    linkdict=linkdf.transpose().to_dict()
    networkgraph={"links":[],"nodes":[{"group": 1,"id": "root","radius":2,"label": "","color": "#F5F5F5"}]}
    for key,value in nodedict.iteritems():
        nodeitem={}
        nodeitem['details']=value
        nodeitem['group']=value['Group']
        nodeitem['radius']=value['Radius']
        nodeitem['color']=value["Color"]
        nodeitem['label']=value['Label']
        nodeitem['id']=value['ID']
        networkgraph['nodes'].append(nodeitem)
    for key,value in linkdict.iteritems():
        linkitem={}
        linkitem['source']=value['Source']
        linkitem['target']=value['Target']
        linkitem['value']=value['Value']
        networkgraph['links'].append(linkitem)
    if outfile==None:
        logger.warning("No output file specified, returning graphdict")
        return networkgraph
    with open(outfile,"w") as f:
        f.write(json.dumps(networkgraph))
    return networkgraph
    
