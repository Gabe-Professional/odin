from odin.collect.hootsuite_api import get_creds
import requests

def main():
    creds = get_creds()
    c = creds['client']
    s = creds['secret']
    ep = creds['endpoint']
    print(c, s, ep)

    r = requests.get(creds['endpoint'], auth=(creds['client'], creds['secret']))

    print(r.status_code)

if __name__ == '__main__':
    main()