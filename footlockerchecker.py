import sys, logging, urllib3, json, requests, csv, os, random, time, datetime, threading
from requests.exceptions import ProxyError, ConnectionError, Timeout
from mods.utils import JKTools

log = logging.getLogger('main.log')

tools = JKTools(log)

def writeJSON(obj, wPath):
    path = os.path.join(os.path.dirname(sys.argv[0]), wPath)
    json.dump(obj, open(path, 'w'), indent=4)

class Footlockerchecker():

    def __init__(self, ordernumber, config, i):

        self.s = requests.Session()
        self.ordernumber = ordernumber
        self.config = config
        self.i = i
        self.delay = int(config['DELAY'])
        self.s = cloudscraper.create_scraper(captcha={'provider':'2captcha','api_key':config['2CAPTCHA']})

        try:
            proxiesPath = os.path.join(os.path.dirname(sys.argv[0]), 'footlockerchecker/proxies.txt')
            proxies = open(proxiesPath, 'r').read()
        except Exception as e:
            self.error(f'Failed to reading proxies: {str(e)}')
            sys.exit()

        if proxies == '':
            self.proxylist = ''
        else:
            self.proxylist = tools.loadProxies(proxies)

        self.mainheaders = {
            'authority': 'footlocker.narvar.com',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="86", "\\"Not\\\\A;Brand";v="99", "Google Chrome";v="86"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'it,en-US;q=0.9,en;q=0.8',
        }
                
        
        self.trackresultheaders = {}

        self.atcheaders = {}


        self.info('Started!')
        self.start()

    def info(self, string):
        log.info(f'[Task {self.i}] [Footlocker EU Checker] {string}')
    
    def warn(self, string):
        log.warning(f'[Task {self.i}] [FootLocker EU Checker] {string}')

    def error(self, string):
        log.error(f'[Task {self.i}] [FootLocker EU Checker] {string}')

    def chooseProxy(self):
        if self.proxylist == '':
            return None

        else:
            return random.choice(self.proxylist)


    def start(self):
        while 1:
            try:

                self.params = (
                    ('order_number', self.ordernumber),
                )

                self.pagecreate = f"https://footlocker.narvar.com/tracking/itemvisibility/v1/footlocker/orders/{self.ordernumber}?order_number={self.ordernumber}&tracking_url=https://footlocker.narvar.com/footlocker/tracking/uk-mail?order_number={self.ordernumber}"
                self.link = f"https://footlocker.narvar.com/footlocker/tracking/uk-mail?order_number={self.ordernumber}"
                productPage = requests.get(self.pagecreate, headers=self.mainheaders, params=self.params, proxies=self.chooseProxy(), timeout=10)
                status_code = productPage.status_code

                try:
                    self.warn('Checking order..')
                    data = json.loads(productPage.text)
                    self.status = data['status']

                    if self.status == 'SUCCESS':

                        self.image = data['order_info']['order_items'][0]
                        self.itemimage1 = self.image['item_image']
                        self.itemimage2 = self.itemimage1.replace("//", "")
                        self.itemimage = self.itemimage2.replace("?wid=232&hei=232", "")

                        self.pid = self.itemimage.replace("images.footlocker.com/is/image/FLEU/", "")

                        self.name = data['order_info']['order_items'][0]
                        self.itemname = self.name['name']

                        self.orderdate = data['order_info']['order_date']

                        self.order_items = data['order_info']['order_items'][0]
                        self.orderstatus = self.order_items['fulfillment_status']
                        self.info('Order status: ' + self.order_items['fulfillment_status'])

                        if self.orderstatus == 'PROCESSING':
                            self.webhookprocessing()
                            break

                        if self.orderstatus == 'SHIPPED' or 'RETURNED':

                            self.carrier1 = data['order_info']['shipments'][0]
                            self.carrier = self.carrier1['carrier']

                            self.tracking = data['order_info']['shipments'][0]
                            self.trackignumber = self.tracking['tracking_number']


                            if self.carrier == 'brt_parcelid':
                                self.statusship1 = data['order_info']['shipments'][0]
                                self.statuship = self.statusship1['status']

                                self.trackignumber = self.statusship1['tracking_number']
                                self.trackinglink = f'https://vas.brt.it/vas/sped_det_show.hsm?referer=sped_numspe_par.htm&Nspediz={self.trackignumber}'
                            
                                self.webhookbartolini()
                                break
            
                            if self.carrier == 'ups':

                                self.statusship1 = data['order_info']['shipments'][0]
                                self.statuship = self.statusship1['status']
                                self.trackinglink = f'https://www.ups.com/track?loc=en_US&tracknum={self.trackignumber}&requester=WT/trackdetails'
                                self.webhookups()
                                break

                            if self.carrier == 'hrm':

                                self.trackinglink = f'https://www.myhermes.co.uk/track#/parcel/{self.trackignumber}/details'
                                self.webhookhermes()
                                break
                        



                        self.webhookgeneral()
                        break



                    else:
                        self.error(f'Error getting order: [{str(productPage.status_code)}]')
                        self.webhookfail()
                        break

                except:
                    self.error(f'Error undefined: [{str(productPage.status_code)}]')
                    break

            except Exception as e:
                self.error(f'Error diocane: {str(e)}')
                time.sleep(self.delay)
                break



    def webhookgeneral(self):
        
        try:

            self.warn('Sending Webhook..')

            webhookheaders = {
                'authority': 'discord.com',
                'sec-ch-ua': '"Chromium";v="86", "\\"Not\\\\A;Brand";v="99", "Google Chrome";v="86"',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                'content-type': 'application/json; charset=UTF-8',
                'origin': 'https://discord.club',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://discord.club/',
                'accept-language': 'it,en-US;q=0.9,en;q=0.8',
            }

        
            self.webhook = self.config['WEBHOOK']
            payload = {}
            payload['embeds'] = []
            embed = {}
            embed['fields'] = []
            embed['title'] = f'**ORDER SUCCESSFULLY CHECKED**'
            embed['url'] = self.link
            embed['color'] = 55552
            embed['thumbnail'] = {'url': f'https://images.footlocker.com/is/image/FLEU/{self.pid}.png'}
            embed['footer'] = {'text': 'FootLocker Order Checker by APU'}
            embed['fields'].append({'name': '**ITEM NAME**', 'value': self.itemname, 'inline':True})
            embed['fields'].append({'name': '**ORDER DATE**', 'value': self.orderdate})
            embed['fields'].append({'name': '**STATUS**', 'value': self.orderstatus})
            embed['fields'].append({'name': '**ORDER NUMBER**', 'value': f'||{self.ordernumber}||', 'inline':True})
            embed['fields'].append({'name': '**CARRIER**', 'value': self.carrier})
            embed['fields'].append({'name': '**TRACKING NUMBER**', 'value': f'||{self.trackignumber}||'})            
 
            payload['embeds'].append(embed)
 
            r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
            if r.status_code == 200 or 302:
                self.info('Webhoook successfully sent !')
            else:
                self.error('Fail while sending webhook !')
            while r.status_code == 429:
                r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
                self.error('Webhook Rate Limit !')
                break


        except Exception as e:
            self.error(f'Webhook error: {str(e)}')


    def webhookfail(self):
        
        try:

            self.warn('Sending Webhook..')

            webhookheaders = {
                'authority': 'discord.com',
                'sec-ch-ua': '"Chromium";v="86", "\\"Not\\\\A;Brand";v="99", "Google Chrome";v="86"',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                'content-type': 'application/json; charset=UTF-8',
                'origin': 'https://discord.club',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://discord.club/',
                'accept-language': 'it,en-US;q=0.9,en;q=0.8',
            }

        
            self.webhook = self.config['WEBHOOK']
            payload = {}
            payload['embeds'] = []
            embed = {}
            embed['fields'] = []
            embed['title'] = f'**FAIL WHILE SEARCHING ORDER**'
            embed['url'] = self.link
            embed['color'] = 0xFF0000
            embed['thumbnail'] = {'url': 'https://impresaformazioneoccupazione.it/wp-content/uploads/2018/08/Foot-Locker-ricerca-personale-in-Veneto.png'}
            embed['footer'] = {'text': 'FootLocker Order Checker by APU'}
            embed['fields'].append({'name': '**REASON**', 'value': 'Your Order does not exist, double check order number'})
            embed['fields'].append({'name': '**ORDER NUMBER**', 'value': f'||{self.ordernumber}||', 'inline':True})

            
 
            payload['embeds'].append(embed)
 
            r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
            if r.status_code == 200 or 302:
                self.info('Webhoook successfully sent !')
                
            else:
                self.error('Fail while sending webhook !')
            while r.status_code == 429:
                r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
                self.error('Webhook Rate Limit !')
                break
 
        except Exception as e:
            self.error(f'Webhook error: {str(e)}')


    def webhookprocessing(self):

        try:

            self.warn('Sending Webhook..')

            webhookheaders = {
                'authority': 'discord.com',
                'sec-ch-ua': '"Chromium";v="86", "\\"Not\\\\A;Brand";v="99", "Google Chrome";v="86"',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                'content-type': 'application/json; charset=UTF-8',
                'origin': 'https://discord.club',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://discord.club/',
                'accept-language': 'it,en-US;q=0.9,en;q=0.8',
            }

        
            self.webhook = self.config['WEBHOOK']
            payload = {}
            payload['embeds'] = []
            embed = {}
            embed['fields'] = []
            embed['title'] = f'**ORDER SUCCESSFULLY CHECKED**'
            embed['url'] = self.link
            embed['color'] = 55552
            embed['thumbnail'] = {'url': f'https://images.footlocker.com/is/image/FLEU/{self.pid}.png'}
            embed['footer'] = {'text': 'FootLocker Order Checker by APU'}
            embed['fields'].append({'name': '**ITEM NAME**', 'value': self.itemname, 'inline':True})
            embed['fields'].append({'name': '**ORDER NUMBER**', 'value': f'||{self.ordernumber}||'})
            embed['fields'].append({'name': '**ORDER DATE**', 'value': self.orderdate})
            embed['fields'].append({'name': '**ORDER STATUS**', 'value': self.orderstatus})

 
            payload['embeds'].append(embed)
            time.sleep(1)
            r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
            if r.status_code == 200 or 302:
                self.info('Webhoook successfully sent !')
            else:
                self.error('Fail while sending webhook !')
            while r.status_code == 429:
                r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
                self.error('Webhook Rate Limit !')
                break
 
        except Exception as e:
            self.error(f'Webhook error: {str(e)}')




    def webhookbartolini(self):
        
        try:

            self.warn('Sending Webhook..')

            webhookheaders = {
                'authority': 'discord.com',
                'sec-ch-ua': '"Chromium";v="86", "\\"Not\\\\A;Brand";v="99", "Google Chrome";v="86"',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                'content-type': 'application/json; charset=UTF-8',
                'origin': 'https://discord.club',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://discord.club/',
                'accept-language': 'it,en-US;q=0.9,en;q=0.8',
            }

        
            self.webhook = self.config['WEBHOOK']
            payload = {}
            payload['embeds'] = []
            embed = {}
            embed['fields'] = []
            embed['title'] = f'**ORDER SUCCESSFULLY CHECKED**'
            embed['url'] = self.link
            embed['color'] = 55552
            embed['thumbnail'] = {'url': f'https://images.footlocker.com/is/image/FLEU/{self.pid}.png'}
            embed['footer'] = {'text': 'FootLocker Order Checker by APU'}
            embed['fields'].append({'name': '**ITEM NAME**', 'value': self.itemname, 'inline':True})
            embed['fields'].append({'name': '**ORDER NUMBER**', 'value': f'||{self.ordernumber}||'})
            embed['fields'].append({'name': '**ORDER DATE**', 'value': self.orderdate})
            embed['fields'].append({'name': '**ORDER STATUS**', 'value': self.orderstatus})
            embed['fields'].append({'name': '**CARRIER**', 'value': 'BRT'})
            embed['fields'].append({'name': '**TRACKING**', 'value': f'||[{self.trackignumber}]({self.trackinglink})||'}) 
            embed['fields'].append({'name': '**SHIPMENT STATUS**', 'value': self.statuship})      
 
            payload['embeds'].append(embed)
 
            r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
            if r.status_code == 200 or 302:
                self.info('Webhoook successfully sent !')
            else:
                self.error('Fail while sending webhook !')
            while r.status_code == 429:
                r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
                self.error('Webhook Rate Limit !')
                break
 
        except Exception as e:
            self.error(f'Webhook error: {str(e)}')



    def webhookups(self):
        
        try:

            self.warn('Sending Webhook..')

            webhookheaders = {
                'authority': 'discord.com',
                'sec-ch-ua': '"Chromium";v="86", "\\"Not\\\\A;Brand";v="99", "Google Chrome";v="86"',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                'content-type': 'application/json; charset=UTF-8',
                'origin': 'https://discord.club',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://discord.club/',
                'accept-language': 'it,en-US;q=0.9,en;q=0.8',
            }

        
            self.webhook = self.config['WEBHOOK']
            payload = {}
            payload['embeds'] = []
            embed = {}
            embed['fields'] = []
            embed['title'] = f'**ORDER SUCCESSFULLY CHECKED**'
            embed['url'] = self.link
            embed['color'] = 55552
            embed['thumbnail'] = {'url': f'https://images.footlocker.com/is/image/FLEU/{self.pid}.png'}
            embed['footer'] = {'text': 'FootLocker Order Checker by APU'}
            embed['fields'].append({'name': '**ITEM NAME**', 'value': self.itemname, 'inline':True})
            embed['fields'].append({'name': '**ORDER NUMBER**', 'value': f'||{self.ordernumber}||'})
            embed['fields'].append({'name': '**ORDER DATE**', 'value': self.orderdate})
            embed['fields'].append({'name': '**ORDER STATUS**', 'value': self.orderstatus})
            embed['fields'].append({'name': '**CARRIER**', 'value': 'UPS'})
            embed['fields'].append({'name': '**TRACKING**', 'value': f'||[{self.trackignumber}]({self.trackinglink})||'}) 
            embed['fields'].append({'name': '**SHIPMENT STATUS**', 'value': self.statuship})      
 
            payload['embeds'].append(embed)
 
            r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
            if r.status_code == 200 or 302:
                self.info('Webhoook successfully sent !')
            else:
                self.error('Fail while sending webhook !')
            while r.status_code == 429:
                r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
                self.error('Webhook Rate Limit !')
                break
 
        except Exception as e:
            self.error(f'Webhook error: {str(e)}')



    def webhookhermes(self):
        
        try:

            self.warn('Sending Webhook..')

            webhookheaders = {
                'authority': 'discord.com',
                'sec-ch-ua': '"Chromium";v="86", "\\"Not\\\\A;Brand";v="99", "Google Chrome";v="86"',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                'content-type': 'application/json; charset=UTF-8',
                'origin': 'https://discord.club',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://discord.club/',
                'accept-language': 'it,en-US;q=0.9,en;q=0.8',
            }

        
            self.webhook = self.config['WEBHOOK']
            payload = {}
            payload['embeds'] = []
            embed = {}
            embed['fields'] = []
            embed['title'] = f'**ORDER SUCCESSFULLY CHECKED**'
            embed['url'] = self.link
            embed['color'] = 55552
            embed['thumbnail'] = {'url': f'https://images.footlocker.com/is/image/FLEU/{self.pid}.png'}
            embed['footer'] = {'text': 'FootLocker Order Checker by APU'}
            embed['fields'].append({'name': '**ITEM NAME**', 'value': self.itemname, 'inline':True})
            embed['fields'].append({'name': '**ORDER NUMBER**', 'value': f'||{self.ordernumber}||'})
            embed['fields'].append({'name': '**ORDER DATE**', 'value': self.orderdate})
            embed['fields'].append({'name': '**ORDER STATUS**', 'value': self.orderstatus})
            embed['fields'].append({'name': '**CARRIER**', 'value': 'Hermès'})
            embed['fields'].append({'name': '**TRACKING**', 'value': f'||[{self.trackignumber}]({self.trackinglink})||'}) 
 
            payload['embeds'].append(embed)
 
            r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
            if r.status_code == 200 or 302:
                self.info('Webhoook successfully sent !')
            else:
                self.error('Fail while sending webhook !')
            while r.status_code == 429:
                r = requests.post(self.webhook, json=payload, headers=webhookheaders, verify=True)
                self.error('Webhook Rate Limit !')
                break
 
        except Exception as e:
            self.error(f'Webhook error: {str(e)}')







