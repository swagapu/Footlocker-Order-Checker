import os, sys, requests, time, datetime, logging, csv

logging.getLogger('requests').setLevel(logging.ERROR)

class JKTools():

    def __init__(self, log):
        self.log = log

    def loadProxies(self, proxies):

        if proxies.endswith('\n') == True:
            proxies = proxies.rstrip('\n')

        proxylist = []
        proxies = proxies.split('\n')

        for proxy in proxies:
            spl = proxy.split(':')

            if len(spl) == 2:

                prx =  {
                    'http': f'http://{prx}', 
                    'https': f'https://{prx}'
                    }
                
            elif len(spl) == 4:

                prx =  {
                    'http': 'http://{}:{}@{}:{}'.format(spl[2], spl[3], spl[0], spl[1]),
                    'https': 'https://{}:{}@{}:{}'.format(spl[2], spl[3], spl[0], spl[1])
                }

            proxylist.append(prx)

        return proxylist