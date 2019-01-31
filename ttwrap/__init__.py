import requests
import json


class TTSession(object):
    '''Holds the state for the current TT-RSS session

    Special feed IDs are as follows:
        -1 starred
        -2 published
        -3 fresh
        -4 all articles
        0 - archived
        IDs < -10 labels
    Special category IDs are as follows:
        0 Uncategorized
        -1 Special (e.g. Starred, Published, Archived, etc.)
        -2 Labels
        -3 All feeds, excluding virtual feeds (e.g. Labels and such)
        -4 All feeds, including virtual feeds
    '''

    def __init__(self, URL, user, password):
        '''Logs in and populates basic session info'''
        self.sid = ""
        self.URL = URL
        self._error = ""
        self._login(user, password)
        self._version = None
        self._apiLevel = None

    def _login(self, user, password):
        '''Attempt login with saved credentials'''
        apiData = {"user": user, "password": password}
        response = self.callAPI("login", apiData)
        if 'error' in response['content'].keys():
            # rrjtodo: should this be an exception
            self._error = response['content']['error']
            return None
        self.sid = response['content']['session_id']
        return self.sid

    def logout(self):
        '''Logout code

        rrjtodo: should this be called in __del__?
        '''
        response = self.callAPI("logout")
        self.sid = ""

    def callAPI(self, operation, data={}):
        '''Makes the call to the underlying API

        Takes an operation and its coresponding data, adds the current sessin
        sid and passes the json object to the API via requests.
        '''
        data["op"] = operation
        data["sid"] = self.sid
        response = requests.post(self.URL, json=data)
        return json.loads(response.text)

    @property
    def apiLevel(self):
        if not self._apiLevel:
            response = self.callAPI("getApiLevel")
            self._apiLevel = response['content']['level']
        return self._apiLevel

    @property
    def version(self):
        if not self._version:
            response = self.callAPI("getVersion")
            self._version = response['content']['version']
        return self._version

    @property
    def loggedIn(self):
        response = self.callAPI("isLoggedIn")
        return response['content']['status']

    @property
    def unread(self):
        response = self.callAPI("getUnread")
        return response['content']['unread']

    def getCounters(self):
        '''get counters for all feeds, labels and categories

        rrjtodo: api documentation doesn't match underlying code. Seems to have
        been added for tt-rss android app, can probably remove from this wrapper
        '''
        data = {}
        response = self.callAPI("getCounters", data)
        return response['content']

    def getFeedTree(self, include_empty):
        '''Returns a complete tree of categories and feeds

        Only special categories have unread counts for performance reasons.
        root of tree is in the list ['categories']['items']
        '''
        data = {'include_empty': include_empty}
        response = self.callAPI("getFeedTree", data)
        return response['content']

    def getFeeds(self, cat_id, unread_only, limit, offset, include_nested):
        '''Returns a list of feeds with counts

        limit = 0 -> all feeds (offset ignored)
        '''
        data = {'cat_id': cat_id, 'unread_only': unread_only,
                'limit': limit, 'offset': offset,
                'include_nested': include_nested}
        response = self.callAPI("getFeeds", data)
        return response['content']

    def getCategories(self, unread_only, enable_nested, include_empty):
        '''Returns a list of categories with unread counts

        Includes (-1)Special and (-2)Labels categories
        unread_only: bool - only return categories with unread feeds
        enable_nested: bool - nested mode only returns top level
            useful for populating top level only for collapsed UI
        include_empty: include categories with no feeds
        '''
        data = {'unread_only': unread_only, 'enable_nested': enable_nested,
                'include_empty': include_empty}
        response = self.callAPI("getCategories", data)
        return response['content']

    def getHeadlines(self, feed_id, view_mode='unread', show_excerpt=True,
                     show_content=True):
        '''
        Parameters:
            feed_id: Int - feed to enumerate
            view_mode: String - all_articles, unread, adaptive, marked, updated
            show_excerpt: Bool - include article excerpt in the output
            show_content: Bool - include full article text in the output
            ============== rrjtodo: which of the below should be supported
            is_cat: Bool - requested feed_id is a category
            include_attachments: Bool - include article attachment
            since_id: Int - returns articles with id greater than since_id
            include_nested: Bool - include articles from child categories
            order_by: String - override default sort order:
                date_reverse (oldest first), feed_dates (newest first)
            sanitize: Bool:true - sanitize content
            has_sandbox: Bool:false - indicate support of sandboxing of iframes
            include_header: Bool - adds status information when returning
                instead of array(articles) -> array(header, array(articles))
            search: String - search query (e.g. a list of keywords)
            search_mode: String - all_feeds, this_feed (default),
                this_cat (category containing requested feed)
            limit: Int - number of articles to return (0?)
            skip: Int - Offset for enumeration
            force_update: bool:false - update feed before showing headlines
        '''
        data = {'feed_id': feed_id, 'view_mode': view_mode, 
                'show_excerpt': show_excerpt, 'show_content': show_content}
        response = self.callAPI("getHeadlines", data)
        return response['content']

    def updateArticle(self, article_ids, mode, field, note=""):
        '''
        article_ids  - comma-separated list of article IDs
        mode (integer) - (0 - set to false, 1 - set to true, 2 - toggle)
        field (integer) - (0 - starred, 1 - published, 2 - unread, 3 - note
        data (string) - data parameter when setting note field
        '''
        data = {'article_ids': article_ids, 'mode': mode, 'field': field,
                'data': note}
        response = self.callAPI("updateArticle", data)
        return response['content']

    def getArticle(self, article_id):
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
        data = {'feed_id': feed_id}
        response = self.callAPI("updateFeed", data)
        return response['content']

    def getPref(self, pref_name):
        data = {'pref_name': pref_name}
        response = self.callAPI("getPref", data)
        return response['content']

    def catchupFeed(self, feed_id, is_cat=False):
        '''Tries to catchup (e.g. mark as read) specified feed.'''
        data = {'feed_id': feed_id, 'is_cat': is_cat}
        response = self.callAPI("catchupFeed", data)
        return response['content']

    def getLabels(self, article_id=0):
        '''
        rrj - is default article_id of 0 safe?
        Returns list of configured labels, as an array of label objects:
            {"id":2,"caption":"Debian","fg_color":"#e14a00",
                "bg_color":"#ffffff","checked":false},
        Parameters:
            article_id (int) - checked=true if specified article has label.
        '''
        data = {'article_id': article_id}
        response = self.callAPI("getLabels", data)
        return response['content']

    def setArticleLabel(self, article_ids, label_id, assign=True):
        data = {'article_ids': article_ids, 'label_id': label_id,
                'assign': assign}
        response = self.callAPI("setArticleLabel", data)
        return response['content']

    def shareToPublished(self, title, url, content):
        data = {'title': title, 'url': url,
                'content': content}
        response = self.callAPI("shareToPublished", data)
        return response['content']

    def subscribeToFeed(self, feed_url, category_id=0):
        data = {'feed_url': feed_url, 'category_id': category_id}
        response = self.callAPI("subscribeToFeed", data)
        return response['content']

    def unsubscribeFeed(self, feed_id):
        data = {'feed_id': feed_id}
        response = self.callAPI("unsubscribeFeed", data)
        return response['content']


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
        # 'auxcounter','unread=unread', 'child_unread',
        pass

    def __repr__(self):
        return f'{self.title} ({self.unread})'


class TTFeed(dict): 
    {
        "feed_url": "http://feeds2.feedburner.com/rsspect/fJur",
        "id": 27,
        "unread": 0,
        "has_icon": true,
        "cat_id": 1,
        "last_updated": 1539065812,
        "order_id": 4
    },
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
