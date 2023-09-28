import scrapy
import re
import json
import requests

answare = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.target.com/p/-/A-79344798?showOnlyQuestions=true',
    'Origin': 'https://www.target.com',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

class TargetSpiderSpider(scrapy.Spider):
    name = 'target_spider'
    allowed_domains = ['target.com']
    start_urls = ['http://target.com/']
    AllQuestionData = []

    # This starting pointing of spider/ or main main function of spider
    def start_requests(self):
        yield scrapy.Request(url=self.ProductUrl, callback=self.GetDetialPage)

    # This function is used to get the total number pages for questions 
    def GetReviewsResponse(self,api_key,product_id):
        params = {
            'key': api_key,
            'page': '0',
            'questionedId': product_id,
            'type': 'product',
            'size': '100',
            'sortBy': 'MOST_ANSWERS',
            'errorTag': 'drax_domain_questions_api_error',
        }
        response = requests.get('https://r2d2.target.com/ggc/Q&A/v1/question-answer', params=params, headers=headers)
        js = response.json()
        if js.get("results"):
            total_pages = js["total_pages"]
            return total_pages
        else:
             return None

    # This function is used for getting product information and questions and answares.
    def GetDetialPage(self, response):            
            items = dict()
            response_data = response.text.replace("\\","").replace("Bu003e","").replace("u003c","")
            product_url = response.css("meta[property='og:url']::attr(content)").get()
            tcin = product_url.split("-")[-1]
            upc = re.findall(',"primary_barcode":"(.*?)",',response_data)
            price = re.findall(',"reg_retail":(.*?),',response_data)
            currency = "USD"
            description = response.xpath("//meta[@name='description']//@content").get()
            specs = ""
            ingredients = []
            bullets = response.css("li[class='styles__Bullet-sc-6aebpn-0 dKfJvU h-padding-t-x2 h-padding-r-tight h-text-md'] span::text").extract()
            product_description = re.findall(',"product_description":(.*?),"downstream_description"',response_data)
            features = json.loads(product_description[0]+"}")["bullet_descriptions"]
            api_key = re.findall('"\}\}\},"apiKey"\:"(.*?)","whatever"\:',response_data)
            items["product_url"] = product_url
            items["tcin"] = tcin if tcin else ""
            items["upc"] = upc[0] if upc else ""
            items["price"] = price[0] if price else ""
            items["currency"] = currency
            items["description"] = description
            items["specs"] = specs
            items["ingredients"] = ingredients
            items["bullets"] = bullets
            items["features"] = features
            pages = self.GetReviewsResponse(api_key[0],tcin)
            QuestsionList = list()
            QuestionItems = dict()
            if pages is not None:
                for page in range(0,pages):
                    params = {
                        'key': api_key[0],
                        'page': page,
                        'questionedId': tcin,
                        'type': 'product',
                        'size': '100',
                        'sortBy': 'MOST_ANSWERS',
                        'errorTag': 'drax_domain_questions_api_error',
                    }

                    response = requests.get('https://r2d2.target.com/ggc/Q&A/v1/question-answer', params=params, headers=headers)
                    js = response.json()
                    
                    if js.get("results"):
                            questionlist = list()
                            for result in js.get("results"):
                                question = dict()
                                ans = list()
                                question["question_id"] = result.get("id")
                                question["submission_date"] = result.get("submitted_at").split("T")[0]
                                question["question_summary"] = result.get("text")
                                question["user_nickname"] = result["author"].get("nickname")
                                if result.get("answers"):
                                    for answer in result.get("answers"):
                                        AnswareItem = dict()
                                        AnswareItem["answer_id"] = answer["id"]
                                        AnswareItem["answer_summary"] = answer["text"]
                                        AnswareItem["submission_date"] = answer["submitted_at"].split("T")[0]
                                        AnswareItem["user_nickname"] = answer["author"].get("nickname")
                                        ans.append(AnswareItem)

                                question["answers"] = ans
                                questionlist.append(question)
                            QuestionItems["questions"] = questionlist

            else:
                items["questions"]=QuestsionList
                print("There is no Question for this product...")

            # It is updating All questions and answare to product information as item and generating a json outout file 
            items.update(QuestionItems)
            f = open('data_ouput.json', 'w')
            json.dump(items, f, indent=4)
            f.close()


                        

                             











        


