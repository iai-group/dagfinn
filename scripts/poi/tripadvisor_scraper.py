"""Class to scrape attractions and restaurants from Tripadvisor.com"""

from typing import Dict

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from webdriver_manager.chrome import ChromeDriverManager


# TODO create util module with interface for scrapers
class TripAdvisorScraper:
    def __init__(self) -> None:
        """Create web driver to execute searches"""
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        self.chrome_options.add_experimental_option(
            "useAutomationExtension", False
        )
        self.chrome_options.add_argument("--disable-blink-features")
        self.chrome_options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )
        self.service = ChromeService(
            executable_path=ChromeDriverManager().install()
        )
        self.browser = webdriver.Chrome(
            service=self.service, options=self.chrome_options
        )

    def get_city_attractions(self, attractions_link: str) -> pd.DataFrame:
        """Scrapes the attractions on the first result page.

        Args:
            attractions_link: URL to scrape.

        Returns:
            Dataframe with information for attrations on the first result page.
        """
        df = pd.DataFrame(
            columns=[
                "name",
                "category",
                "rating",
                "price",
                "address",
                "busStop",
                "distanceFromBusStop",
                "website",
                "googleMapsID",
            ]
        )
        self.browser.get(attractions_link)

        soup = BeautifulSoup(self.browser.page_source, "lxml")
        attraction_divs = soup.find_all(class_="alPVI eNNhq PgLKC tnGGX")

        for div in attraction_divs:
            a = div.select("a:nth-of-type(1)")[0]
            info = self.parse_attraction_page(
                "https://www.tripadvisor.com" + a.get("href")
            )
            df = df.append(info, ignore_index=True)
        return df

    def parse_attraction_page(self, attraction_link: str) -> Dict:
        """Scrapes attraction's details page.

        Args:
            attraction_link: URL to scrape.

        Returns:
            Dictionary with information related to a specific attraction.
        """
        info = {
            "name": "",
            "category": "",
            "rating": 0,
            "price": "",
            "address": "",
            "busStop": "",
            "distanceFromBusStop": 0,
            "website": "",
            "googleMapsID": "",
        }
        self.browser.get(attraction_link)
        try:
            wait(self.browser, 60).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        (
                            "section.vwOfI.nlaXM > div > div > span > div > "
                            "div:nth-child(2) > div.WoBiw > a:nth-child(1)"
                        ),
                    )
                )
            )
        except Exception as e:
            print(e)
        soup = BeautifulSoup(self.browser.page_source, "lxml")

        name = soup.find("h1", class_="biGQs _P fiohW eIegw")
        if name:
            info["name"] = name.text
        else:
            info["name"] = soup.select_one("#HEADING").text

        category = soup.select_one(
            "div.bkycL.z > div:nth-child(2) > div > div > span > "
            "section:nth-child(2) > div > div > span > div > div:nth-child(1) "
            "> div:nth-child(3) > div > div > div.fIrGe._T.bgMZj"
        )
        if category:
            info["category"] = category.text
        else:
            categories = soup.select(
                "div.DEuCL.hasAvatar > div.dSQMQ.d.S4 > span:nth-child(1) > a"
            )
            info["category"] = " • ".join(
                [category.text for category in categories]
            )

        rating = soup.select_one(
            "div.bdeBj.e > span > div > div.f.u.j > "
            "div.biGQs._P.fiohW.hzzSG.uuBRH"
        )
        if rating:
            info["rating"] = float(rating.get_text(strip=True))

        address = soup.select_one(
            "button.UikNM._G.B-._S._T.c.G_.P0.wSSLS.wnNQG.raEkE > "
            "span.biGQs._P.XWJSj.Wb"
        )
        if address:
            info["address"] = address.text

        website = soup.select_one(
            "section.vwOfI.nlaXM > div > div > span > div > div:nth-child(2) > "
            "div.WoBiw > a:nth-child(1)"
        )
        if website:
            info["website"] = website.get("href")

        return info

    def get_city_restaurants(self, restaurants_link: str) -> pd.DataFrame:
        """Scrapes the restaurants on the first result page.

        Args:
            restaurants_link: URL to scrape.

        Returns:
            Dataframe with information for restaurants on the first result page.
        """
        df = pd.DataFrame(
            columns=[
                "name",
                "category",
                "rating",
                "price",
                "address",
                "busStop",
                "distanceFromBusStop",
                "website",
                "googleMapsID",
            ]
        )
        self.browser.get(restaurants_link)
        soup = BeautifulSoup(self.browser.page_source, "lxml")

        restaurant_urls = soup.find_all("a", class_="Lwqic Cj b")
        for url in restaurant_urls:
            info = self.parse_restaurant_page(
                "https://www.tripadvisor.com" + url.get("href")
            )
            df = df.append(info, ignore_index=True)
        return df

    def parse_restaurant_page(self, restaurant_link: str) -> Dict:
        """Scrapes restaurant's details page.

        Args:
            restaurant_link: URL to scrape.

        Returns:
            Dictionary with information related to a specific restaurant.
        """
        info = {
            "name": "",
            "category": "",
            "rating": 0,
            "price": "",
            "address": "",
            "busStop": "",
            "distanceFromBusStop": 0,
            "website": "",
            "googleMapsID": "",
        }
        self.browser.get(restaurant_link)

        soup = BeautifulSoup(self.browser.page_source, "lxml")

        name = soup.select_one("div.acKDw.w.O > h1")
        if name:
            info["name"] = name.text

        categories = soup.select("span.DsyBj.DxyfE > a")
        if categories:
            cats = [category.text for category in categories[1:]]
            if not set(cats).intersection({"Bar", "Cafe", "Pub"}):
                cats = cats + ["Restaurant"]
            info["category"] = " • ".join(cats)

        rating = soup.select_one(
            "div.hILIJ.MD > div > div:nth-child(1) > div > div:nth-child(1) > "
            "div.QEQvp > span.ZDEqb"
        )
        if rating:
            info["rating"] = float(rating.get_text(strip=True))

        price = soup.select_one(
            "div.vQlTa.H3 > span.DsyBj.DxyfE > a.dlMOJ:nth-child(1)"
        )
        if price:
            info["price"] = max(
                len(i) for i in price.get_text(strip=True).split(" - ")
            )

        address = soup.select_one("span.DsyBj.cNFrA > span > a.AYHFM")
        if address:
            info["address"] = address.text

        website = soup.select_one(
            "span.DsyBj.cNFrA > span > a.YnKZo.Ci.Wc._S.C.AYHFM"
        )

        if website:
            info["website"] = website.get("href")

        return info
