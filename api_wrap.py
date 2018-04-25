import requests
import getpass
import json
import config
from pprint import pprint as pp


class TTFeed(dict):
    """docstring for TTFeed"""

    def __init__(self, id, feed_data={}):
        self.id = id
        self.data = {}
        self.update(feed_data)

    def update(self, feed_data):
        self.data.update(feed_data)

    @property
    def title(self):
        return self.data['title']

    @property
    def unread(self):
        return self.data['unread']

    def __repr__(self):
        return f'{self.title} ({self.unread})'


class TTCategory(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title

    def set_stat(self, cat_data):
        self.unread = cat_data['unread']
        if 'order_id' in cat_data:
            self.order_id = cat_data['order_id']

    def set_dyn(self, cat_data):
        # 'bare_id', 'name?title', 'type', 'checkbox', 'param'
        'auxcounter','unread=unread', 'child_unread',  
    def __repr__(self):
        return f'{self.title} ({self.unread})'


class TTSession(object):
    """docstring for TTRSSSession"""

    def __init__(self, URL, user, password):
        self.sid = ""
        self.URL = URL
        self._login(user, password)

    def _login(self, user, password):
        apiData = {"user": user, "password": password}
        response = self.callAPI("login", apiData)
        self.sid = response['content']['session_id']
        return self.sid

    def logout(self):
        response = self.callAPI("logout")
        self.sid = ""

    def callAPI(self, operation, data={}):
        data["op"] = operation
        data["sid"] = self.sid
        response = requests.post(self.URL, json=data)
        return json.loads(response.text)

    @property
    def apiLevel(self):
        response = self.callAPI("getApiLevel")
        return response['content']['level']

    @property
    def version(self):
        response = self.callAPI("getVersion")
        return response['content']['version']

    @property
    def loggedIn(self):
        response = self.callAPI("isLoggedIn")
        return response['content']['status']

    @property
    def unread(self):
        response = self.callAPI("getUnread")
        return response['content']['unread']

    def getCounters(self):
        data = {}
        response = self.callAPI("getCounters", data)
        return response['content']

    def getFeedTree(self, include_empty):
        '''
        include_empty (bool) - include empty categories
        Returns full tree of categories and feeds.
        Note: counters for most feeds are not returned with this call for
        performance reasons.
        '''
        data = {'include_empty': include_empty}
        response = self.callAPI("getFeedTree", data)
        return response['content']

    def getFeeds(self, cat_id, unread_only, limit, offset, include_nested):
        '''
        limit = 0 -> all feeds (offset ignored)
        Special category IDs are as follows:
            0 Uncategorized
            -1 Special (e.g. Starred, Published, Archived, etc.)
            -2 Labels
            -3 All feeds, excluding virtual feeds (e.g. Labels and such)
            -4 All feeds, including virtual feeds
        '''
        data = {'cat_id': cat_id, 'unread_only': unread_only,
                'limit': limit, 'offset': offset,
                'include_nested': include_nested}
        response = self.callAPI("getFeeds", data)
        return response['content']

    def getCategories(self, unread_only, enable_nested, include_empty):
        '''
        Nested means that a flat list of only topmost categories is returned.
        This should be used as a starting point, to display a root list of all
        or topmost categories, use getFeeds to traverse deeper.
        '''
        data = {'unread_only': unread_only, 'enable_nested': enable_nested,
                'include_empty': include_empty}
        response = self.callAPI("getCategories", data)
        return response['content']

    def getHeadlines(self, feed_id):
        '''
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
        data = {'feed_id': feed_id}
        response = self.callAPI("getHeadlines", data)
        return response['content']

    def updateArticle(self, article_ids, mode, field, note=""):
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
        data = {'article_ids': article_ids, 'mode': mode, 'field': field,
                'note': 123}
        response = self.callAPI("updateArticle", data)
        return response['content']

    def getArticle(self, article_id):
        '''
        Requests JSON-encoded article object with specific ID.
        article_id (integer) - article ID to return as of 15.10.2010 git or
            version:1.5.0 supports comma-separated list of IDs
        Since version:1.4.3 also returns article attachments.
        '''
        data = {'article_id': article_id}
        response = self.callAPI("getArticle", data)
        return response['content']

    def getConfig(self):
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
        response = self.callAPI("getConfig", {})
        return response['content']

    def updateFeed(self, feed_id):
        '''
        Tries to update specified feed. This operation is not performed in the
        background, so it might take considerable time and, potentially, be aborted
        by the HTTP server.
        feed_id (integer) - ID of feed to update
        Returns status-message if the operation has been completed.
            {"status":"OK"}
        '''
        data = {'feed_id': feed_id}
        response = self.callAPI("updateFeed", data)
        return response['content']

    def getPref(self, pref_name):
        '''
        Returns preference value of specified key.
        pref_name (string) - preference key to return value of
            {"value":true}
        '''
        data = {'pref_name': pref_name}
        response = self.callAPI("getPref", data)
        return response['content']

    def catchupFeed(self, feed_id, is_cat=False):
        '''
        Required version: version:1.4.3
        Tries to catchup (e.g. mark as read) specified feed.
        Parameters:
            feed_id (integer) - ID of feed to update
            is_cat (boolean) - true if the specified feed_id is a category
        Returns status-message if the operation has been completed.
            {"status":"OK"}
        '''
        data = {'feed_id': feed_id, 'is_cat': is_cat}
        response = self.callAPI("catchupFeed", data)
        return response['content']

    def getLabels(self, article_id=0):
        '''
        rrj - is default article_id of 0 safe?
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
        data = {'article_id': article_id}
        response = self.callAPI("getLabels", data)
        return response['content']

    def setArticleLabel(self, article_ids, label_id, assign=True):
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
        data = {'article_ids': article_ids, 'label_id': label_id,
                'assign': assign}
        response = self.callAPI("setArticleLabel", data)
        return response['content']

    def shareToPublished(self, title, url, content):
        '''
        (since API level 4 - version:1.6.0)
        Creates an article with specified data in the Published feed.
        Parameters:
            title - Article title (string)
            url - Article URL (string)
            content - Article content (string)
        '''
        data = {'title': title, 'url': url,
                'content': content}
        response = self.callAPI("shareToPublished", data)
        return response['content']

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


def tree_build(root, id, label, depth=0):
    pad = " " * depth
    for item in root:
        t, i = item['id'].split(':')
        # print(pad, t, i)
        print(pad, t, item[label])
        # print(pad, item.keys())
        temp = item.copy()
        temp.pop('items', '')
        print(pad, "*", temp.keys())
        if t == 'CAT':
            tree_build(item['items'], id, label, depth + 1)
            # print(pad, len(item['items']))


def main():
    if config.user:
        user = config.user
    else:
        user = input("User: ")

    if config.password:
        password = config.password
    else:
        password = getpass.getpass("Password: ")

    if config.url:
        apiURL = config.url
    else:
        apiURL = input("URL: ")

    session = TTSession(apiURL, user, password)
    print("Version: ", session.version)
    print("Unread: ", session.unread)

    tree_data = session.getFeedTree(True)

    identifier = tree_data['categories']['identifier']
    label = tree_data['categories']['label']

    tree_build(tree_data['categories']['items'], identifier, label)

    session.logout()


if __name__ == '__main__':
    main()
