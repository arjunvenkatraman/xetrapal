# Xetrapal (क्षेत्रपाल)

**Xetrapal** (क्षेत्रपाल - "Kshetrapal", meaning "Guardian of the Field/Region") is a Python-based orchestration and automation framework. It is designed for web-based task automation, data analysis, and data mining, with a particular focus on capabilities for Indic languages.

The framework provides a structured way to define and manage digital entities (Jeevas), their tools (Astras), and the actions they perform (Karmas).

## Core Concepts

The Xetrapal framework is built around a few core concepts, metaphorically named from Sanskrit/Hindi terms:

*   **Jeeva (जीव):** Represents a "living entity" or an agent within the system. Each Jeeva has its own configuration, manages its profile (persistent state), sets up logging, and handles session management. It is the fundamental building block that can possess Astras and perform Karmas.
*   **Astra (अस्त्र):** Translates to "weapon" or "tool." In Xetrapal, Astras are objects that provide interfaces to external services or functionalities. Examples include a Selenium browser instance for web automation, API clients for services like Twitter or Google Drive, or a Telegram bot controller.
*   **Karma (कर्म):** Refers to "action" or "deed." Karmas are the functions or tasks carried out by a Jeeva, typically utilizing one or more Astras. These can range from simple actions like logging into a website to complex workflows like searching for data, processing it, and storing the results.
*   **Vaahan (वाहन):** Meaning "vehicle" or "carrier." A Vaahan is a specialized type of Jeeva that is also capable of holding and managing its own set of Astras. This allows for a hierarchical or modular structuring of agents and their capabilities.

## Project Structure

The project is organized into two main directories:

*   `xetrapal/`: Contains the core framework code, including the definitions for Jeeva, Astra, Karma, Vaahan, and service-specific modules.
*   `tools/`: Contains utility scripts for setting up, managing, and interacting with the Xetrapal framework.

## Key Modules and Scripts

### `xetrapal/` Directory

*   **`Xetrapal.py`:** Defines the main `Xetrapal` class, which is a specialized `Jeeva`. It serves as the primary orchestrator, managing various Astras (like Twitter, Facebook, Google Drive clients) and Vaahans. It can initiate tasks and interact with different services.
*   **`jeeva.py`:** Defines the base `Jeeva` class, responsible for configuration, profile management (JSON-based persistence), logging, and session handling.
*   **`astra.py`:** Contains utility functions for creating and managing Astras. This includes helper functions for JSON processing, configuration loading, creating Selenium browser instances, and setting up colored loggers.
*   **`karma.py`:** Provides helper functions related to actions (Karmas). This includes utilities for JSON formatting, configuration management, data loading/saving, file downloads, Selenium browser interactions (scrolling, closing modals), and creating "aadesh" (command) objects for task dispatch.
*   **`vaahan.py`:** Defines the `Vaahan` class, a type of `Jeeva` that can hold and manage its own collection of Astras.
*   **`aadhaar.py`:** (आधार - "foundation" or "base") Contains constant definitions used across the framework, such as logging formats, color styles for logging, and predefined wait times.
*   **Service-Specific Modules:**
    *   The directory contains numerous modules for interacting with specific services, typically pairing an `astra.py` (for API client/tool setup) and a `karmas.py` (for actions related to that service).
    *   Examples:
        *   `fbkarmas.py`: Functions for Facebook automation (e.g., login, search, fetching post links).
        *   `twastras.py`: Defines custom Twitter streamers (`XpalTwitterStreamer`) and functions to get Twython and Tweepy API instances.
        *   `twkarmas.py`: Functions for Twitter actions (e.g., authentication check, search, calculating tweet/mention density).
        *   `gdastras.py`: Function to get an authorized Pygsheets client for Google Drive/Sheets.
        *   `gdkarmas.py`: Functions for Google Drive/Sheets operations (e.g., looking up, creating, opening spreadsheets, generating graph data from sheets).
        *   `mojomailastras.py`: Interface for MojoMail (Gmail interaction).
        *   `telegramastras.py` & `telegramkarmas.py`: For Telegram bot interactions, including state management and message polling/parsing.
*   **`pykkakarta.py`:** Implements `Karta`, a Pykka `ThreadingActor` for asynchronous task execution within the Xetrapal framework.
*   **`thespiankarta.py`:** Initializes a Thespian actor system, suggesting an alternative or additional actor model for distributed/concurrent processing.

### `tools/` Directory

