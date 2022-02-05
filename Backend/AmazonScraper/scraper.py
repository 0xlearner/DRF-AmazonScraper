import time
import os
import random
import json
from datetime import datetime
from requests_html import AsyncHTMLSession
import asyncio
from scraper_config import (
    DIRECTORY,
    CATEGORIES,
    FILTERS,
    CURRENCY,
    BASE_URL,
)


class Reporter:
    def __init__(self, categories, filters, base_url, currency, directory):
        self.categories = categories
        self.base_url = base_url
        self.currency = currency
        self.filters = filters
        self.directory = f"{os.path.dirname(os.path.abspath(__file__))}/{directory}"

    def run(self):
        # self.generate_report("PS5")  # <---------- single category
        # multiple categories here
        self.run_bot_on_all_categories()

    def run_bot_on_all_categories(self):
        for category in self.categories:
            self.generate_report(category)
            pause = random.randint(50, 70)
            print(f"Sleeping for {pause} seconds....")
            time.sleep(pause)

    def generate_report(self, category):
        data = self.get_data_from_category(category)
        full_directory = f"{self.directory}/{category}.json"
        report = {
            "date": self.get_now(),
            "category": category,
            "product_count": len(data),
            "currency": self.currency,
            "base_link": self.base_url,
            "products": data,
        }

        print(f"Creating report for {category}")
        if not os.path.exists(full_directory):
            os.makedirs(os.path.dirname(full_directory), exist_ok=True)
        with open(full_directory, "w") as f:
            json.dump(report, f)
        print(f"Created report for {category}")

    @staticmethod
    def get_now():
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")

    def remove_empty_elements(self, d):
        """recursively remove empty lists, empty dicts, or None elements from a dictionary"""

        def empty(x):
            return x is None or x == {} or x == []

        if not isinstance(d, (dict, list)):
            return d
        elif isinstance(d, list):
            return [
                v for v in (self.remove_empty_elements(v) for v in d) if not empty(v)
            ]
        else:
            return {
                k: v
                for k, v in ((k, self.remove_empty_elements(v)) for k, v in d.items())
                if not empty(v)
            }

    def get_data_from_category(self, category):
        loop = asyncio.get_event_loop()
        scraper = AmazonScraper(category, self.filters, self.base_url, self.currency)
        scraped_data = loop.run_until_complete(scraper.run())
        data = self.remove_empty_elements(scraped_data)
        return data


