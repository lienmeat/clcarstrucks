
from scrapy import Spider, Request
from scrapy.selector import Selector
from urllib.parse import urlencode

class CLCarsTrucks(Spider):
    name = 'CLCarsTrucks'
    #cl url city name
    proto = 'https://'
    domain = 'craigslist.org'

    allowed_search_args = [
        'auto_make_model',
        'auto_title_status',
        'auto_transmission',
        'min_price',
        'max_price',
        'min_auto_miles',
        'max_auto_miles',
        'min_auto_year',
        'max_auto_year',
        'postal',
        'search_distance',
    ]

    # search_page_args = {
    #     'auto_make_model': 'honda fit',
    #     'auto_title_status': '1', #{"1": "clean", "2": "salvage", "3": "rebuilt", "4": "parts only", "5": "lien", "6": "missing"}
    #     'auto_transmission': '2', #{"1": "manual", "2": "automatic", "3": "other"}
    #     'min_price': '300',
    #     'max_price': '100000',
    #     'min_auto_miles': '1000',
    #     'max_auto_miles': '100000',
    #     'min_auto_year': '2011',
    #     'max_auto_year': '2017',
    #     'postal': '98133',
    #     'search_distance': '30'
    # }


    def start_requests(self):
        yield Request(self.proto + self.city + '.' + self.domain + '/search/stn/sss')

    def getSearchArgs(self):
        args = {}
        for a in self.allowed_search_args:
            try:
                val = getattr(self, a)
                if val != '':
                    args[a] = val
            except:
                pass
        return args

    def parse(self, response):
        urls = []
        sargs = self.getSearchArgs()

        args = "&" + urlencode(sargs)
        for i in range(20):
            tn = '?s=' + str(100*i) + args
            urls.append(response.urljoin(tn))
        for url in urls:
            yield Request(url, callback=self.parse_main_page)

    def parse_main_page(self, response):
        links = response.css('li.result-row a.hdrlnk::attr(href)').extract()
        for link in links:
            link = self.proto + self.city + '.' + self.domain + link
            yield Request(link, callback=self.parse_detail_page)

    def parse_detail_page(self, response):
        attrs = []
        try:
            price = response.xpath('//*[@class = "price"]/text()').extract_first().replace("$", "")
        except:
            price = ""
        attrs_l = response.xpath('//*[@class = "attrgroup"]/span').extract()
        attrs = self.processATTRS(attrs_l)

        title = response.xpath('//*[@id = "titletextonly"]/text()').extract_first()
        mapaddress = response.css("div.mapaddress::text").extract_first()
        map_url = response.css("p.mapaddress small a::attr(href)").extract_first()
        post_time=response.css('p.postinginfo time::attr(datetime)').extract_first()

        item = {}
        item['post_url'] = response._url
        item['price'] = price
        item['address'] = mapaddress
        item['map_url'] = map_url
        try:
            item['odometer'] = attrs['odometer']
        except:
            item['odometer'] = 0
        try:
            item['VIN'] = str(attrs['VIN'])
        except:
            item['VIN'] = ""
        try:
            item['title status'] = str(attrs['title status'])
        except:
            item['title status'] = ""
        try:
            item['transmission'] = str(attrs['transmission'])
        except:
            item['transmission'] = ""

        item['title'] = str(title)
        item['post_time']=str(post_time)
        try:
            item['auto_descr_short'] = attrs['auto_descr_short']
        except:
            item['auto_descr_short'] = ""
        yield item

    def processATTRS(self, attrs):
        ret = {}
        for a in attrs:
            a = a.replace("<span>", "").replace("</span>", "")
            parts = a.split("<b>", 1)
            print(parts)
            if len(parts) > 1 or parts[0] == '':
                prop = parts[0].rstrip(": ")
                if prop == '':
                    prop = "auto_descr_short"
                val = parts[1].replace("</b>", "")
                if val != '':
                    ret[prop] = val
        return ret
