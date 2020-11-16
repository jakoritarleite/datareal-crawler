from __future__ import annotations

from io import BytesIO
from parsel import Selector
from urllib.parse import urljoin

from lib.url import validator

class Crawl:
    """Docstring for the Crawl class.
    
    Retrieves the crawled content from the given HTML using
    the XPath passed as param.

    Typical usage example:
        crawl = Class(
            mapping={'parser...':...},
            encoding='ASCII',
            use_scrape=True,
            use_head=False
        )
        result = crawl.get_content()
    """
    def __init__(
        self,
        mapping: dict[str, str],
        encoding: str = 'UTF-8',
        use_scrape: bool = False,
        use_head: bool = False
    ) -> None:
        """Docstring for the __init__ method.
        Args:
            param1 (str) encoding: (default 'UTF-8')
                The encoding for converting Bynary into String
            param2 (dict) mapping:
                The XPaths in a object
            param3 (bool) use_scrape: (default False)
                If the target crawling is the Scrape State Machine or not
            param4 (bool) use_head: (default False)
                If you want to crawl information from <header> (olx specific)
        """
        assert isinstance(encoding, str), \
            'The encoding param must be String'

        assert isinstance(mapping, dict), \
            'The XPath mapping param must be dict'

        self.encoding = encoding
        self.mapping = mapping

        if use_scrape:
            assert isinstance(use_scrape, bool), \
                'The use_scrape param must be bool'

            self._set_scrape()

        else:
            self._set_crawl()

        if use_head:
            assert isinstance(use_head, bool), \
                'The use_head param must be bool'

            self._set_head()

    def _set_scrape(self) -> ClassVar[scrape]:
        """Docstring for the _set_scrape property.

        Returns:
            Function for Scrape State Machine
        """
        self.crawler = _Scrape(mapping=self.mapping)

    def _set_crawl(self) -> ClassVar[crawl]:
        """Docstring for the _set_crawl property.

        Returns:
            Funtion for Crawl State Machine
        """
        
        self.crawler = _Crawl(mapping=self.mapping)

    def _set_head(self) -> ClassVar[head]:
        """Docstring for the _set_crawl property.
        
        Returns:
            Function for the Scrape State Machine but using <head> instead <body>
        """
        self.crawler = _Head(mapping=self.mapping)

    def get_content(self, content: bytes, url: str) -> Dict[str, str]:
        """Docstring for the get_content function.
        Args:
            param1 (bytes) content:
                The HTML itself
        
        Returns:
            A dict corresponding to the DynamoDB Pattern
            with all crawled content.
            example: 
        
            {
                'title': ...,
                'price': ...,
                ...
            }
        """
        result: Dict[str, str] = self.crawler._get(content.decode(self.encoding), url)

        return result

class _Scrape:
    """Docstring for the _Scrape class.
    
    Get the target content of the given HTML
    using XPath config. This Class is made specific
    for the Scrape State Machine.
    """
    def __init__(self, mapping: Dict[XPath]) -> None:
        """Docstring for the __init__ method.
        Args:
            param1 (dict) mapping:
                The XPaths in a object
        """
        self.mapping = mapping
    
    def _get(self, content: str, url: str) -> dict:
        """Docstring for the _scrape function.

        It crawl the information on the given HTML ``content``
        using the given dict with XPaths ``mapping``. The content
        it crawls is title, price, bedrooms, and informations like that.

        Note:
            It's different from the _crawl function since the crawled content
            and the dict structure are not the same
        
        Args:
            param1 (str) content: The HTML content
        
        Returns:
            A dict with the crawled content
        """
        parser: ClassVar[Parser] = Selector(text = content)
        item: Dict[str, str] = dict()
        items: List[str] = ['title', 'price', 'rooms', 'suites', 'garages', 'location', 'category', 'url', 'body', 'features', 'images']

        body: str = parser.xpath(self.mapping['parser_body']).extract_first()
        title: str = parser.xpath(self.mapping['parser_title']).extract_first()
        price: str = parser.xpath(self.mapping['parser_price']).extract_first()
        rooms: str = parser.xpath(self.mapping['parser_rooms']).extract_first()
        suites: str = parser.xpath(self.mapping['parser_suites']).extract_first()
        garages: str = parser.xpath(self.mapping['parser_garages']).extract_first()
        location: str = parser.xpath(self.mapping['parser_location']).extract_first()
        category: str = parser.xpath(self.mapping['parser_category']).extract_first()
        features: List[str] = parser.xpath(self.mapping['parser_features']).extract()
        images_src: List[str] = parser.xpath(self.mapping['parser_images_src']).extract()
        images_alt: List[str] = parser.xpath(self.mapping['parser_images_alt']).extract()
        images: List[Dict[str, str]] = [
            {
                'src': images_src[i],
                'alt': images_alt[i]
            }
            for i in range(len(images_src))
        ]
        url: str = url

        print(f'Price: {price}')

        for variable in items:
            item[variable] = eval(variable)

        return item