class AmazonScraper:
    def __init__(self, search_term, filters, base_url, currency):
        self.asession = AsyncHTMLSession()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
            "Accept": "text/html,*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Referer": f"https://www.amazon.com/s?k={search_term}&ref=nb_sb_noss",
        }
        self.base_url = base_url
        self.search_term = search_term
        self.currency = currency
        print(filters)
        self.price_filter = f"&rh=p_36%3A{filters['min']}00-{filters['max']}00"

    async def run(self):
        print("Strating script...")
        print(f"Looking for {self.search_term} products...")
        urls = await self.get_product_links()
        if not urls:
            print("Stopped script.")
            return
        print(f"Got {len(urls)} products.")
        print("Parsing the product links...")
        tasks = [asyncio.create_task(self.parse_urls(url)) for url in urls]
        print(f"Got information about {len(tasks)} products.")
        result = await asyncio.gather(*tasks)
        return result

    async def get_product_links(self):  #
        # https://www.amazon.com/s?k=ps5&rh=p_36%3A27500-65000
        url = await self.asession.get(
            self.base_url + self.search_term + self.price_filter,
            headers=self.headers,
        )
        print(url)
        print(url.status_code)
        asin = "div[data-asin]"
        price_tag = "span.a-offscreen"
        product_asins = []

        tag = url.html.find("div[data-component-type=s-search-result]")
        for check in tag:
            if check.find(price_tag) and check.find(asin):
                for a in check.find(asin):
                    product_asins.append(a.attrs["data-asin"])
            else:
                print("Bad price tag")

        time_wasting_asin = ["B015HS4O1K", "B0756GB78C", "B088ZWQB48"]
        for asin in time_wasting_asin:
            if asin in product_asins:
                product_asins.remove(asin)
        product_link = ["https://www.amazon.com/dp/" + link for link in product_asins]
        print(len(product_link))
        return product_link

    async def parse_urls(self, url):
        print("----------------------------------------------------------------")
        print(f"Getting Product:{url} --- Data")

        product_asin = url.split("/")[4]
        print("ASIN:", product_asin)
        product_title = await self.get_title(url)
        print("TITLE:", product_title)
        product_price = await self.get_price(url)
        print("PRICE:", product_price)
        product_seller = await self.get_seller(url)
        print("SELLER:", product_seller)
        product_review_count = await self.get_review_count(url)
        print("REVIEW_COUNT:", product_review_count)
        product_rating = await self.get_rating(url)
        print("RATING:", product_rating)
        product_photo_url = await self.get_photo_url(url)
        print("PHOTO_URL:", product_photo_url)
        print("----------------------------------------------------------------")
        if product_title and product_price and product_rating and product_photo_url:
            product_info = {
                "asin": product_asin,
                "url": url,
                "title": product_title,
                "price": product_price,
                "rating": product_rating,
                "photo": product_photo_url,
                "seller": product_seller,
                "review_count": product_review_count,
            }

            return product_info
        return None

    async def get_title(self, url):
        _session = await self.asession.get(url, headers=self.headers)
        title = None

        try:
            if _session.html.find("span#productTitle", first=True):
                title = _session.html.find("span#productTitle", first=True).text
                return title
            elif _session.html.find("h1.a-size-large", first=True):
                title = _session.html.find("h1.a-size-", first=True).text
                return title
            else:
                title = ""

        except Exception as e:
            print(e)
            print(f"Can't get a title of a product - {url}")
            return None

    async def get_seller(self, url):
        _session = await self.asession.get(url, headers=self.headers)
        try:
            seller = _session.html.find("a#bylineInfo", first=True).text
            if "Visit the" in seller:
                return " ".join(seller.split(" ")[2:])
            elif "Brand" or "Brand: " or "Brand:" in seller:
                return "".join(seller.split(" ")[0:])

        except Exception as e:
            print(e)
            try:
                return _session.html.find("a.qa-byline-url", first=True).text
            except Exception as e:
                print(f"Can't get a seller of a product - {url}")
                return None

    async def get_price(self, url):
        price = None
        _session = await self.asession.get(url, headers=self.headers)
        try:
            price_1 = _session.html.find("span.apexPriceToPay", first=True)
            if price_1 is not None:
                price = float(price_1.text.split("$")[1])
            else:
                price = float(
                    _session.html.find(
                        "span#priceblock_ourprice", first=True
                    ).text.split("$")[1]
                )
                print(price)
        except Exception as e:
            print(e)
            try:
                availability = _session.html.find("span.a-color-price", first=True).text
                out_of_stock = _session.html.find("span.a-color-price", first=True).text
                availability_message = _session.html.find(
                    "span.qa-availability-message", first=True
                ).text
                if "In Stock." or None in availability:
                    price = float(
                        _session.html.find(
                            "span.apexPriceToPay", first=True
                        ).text.split("$")[1]
                    )
                elif "Temporarily out of stock." in out_of_stock:
                    price = 0
                elif "Currently unavailable." in availability:
                    price = 0
                elif "Currently unavailable." in availability_message:
                    price = 0
                    print(price)
                elif "Currently unavailable." in out_of_stock:
                    price = 0
                else:
                    price = None
            except Exception as e:
                print(price)
                if not price:
                    try:
                        price = float(
                            _session.html.find(
                                "span.a-color-price:nth-child(2)", first=True
                            ).text.split("$")[1]
                        )
                    except Exception as e:
                        availability = None
                        if _session.html.find(
                            "div#availability", first=True
                        ).text.startswith("P"):
                            availability = "N/A"
                            print(f"Product {availability}")
                        elif (
                            "In Stock."
                            in _session.html.find("div#availability", first=True).text
                        ):
                            price = 0
                        else:
                            availability = _session.html.find(
                                "div#availability", first=True
                            ).text.split("\n")[0]
                            print(f"Product {availability}")

                        return None
        return float(price)

    async def get_review_count(self, url):
        _session = await self.asession.get(url, headers=self.headers)

        try:
            return int(
                _session.html.find("span#acrCustomerReviewText", first=True)
                .text.split(" ")[0]
                .replace(",", "")
                .strip()
            )
        except Exception as e:
            print(e)
            print(f"Can't get a review count of a product - {url}")
            return None

    async def get_rating(self, url):
        _session = await self.asession.get(url, headers=self.headers)

        try:
            return float(
                _session.html.find("span.a-icon-alt", first=True).text.split(" ")[0]
            )
        except Exception as e:
            print(e)
            print(f"Can't get a review of a product - {url}")
            return None

    async def get_photo_url(self, url):
        _session = await self.asession.get(url, headers=self.headers)

        try:
            return _session.html.find("img#landingImage", first=True).attrs["src"]
        except Exception as e:
            print(e)
            print(f"Can't get a photo url of a product - {url}")
            return None


def main():
    report = Reporter(CATEGORIES, FILTERS, BASE_URL, CURRENCY, DIRECTORY)
    report.run()


if __name__ == "__main__":
    main()
