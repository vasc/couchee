import pymongo
import sys

def main(group):
    db = pymongo.Connection().usenet
    g = {'group': group, 'init': 0, 'end': 0, 'done': True}
    db.control.save(g)

if __name__ == '__main__':
    main(sys.argv[1])
