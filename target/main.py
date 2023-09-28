import os

# This main file is used for scraping multiple products urls. Using list, exel, json or passing through the pandas
urls = ["https://www.target.com/p/-/A-79344798", "https://www.target.com/p/-/A-13493042", "https://www.target.com/p/-/A-85781566"]
for url in urls:
    os.system("scrapy crawl target_spider -a ProductUrl={}".format(url))

