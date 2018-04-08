import requests
import getpass
import json

apiURL = "https://home.queegmire.com/tt-rss/api/index.php"
sessionID = ""


def callAPI(apiRequest):
    response = requests.post(apiURL, json=apiRequest)
    r_data = json.loads(response.text)
    return r_data


def getApiLevel():
    '''
    since version:1.5.8, api level 1
    Return an abstracted integer API version level, increased with each API
    functionality change. This is the proper way to detect host API
    functionality, instead of using getVersion.
    {"level":1}
    Whether tt-rss returns error for this method (e.g. version:1.5.7 and below)
    client should assume API level 0.
    '''
    pass


def getVersion():
    '''
    Returns tt-rss version. As of, version:1.5.8 it is not recommended to use
    this to detect API functionality, please use getApiLevel instead.
    {"version":"1.4.0"}
    '''
    pass


def login(user, password):
    '''
    Returns client session ID.
    {"session\_id":"xxx"}
    It can also return several error objects:
        If API is disabled for this user: error: "API_DISABLED"
        If specified username and password are incorrect: error: "LOGIN_ERROR"
        In case it isn’t immediately obvious, you have to login and get a
            session ID even if you are using single user mode. You can omit
            user and password parameters.
    On version:1.6.0 and above login also returns current API level as an
    api_level integer, you can use that instead of calling getApiLevel after
    login.
    '''
    global sessionID
    apiCall = {"op": "login", "user": user, "password": password}
    response = callAPI(apiCall)
    sessionID = response['content']['session_id']
    print('login response: ', response)
    return response


def logout():
    '''
    Closes your login session. Returns either status-message {"status":"OK"}
    or an error (e.g. {"error":"NOT_LOGGED_IN"})
    '''
    global sessionID
    apiCall = {"op": "logout", "sid": sessionID}
    response = callAPI(apiCall)
    print('logout response: ', response)
    return response


def isLoggedIn():
    '''
    Returns a status message with boolean value showing whether your client
    (e.g. specific session ID) is currently logged in.
    {"status":false}
    '''
    pass


def getUnread():
    '''
    Returns an integer value of currently unread articles.
    {"unread":"992"}
    '''
    pass


def getCounters(output_mode):
    '''
    Required version: version:1.5.0
    Returns a list of unread article counts for specified feed groups.
    Parameters:
        output_mode (string) - Feed groups to return counters for
    Output mode is a character string, comprising several letters
        (defaults to “flc”):
        f - actual feeds
        l - labels
        c - categories
        t - tags
    Several global counters are returned as well, those can’t be disabled with
        output_mode.
    '''
    pass


def getFeeds(cat_id, unread_only, limit, offset, include_nested):
    '''
    Returns JSON-encoded list of feeds. The list includes category id, title,
    feed url, etc.
    Parameters:
        cat_id (integer) - return feeds under category cat_id
        unread_only (bool) - only return feeds which have unread articles
        limit (integer) - limit amount of feeds returned to this value
        offset (integer) - skip this amount of feeds first
        include_nested (bool) - include child categories (as Feed objects with
            is_cat set) requires version:1.6.0
    Pagination:
        Limit and offset are useful if you need feedlist pagination. If you use
        them, you shouldn’t filter by unread, handle filtering in your app
        instead.
    Special category IDs are as follows:
        0 Uncategorized
        -1 Special (e.g. Starred, Published, Archived, etc.)
        -2 Labels
        Added in version:1.5.0:
        -3 All feeds, excluding virtual feeds (e.g. Labels and such)
        -4 All feeds, including virtual feeds
    Known bug: Prior to version:1.5.0 passing null or 0 cat_id to this method
    returns full list of feeds instead of Uncategorized feeds only.
    '''
    pass


def getCategories():
    '''
    Returns JSON-encoded list of categories with unread counts.
        unread_only (bool) - only return categories which have unread articles
        enable_nested (bool) - switch to nested mode, only returns topmost
            categories requires version:1.6.0
        include_empty (bool) - include empty categories requires version:1.7.6
    Nested mode in this case means that a flat list of only topmost categories
    is returned and unread counters include counters for child categories.
    This should be used as a starting point, to display a root list of all
    (for backwards compatibility) or topmost categories, use getFeeds to
    traverse deeper.
    '''
    pass


def getHeadlines():
    '''
    Returns JSON-encoded list of headlines.
    Parameters:
        feed_id (integer) - only output articles for this feed
        limit (integer) - limits the amount of returned articles (see below)
        skip (integer) - skip this amount of feeds first
        filter (string) - currently unused (?)
        is_cat (bool) - requested feed_id is a category
        show_excerpt (bool) - include article excerpt in the output
        show_content (bool) - include full article text in the output
        view_mode (string = all_articles, unread, adaptive, marked, updated)
        include_attachments (bool) - include article attachments (e.g.
            enclosures) requires version:1.5.3
        since_id (integer) - only return articles with id greater than since_id
            requires version:1.5.6
        include_nested (boolean) - include articles from child categories
            requires version:1.6.0
        order_by (string) - override default sort order requires version:1.7.6
        sanitize (bool) - sanitize content or not requires version:1.8
            (default: true)
        force_update (bool) - try to update feed before showing headlines
            requires version:1.14 (api 9) (default: false)
        has_sandbox (bool) - indicate support for sandboxing of iframe elements
            (default: false)
        include_header (bool) - adds status information when returning
            headlines, instead of array(articles) return value changes to
            array(header, array(articles)) (api 12)
    Limit:
        Before API level 6 maximum amount of returned headlines is capped at
        60, API 6 and above sets it to 200.
    This parameters might change in the future (supported since API level 2):
        search (string) - search query (e.g. a list of keywords)
        search_mode (string) - all_feeds, this_feed (default), this_cat
            (category containing requested feed)
        match_on (string) - ignored
    Special feed IDs are as follows:
        -1 starred
        -2 published
        -3 fresh
        -4 all articles
        0 - archived
        IDs < -10 labels
        Sort order values:
            date_reverse - oldest first
            feed_dates - newest first, goes by feed date
            (nothing) - default
    '''
    pass


