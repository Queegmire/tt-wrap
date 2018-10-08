from ttwrap import *
import getpass
from config import Config


def tree_build(root, depth=0, unread=False):
    pad = " " * depth
    for item in root:
        t, i = item['id'].split(':')
        if t == 'CAT':
            print(pad, '+', item['name'])
            tree_build(item['items'], depth + 2)
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
    tree_data = session.getFeedTree(True)
    print(session.updateArticle(134311, 2, 3, "foo"))
    for item in session.getHeadlines(-4):
        #print(item.keys())
        print(f"#{item['id']}: {item['title']} ({item['feed_title']})")
    # tree_build(tree_data['categories']['items'])
    # for item in session.getCounters(output_mode='flc'):
    #     print(item)
    session.logout()


if __name__ == '__main__':
    main()
