import sys, logging, urllib3, json, requests, csv, os, random, time, datetime, threading
from mods.logger import Logger
from mods.utils import JKTools
from pypresence import Presence
from colorama import Fore, init
init(convert=True, autoreset=True)

log = Logger()
#disable all log
urllib3.disable_warnings()
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)

version = '0.0.1'
rpc = {'status':'In the menu...'}
threads = {}
open('JK.log', 'w').write('')

def richPresence():
    try:
        client = '769955229461643304'
        RPC = Presence(client_id=client)
        RPC.connect()
        start = int(time.time())

        def rich():
            try:
                while True:
                    RPC.update(large_image='large', large_text='@JK', state=f'Version {version}', details=rpc['status'], start=start)
                    time.sleep(15)
            except:
                pass

        threading.Thread(target=rich).start()
    except:
        pass

richPresence()

def writeJSON(obj, wPath):
    path = os.path.join(os.path.dirname(sys.argv[0]), wPath)
    json.dump(obj, open(path, 'w'), indent=4)

def getInput(choice):
    path = os.path.join(os.path.dirname(sys.argv[0]), 'JK.log')
    asctime = str(datetime.datetime.now()).replace('.', ',')[:-3]
    print (f'[{asctime}] {Fore.YELLOW}{choice}: ', end='')
    open(path, 'a').write(f'{asctime} : {choice}: \n')

class mainFlow():

    def __init__(self):
        log.info(f'Welcome in APUtool - {version}')
        self.startBot()


    def startBot(self):


        log.warning(f'1. FootlockerEU order checker')
        getInput('Your choice: ')

        mode = input().strip()

        if mode == '1':
            
            from footlockerchecker import Footlockerchecker

            try:
                configPath = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')
                config = json.load(open(configPath))
                path = os.path.join(os.path.dirname(sys.argv[0]), 'footlockerchecker/tasks.csv')
                csvTasks = csv.DictReader(open(path, 'r'))
                activeTasks = []

                for i, row in enumerate(csvTasks):

                    ordernumber = row['ORDERNUMBER']

                    log.warning(f'[Task {str(i)}] Starting...')
                    t = threading.Thread(target=Footlockerchecker, args=(ordernumber, config, str(i)))
                    activeTasks.append(t)
                    t.start()

                rpc['status'] = 'Checking some orders...'
                log.info('All task(s) started!')
                for t in activeTasks:
                    try:
                        t.join()
                    except:
                        pass

                self.startBot()

            except Exception as e:
                log.error(f'Failed to read tasks: {str(e)}')



        else:
            log.error('Invalid choice!')
            self.startBot()


main = threading.Thread(target=mainFlow)
main.start()
