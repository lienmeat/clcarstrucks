
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
        #build the initial request
        yield Request(self.proto + self.city + '.' + self.domain + '/search/cta?' + urlencode(self.getSearchArgs()))


    def getSearchArgs(self):
        #todo: Doesn't support multiples of the same param.  Ok for now...
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

        #grab the next page url from the paginator
        nextp =  response.css('a.next::attr(href)').extract_first()
        if nextp:
            yield Request(self.proto + self.city + '.' + self.domain + nextp, callback=self.parse)

        #get all the links for the adds
        links = response.css('li.result-row a.hdrlnk::attr(href)').extract()
        for link in links:
            #links are relative
            link = self.proto + self.city + '.' + self.domain + link
            yield Request(link, callback=self.parse_detail_page)

    def parse_detail_page(self, response):
        item = {}

        item['title'] = response.xpath('//*[@id = "titletextonly"]/text()').extract_first()
        #if we have a title, we can continue, otherwise get out
        if not item['title'] or len(item['title']) < 1:
            return

        try:
            item['price'] = response.xpath('//*[@class = "price"]/text()').extract_first().replace("$", "")
        except AttributeError:
            item['price'] = ""

        item['post_url'] = response._url
        item['address'] = response.css("div.mapaddress::text").extract_first()
        item['map_url'] = response.css("p.mapaddress small a::attr(href)").extract_first()
        item['post_time'] = response.css('p.postinginfo time::attr(datetime)').extract_first()

        attrs_l = response.xpath('//*[@class = "attrgroup"]/span').extract()
        item = self.processATTRS(attrs_l, item)

        if item['title']:
            yield item

    def processATTRS(self, attrs, item):
        '''ATTRS are the attrgoup items at the right hand side that describe a car'''
        #we only care about these attributes
        allowed = ['odometer', 'VIN', 'title status', 'transmission', 'auto_descr_short']
        attr_found = {}
        for a in attrs:
            a = a.replace("<span>", "").replace("</span>", "")
            parts = a.split("<b>", 1)
            if len(parts) > 1 or parts[0] == '':
                prop = parts[0].rstrip(": ")
                if prop == '':
                    prop = "auto_descr_short"
                val = parts[1].replace("</b>", "")
                attr_found[prop] = val
        for i in allowed:
            try:
                item[i] = attr_found[i]
            except KeyError:
                item[i] = ""
        return item
