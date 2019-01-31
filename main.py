from ttwrap import *
import getpass
from config import Config


def tree_build(root, *, depth=0):
    pad = " " * depth
    for item in root:
        t, i = item['id'].split(':')
        if t == 'CAT':
            print(f'{pad}+ {item["name"]} ({item["unread"]})')
            tree_build(item['items'], depth=depth + 2)
        else:
            print(f'{pad}- {item["name"]} ({item["unread"]})')


def main():
    if Config.USERNAME:
        user = Config.USERNAME
    else:
        user = input("User: ")

    if Config.PASSWORD:
        password = Config.PASSWORD
    else:
        password = getpass.getpass("Password: ")

    if Config.URL_ROOT:
        apiURL = Config.URL_ROOT
    else:
        apiURL = input("URL: ")

    session = TTSession(apiURL, user, password)
    print("Version: ", session.version)
    print("Unread: ", session.unread)
#    tree_data = session.getFeedTree(True)
#    print(session.updateArticle(117472, 2, 2, "foo"))
#    for item in session.getHeadlines(-4):
#        print(f"#{item['id']}: {item['title']} ({item['feed_title']})")
#    tree_build(tree_data['categories']['items'])
    temp = session.getFeeds(-3, False, 10, 0, True)
    print(json.dumps(temp, indent=4))
    print(len(temp))
#    print(json.dumps(session.getCategories(False, False, True), indent=4))
    session.logout()


if __name__ == '__main__':
    main()
