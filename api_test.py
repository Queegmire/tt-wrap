from ttwrap import *
import getpass
import config


def tree_build(root, id, label, depth=0):
    pad = " " * depth
    for item in root:
        t, i = item['id'].split(':')
        print(pad, t, item[label])
        temp = item.copy()
        temp.pop('items', '')
        print(pad, "*", temp.keys())
        if t == 'CAT':
            tree_build(item['items'], id, label, depth + 1)


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
    print("Cached version:", session._version)
    print("Version: ", session.version)
    print("Cached version:", session._version)
    print("Unread: ", session.unread)

    tree_data = session.getFeedTree(True)
    identifier = tree_data['categories']['identifier']
    label = tree_data['categories']['label']
    tree_build(tree_data['categories']['items'], identifier, label)

    session.logout()


if __name__ == '__main__':
    main()