*   **`createxetrapal.py`:** A utility script intended to create a Xetrapal instance if one does not exist (currently a placeholder).
*   **`getnewauthtoken.py`:** A script to guide users through the OAuth process to obtain and save Twitter authentication tokens using the Twython library.
*   **`harness.py`:** A script that sets up the Python path to include the parent directory and imports the `xetrapal` module. This is likely used as a test harness or an entry point for running Xetrapal from the `tools` directory.

## Basic Setup

1.  **Prerequisites:** Ensure Python 2.x (as indicated by some scripts) or Python 3.x (if modules have been updated) is installed.
2.  **Dependencies:** Install required Python packages. A `requirements.txt` file should ideally list these. Common dependencies based on the modules include:
    *   `twython`
    *   `tweepy`
    *   `pygsheets`
    *   `selenium`
    *   `beautifulsoup4` (or `BeautifulSoup` for older versions)
    *   `coloredlogs`
    *   `pygments`
    *   `configparser`
    *   `pykka`
    *   `thespian`
    *   `pandas`
    *   `telegram` (python-telegram-bot)
    You can typically install these using pip:
    ```bash
    pip install -r requirements.txt
    ```
    (If `requirements.txt` is missing, you'll need to install them individually, e.g., `pip install twython tweepy pygsheets selenium beautifulsoup4 coloredlogs pygments configparser pykka thespian pandas python-telegram-bot`)
3.  **GeckoDriver (for Firefox/Selenium):** The `tools` directory contains `geckodriver-v0.19.1-linux64.tar.gz`. You'll need to extract and place the `geckodriver` executable in your system's PATH, or configure Selenium to find it.
4.  **Configuration:**
    *   The framework relies heavily on configuration files (e.g., for API keys, paths, credentials). You will need to set up these configuration files.
    *   For example, `Xetrapal.py` and `jeeva.py` load configurations, and service-specific modules like `twastras.py` expect sections like `[Twython]` with API keys.
    *   The `tools/getnewauthtoken.py` script helps in creating part of this configuration for Twitter.
    *   Pay attention to paths for state files, token files, and data storage as specified in the configuration.

## High-Level Usage Overview

1.  **Configure:** Create the necessary configuration files with API keys, user credentials, and paths for data and logging.
2.  **Instantiate Xetrapal:**
    ```python
    from xetrapal.Xetrapal import Xetrapal
    # Assuming you have a configuration file, e.g., 'my_config.ini'
    xpal = Xetrapal(configfile='my_config.ini')
    ```
3.  **Acquire Astras (Tools):**
    *   Xetrapal can automatically acquire some Astras based on configuration (e.g., `get_twython()`, `get_googledriver()`).
    *   You might need to explicitly add or manage others.
    ```python
    twitter_api = xpal.get_twython()
    google_sheets_client = xpal.get_googledriver()
    # For services requiring manual setup or specific Vaahans:
    # my_vaahan.add_astra("my_custom_tool", custom_tool_instance)
    ```
4.  **Perform Karmas (Actions):**
    *   Use the acquired Astras to perform actions. These actions are often encapsulated in "karma" modules.
    ```python
    from xetrapal import twkarmas, gdkarmas

    if twitter_api:
        tweets = twkarmas.twython_search(twitter_api, "YourSearchQuery", tcount=50)
        for tweet in tweets:
            print(tweet.get('full_text', tweet.get('text')))

    if google_sheets_client:
        spreadsheet = gdkarmas.get_ssheet_by_name(google_sheets_client, "MySheetTitle")
        # ... work with the spreadsheet
    ```
5.  **Asynchronous Tasks (Karta):**
    *   For long-running or parallel tasks, Xetrapal can use Kartas (actors).
    ```python
    from xetrapal import karma # For get_aadesh

    def my_long_task(param1, param2):
        # ... do something time-consuming ...
        print(f"Task done with {param1} and {param2}")

    if xpal.kartarefs: # Check if a Karta system is running/available
      karta_ref = xpal.kartarefs[0] # Get a reference to a Karta
      task_message = karma.get_aadesh(msg="run my task", func=my_long_task, args=[10, "hello"])
      karta_ref.tell(task_message)
    else: # Or start one if needed
      karta_ref = xpal.start_pykka_karta()
      task_message = karma.get_aadesh(msg="run my task", func=my_long_task, args=[10, "hello"])
      karta_ref.tell(task_message)

    ```
6.  **Session Management & Logging:**
    *   Jeeva (and thus Xetrapal and Vaahan) automatically handles session creation (timestamped directories for logs, data) and logging. Check the console output and log files in your configured data path.

This framework provides a flexible, albeit complex, structure for building sophisticated automation and data analysis agents. Its strength lies in its modularity and the clear separation of concerns between the agent (Jeeva), its tools (Astras), and its actions (Karmas).