def updateArticle():
    '''
    Update information on specified articles.
    Parameters:
        article_ids (comma-separated list of integers) - article IDs to operate
            on
        mode (integer) - type of operation to perform (0 - set to false,
            1 - set to true, 2 - toggle)
        field (integer) - field to operate on (0 - starred, 1 - published, 2 -
            unread, 3 - article note since api level 1)
        data (string) - optional data parameter when setting note field (since
            api level 1)
    E.g. to set unread status of articles X and Y to false use the following:
        ?article_ids=X,Y&mode=0&field=2
    Since version:1.5.0 returns a status message:
        {"status":"OK","updated":1}
    “Updated” is number of articles updated by the query.
    '''
    pass


def getArticle():
    '''
    Requests JSON-encoded article object with specific ID.
    article_id (integer) - article ID to return as of 15.10.2010 git or
        version:1.5.0 supports comma-separated list of IDs
    Since version:1.4.3 also returns article attachments.
    '''
    pass


def getConfig():
    '''
    Returns tt-rss configuration parameters:
        {"icons_dir":"icons","icons_url":"icons",
            "daemon_is_running":true,"num_feeds":71}
    icons_dir - path to icons on the server filesystem
    icons_url - path to icons when requesting them over http
    daemon_is_running - whether update daemon is running
    num_feeds - amount of subscribed feeds (this can be used to refresh
        feedlist when this amount changes)
    '''
    pass


def updateFeed():
    '''
    Tries to update specified feed. This operation is not performed in the
    background, so it might take considerable time and, potentially, be aborted
    by the HTTP server.
    feed_id (integer) - ID of feed to update
    Returns status-message if the operation has been completed.
        {"status":"OK"}
    '''
    pass


def getPref():
    '''
    Returns preference value of specified key.
    pref_name (string) - preference key to return value of
        {"value":true}
    '''
    pass


def catchupFeed():
    '''
    Required version: version:1.4.3
    Tries to catchup (e.g. mark as read) specified feed.
    Parameters:
        feed_id (integer) - ID of feed to update
        is_cat (boolean) - true if the specified feed_id is a category
    Returns status-message if the operation has been completed.
        {"status":"OK"}
    '''
    pass


def getLabels():
    '''
    (since API level 1)
    Returns list of configured labels, as an array of label objects:
        {"id":2,"caption":"Debian","fg_color":"#e14a00","bg_color":"#ffffff",
            "checked":false},
    Before version:1.7.5:
        Returned id is an internal database id of the label, you can convert it
        to the valid feed id like this:
            feed_id = -11 - label_id
    After:
        No conversion is necessary.
    Parameters:
        article_id (int) - set “checked” to true if specified article id has
        returned label.
    '''
    pass


def setArticleLabel():
    '''
    (since API level 1)
    Assigns article_ids to specified label.
    Parameters:
        article_ids - comma-separated list of article ids
        label_id (int) - label id, as returned in getLabels
        assign (boolean) - assign or remove label
    Note: Up until version:1.15 setArticleLabel() clears the label cache for
    the specified articles. Make sure to regenerate it (e.g. by calling API
    method getLabels() for the respecting articles) when you’re using methods
    which don’t do that by themselves (e.g. getHeadlines()) otherwise
    getHeadlines() will not return labels for modified articles.
    '''
    pass


def shareToPublished():
    '''
    (since API level 4 - version:1.6.0)
    Creates an article with specified data in the Published feed.
    Parameters:
        title - Article title (string)
        url - Article URL (string)
        content - Article content (string)
    '''
    pass


def subscribeToFeed():
    '''
    (API level 5 - version:1.7.6)
    Subscribes to specified feed, returns a status code. See
    subscribe_to_feed() in functions.php for details.
    Parameters:
        feed_url - Feed URL (string)
        category_id - Category id to place feed into (defaults to 0,
            Uncategorized) (int)
        login, password - Self explanatory (string)
    '''
    pass


def unsubscribeFeed():
    '''
    (API level 5 - version:1.7.6)
    Unsubscribes specified feed.
    Parameters:
        feed_id - Feed id to unsubscribe from
    '''
    pass


def getFeedTree():
    '''
    (API level 5 - version:1.7.6)
    include_empty (bool) - include empty categories
    Returns full tree of categories and feeds.
    Note: counters for most feeds are not returned with this call for
    performance reasons.
    '''
    pass


def test():
    user = input("User: ")
    password = getpass.getpass("Password: ")
    login(user, password)
    logout()


if __name__ == '__main__':
    test()