class _Crawl:
    """Docstring for the Crawl class.
    
    Get the target content of the given HTML
    using XPath config. This Class is made specific
    for the Crawl State Machine.
    """
    def __init__(self, mapping: Dict[XPath]) -> None:
        """Docstring for the __init__ method.
        Args:
            param1 (dict) mapping:
                The XPaths in a object
        """
        self.mapping = mapping

    def _get(self, content: str, url: str) -> list:
        """Docstring for the _crawl function.

        It crawl the information on the given HTML ``content``
        using the given dict with XPaths ``mapping``. The content
        it crawls is title, urls and next_page.

        Note:
            It's different from the _scrape function since the crawled content
            and the dict structure are not the same

        Args:
            param1 (str) content:
                The HTML itself

        Returns:
            A list[dict, str] with the items url and next page urls
        """
        parser: ClassVar[Parser] = Selector(text = content)
        result: List[Items, NextPage] = list()
        items: List[str] = list()
        _items: List[str] = ['items', 'next_page']

        for item in parser.xpath(self.mapping['parser_items']):
            item_url = item.xpath(self.mapping['parser_items_url']).extract_first()
            
            if item_url:
                if not validator(item_url):
                    item_url = urljoin(self.origin, item_url)

                items.append(item_url)

        next_page: str = parser.xpath(self.mapping['parser_next_page']).extract_first()

        if next_page:
            if not validator(next_page):
                next_page = urljoin(url, next_page)

        return items, next_page

class _Head:
    """Docstring for the _Scrape class.
    
    Get the target content of the given HTML
    using XPath config to get the JSON. This Class is made specific
    for the Scrape State Machine and for OLX urls.
    """
    def __init__(self, mapping: Dict[XPath]) -> None:
        """Doctsting for the __init__ method.

        Args:
            param1 (dict) mapping:
                The XPaths in a object
        """
        self.mapping = mapping

    def _get(self, content: str, url: str) -> dict:
        """Docstring for the _head function.
        
        It gets the information from the JSON using ``eval`` python
        function.

        Note:
            This is exclusive to OLX, since it's the unique website that keep the JSON on the <head>

        Args:
            param1 (str) content: The HTML <head> content

        Returns:
            A dict with the crawled content

        """
        parser: ClassVar[Parser] = Selector(text = content)
        item: Dict[str, str] = dict()
        items: List[str] = ['title', 'price', 'rooms', 'bathrooms', 'garages', 'location', 'category', 'url', 'body', 'features', 'images']

        head_json = eval(parser.xpath(self.mapping['parser_json']).extract_first().replace('null', 'None').replace('true', 'True').replace('false', 'False'))['ad']

        body: str = head_json['body']
        title: str = parser.xpath(self.mapping['parser_title']).extract_first()
        location: Dict[str, str] = head_json['location']

        price: str = None
        rooms: str = None
        garages: str = None
        bathrooms: str = None
        category: str = None
        features: list = list()

        for _property in head_json['properties']:
            if _property['name'] == 'price':
                price = _property['value']  

            elif _property['name'] == 'rooms':
                rooms = _property['value']

            elif _property['name'] == 'garage_spaces':
                garages = _property['value']

            elif _property['name'] == 'bathrooms':
                bathrooms = _property['value']

            elif _property['name'] == 'category':
                category = _property['value']

            elif 'features' in _property['name']:
                for feature in _property['values']:
                    features.append(feature['label'])

        images: list = list()

        for image in head_json['images']:
           images.append({
               'src': image['original'],
               'alt': image['originalAlt']
           })

        for variable in items:
            item[variable] = eval(variable)

        return item
