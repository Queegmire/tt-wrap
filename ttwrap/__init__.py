import requests
import json


class TTSession(object):
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
        '''Nested returns a flat list of only topmost categories'''
        data = {'unread_only': unread_only, 'enable_nested': enable_nested,
                'include_empty': include_empty}
        response = self.callAPI("getCategories", data)
        return response['content']

    def getHeadlines(self, feed_id):
        '''
        Parameters:
            feed_id (integer) - only output articles for this feed
            limit (integer) - limits the amount of returned articles
            skip (integer) - skip this amount of feeds first
            filter (string) - currently unused (?)
            is_cat (bool) - requested feed_id is a category
            show_excerpt (bool) - include article excerpt in the output
            show_content (bool) - include full article text in the output
            view_mode (string) all_articles, unread, adaptive, marked, updated
            include_attachments (bool) - include article attachment
            since_id (integer) - returns articles with id greater than since_id
            include_nested (boolean) - include articles from child categories
            order_by (string) - override default sort order
            sanitize (bool) - sanitize content (default: true)
            force_update (bool) - try to update feed before showing headlines
                (default: false)
            has_sandbox (bool) - indicate support for sandboxing of iframes
                (default: false)
            include_header (bool) - adds status information when returning
                headlines, instead of array(articles) return value changes to
                array(header, array(articles))
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
        article_ids  - comma-separated list of article IDs
        mode (integer) - (0 - set to false, 1 - set to true, 2 - toggle)
        field (integer) - (0 - starred, 1 - published, 2 - unread, 3 - note
        data (string) - data parameter when setting note field
        '''
        data = {'article_ids': article_ids, 'mode': mode, 'field': field,
                'note': 123}
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
