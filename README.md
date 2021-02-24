# Footlocker-Order-Checker
An easy script to scrape all infos from an order by APU#0001

What is supported ? 

- Image Scraping 
- Product Scraping 
- Order Date Scraping 
- Order Status
- Carrier Scraping 
- Tracking Scraping
- Proxy Support 
- Response status code stuff 
- Shipment status Scraping 


How to setup it? 

- Open config.json file and put your webhook
- Open tasks.csv file in footlocker folder and put your Order Numbers
- Open proxy.txt file in footlocker folder if you are planning to check more than 1 order at the same time, put your proxies ( if you wanna run proxyless just leave empty it ) 


How to run it?

- Open main.py file and run it


**ERROR**

- Error scraping [403] = Banned from footlocker, use proxies
- Error scraping [200] = Order not found, double check your order number



**REQUIREMENTS**

- Python 3.7.9 (or more) with requests, cloudscraper, colorlog library




IF YOU NEED HELP JUST DM ME ON DISCORD ( APU#0001 ) or on twitter @swagapu
© 2021 GitHub, Inc.
