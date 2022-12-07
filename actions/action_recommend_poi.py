"""Custom actions related to point of interest recommendations."""
from random import randrange
from typing import Any, Dict, List, Text
from urllib.parse import quote_plus

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from actions.db_connector import DBConnector
from actions.maps import DirectionMap

DB_NAME = "poi"
CONFERENCE_ADDRESS = "Kristine Bonnevies vei 22, 4021 Stavanger, Norway"
MAPS = DirectionMap("Stavanger, Rogaland, Norway")


class POIResults:
    DISLIKE_TO_LIKE_REPLACEMENT_MAP = {
        "gluten": ["gluten-free food"],
        "meat": ["vegetarian food"],
    }
    BUS_STOPS_WITHIN_WALKING_DISTANCE = [
        "Jernbaneveien",
        "Jorenholmen",
        "Kannik",
    ]
    LAYOVER_TO_ORIGIN_MAP = {
        "Stavanger bus terminal 3": "Jernbaneveien",
    }
    SELECT_POI_BY_PID = """
            SELECT *
            FROM POI
            WHERE pid IN ({pids})
            ORDER BY {order}
    """
    SELECT_POI_BY_CATEGORY = """
            SELECT *
            FROM POI
            WHERE LOWER(category) LIKE '%{category}%'
            ORDER BY {order}
    """
    SELECT_PID_BY_TAG = """
            SELECT POI.pid
            FROM POI
            INNER JOIN POITag
            ON POI.pid = POITag.pid
            WHERE POITag.tag LIKE '%{}%'
    """
    SELECT_PID_BY_CATEGORY_AND_NOT_PID = """
            SELECT pid
            FROM POI
            WHERE LOWER(category) LIKE '%{category}%'
            AND pid NOT IN ({pids})
    """
    SELECT_TAG_BY_TAG = """
            SELECT tag
            FROM POITag
            WHERE tag LIKE '%{}%'
    """
    SELECT_BUS_ROUTE_BY_DESTINATION = """
            SELECT *
            FROM busRoute
            WHERE destination = '{}'
            ORDER BY duration ASC
    """

    def __init__(
        self,
        category: Text = "",
        likes: List = [],
        dislikes: List = [],
    ) -> None:
        """Object for browsing POI-related things in database.

        Args:
            category: POI category. Defaults to "restaurant".
            likes: Liked POI tags. Defaults to [].
            dislikes: Disliked POI tags. Defaults to [].
        """
        self.database = DBConnector(DB_NAME)
        self.category = category
        self.likes = likes
        self.dislikes = dislikes
        self.order_by = "rating DESC, price ASC"
        self.initialization()

    def initialization(self) -> None:
        """Further initialization of fields."""
        if not self.category:
            self.category = "restaurant"
        if not self.likes:
            self.likes = []
        if not self.dislikes:
            self.dislikes = []
        self.swap_dislikes_with_likes()
        self.remove_duplicate_tags()

    def swap_dislikes_with_likes(self) -> None:
        """Swaps certain disliked POI tags with more appropriate liked ones."""
        if not self.dislikes:
            return
        for dislike in self.dislikes:
            for (
                key,
                replacement,
            ) in self.DISLIKE_TO_LIKE_REPLACEMENT_MAP.items():
                if key.lower() in dislike.lower():
                    self.dislikes.remove(dislike)
                    self.likes.extend(replacement)

    def remove_duplicate_tags(self) -> None:
        """Removes duplicates from liked and disliked POI tags. If the same tag
        is found in both dislikes and likes it will be removed from dislikes.
        """
        self.likes = list(dict.fromkeys(self.likes))
        self.dislikes = list(dict.fromkeys(self.dislikes))
        for like in self.likes:
            for dislike in self.dislikes:
                if like in dislike or dislike in like:
                    self.dislikes.remove(dislike)

    def get_poi_matches(self) -> List:
        """Returns a list of POIs that matches likes, dislikes or category.

        Returns:
            List: List of POIs.
        """
        if self.likes:
            if self.dislikes:
                return self.fetch_pois_by_likes_and_dislikes()
            return self.fetch_pois_by_likes()
        if self.dislikes:
            return self.fetch_pois_by_dislikes()
        return self.fetch_pois_by_category()

    def get_cheap_poi_matches(self) -> List:
        """Returns a list of POIs sorted by price that matches
        likes, dislikes or category.

        Returns:
            List: List of POIs.
        """
        self.order_by = "price ASC, rating DESC"
        return self.get_poi_matches()

    def get_full_bus_route(self, destination: Text) -> Dict:
        """Gives dictionary of bus routes to reach some final bus stop.

        Args:
            destination: Name of bus top to be reached

        Returns:
            Dict: Dictionary of bus route dictionary objects.
        """
        routes = {}
        fetched_routes = self.fetch_bus_routes(destination)
        if fetched_routes:
            to_destination = fetched_routes[0]
            routes["to_destination"] = to_destination
            origin = to_destination.get("origin")
            if origin not in self.BUS_STOPS_WITHIN_WALKING_DISTANCE:
                prior_destination = self.LAYOVER_TO_ORIGIN_MAP.get(origin)
                routes["to_layover"] = self.fetch_bus_routes(prior_destination)[
                    0
                ]
        return routes

    def fetch_bus_routes(self, destination: Text) -> List:
        """Fetches list of bus routes matching destination.

        Args:
            destination: Destination bus stop.

        Returns:
            List: List of route dictionary objects to provided bus stops.
        """
        sql = self.SELECT_BUS_ROUTE_BY_DESTINATION.format(destination) + ";"
        cur = self.database.cur
        cur.row_factory = None
        cur.execute(sql)
        return self.get_organized_bus_route_list(cur.fetchall())

    def fetch_pois_by_category(self) -> List:
        """Returns list of matching POIs based on category.

        Returns:
            List: List of POI dictionary objects.
        """
        sql = self.SELECT_POI_BY_CATEGORY.format(
            category=self.category.lower(), order=self.order_by
        )
        cur = self.database.cur
        cur.row_factory = None
        cur.execute(sql)
        return self.get_organized_poi_list(cur)

    def fetch_pois_by_likes(self) -> List:
        """Gives list of POI objects based on likes.

        Returns:
            List: List of POI dictionary objects.
        """
        pids = self.fetch_pids_by_likes()
        return self.fetch_pois_by_pids(pids)

    def fetch_pids_by_likes(self) -> List:
        """Creates list of POIs containing all liked tags.

        Returns:
            List: List of POI IDs.
        """
        final_pid_matches = []
        for i, like in enumerate(self.likes):
            pid_matches = self.fetch_by_sql(
                self.SELECT_PID_BY_TAG.format(like) + ";"
            )
            if i == 0:
                final_pid_matches = pid_matches
            else:
                final_pid_matches = [
                    item for item in final_pid_matches if item in pid_matches
                ]
        return final_pid_matches

    def fetch_pids_by_dislikes(self) -> List:
        """Creates list of POIs containing any of the disliked tags.

        Returns:
            List: List of POI IDs.
        """
        final_pid_matches = []
        for dislike in self.dislikes:
            pid_matches = self.fetch_by_sql(
                self.SELECT_PID_BY_TAG.format(dislike) + ";"
            )
            final_pid_matches.extend(pid_matches)
        return final_pid_matches

    def fetch_pois_by_dislikes(self) -> List:
        """Gives list of POI objects without unwanted tags.

        Returns:
            List: List of POI dictionary objects.
        """
        unwanted_pids = self.fetch_pids_by_dislikes()
        sql = self.SELECT_PID_BY_CATEGORY_AND_NOT_PID.format(
            category=self.category.lower(),
            pids=",".join(["?"] * len(unwanted_pids)),
        )
        wanted_pids = self.fetch_by_sql(sql + ";", unwanted_pids)
        return self.fetch_pois_by_pids(wanted_pids)

    def fetch_pois_by_likes_and_dislikes(self) -> List:
        """Generates list of POI objects satisfying both likes and dislikes.

        Returns:
            List: List of POI dictionary objects.
        """
        wanted_pids = self.fetch_pids_by_likes()
        unwanted_pids = self.fetch_pids_by_dislikes()
        pids = [pid for pid in wanted_pids if pid not in unwanted_pids]
        return self.fetch_pois_by_pids(pids)

    def fetch_proper_tags(self, tags: List) -> List:
        """Fetches list proper tag names from NLU generated ones.

        Args:
            tags: Tags extracted by NLU.

        Returns:
            List: Proper tags from database.
        """
        proper_tags = []
        for tag in tags:
            matching_tags = self.fetch_by_sql(
                self.SELECT_TAG_BY_TAG.format(tag) + ";"
            )
            if not matching_tags:
                proper_tags.append(tag)
                continue
            if tag in matching_tags:
                proper_tags.append(tag)
                continue
            proper_tags.append(matching_tags[0])
        return proper_tags

    def fetch_by_sql(self, sql: Text, list: List = []) -> List:
        """Fetches list from database based on SQL statement.

        Args:
            sql: SQL to be executed by SQLite.
            list: List of arguments for SQL.

        Returns:
            List: List of items.
        """
        cur = self.database.cur
        cur.row_factory = lambda cursor, row: row[0]
        if list:
            cur.execute(sql, list)
        else:
            cur.execute(sql)
        return cur.fetchall()

    def fetch_pois_by_pids(self, pids: List) -> List:
        """Given list of POI IDs, returns list of POI objects.

        Args:
            pids: List of POI IDs.

        Returns:
            List: List of POI dictonary objects.
        """
        sql = (
            self.SELECT_POI_BY_PID.format(
                pids=",".join(["?"] * len(pids)), order=self.order_by
            )
            + ";"
        )
        cur = self.database.cur
        cur.row_factory = None
        cur.execute(sql, pids)
        return self.get_organized_poi_list(cur.fetchall())

    def get_organized_poi_list(self, cur: List) -> List:
        """Organizes SQL data into a list of POI dictionaries.

        Args:
            cur: Result from SQL query.

        Returns:
            List: List of POI dictionary objects.
        """
        results = []
        for (
            id,
            name,
            category,
            rating,
            price,
            address,
            bus_stop,
            distance,
            website,
            google_maps_id,
        ) in cur:
            results.append(
                {
                    "id": id,
                    "name": name,
                    "category": category,
                    "rating": rating,
                    "price": price,
                    "address": address,
                    "bus_stop": bus_stop,
                    "distance": distance,
                    "website": website,
                    "google_maps_id": google_maps_id,
                    "likes": self.fetch_proper_tags(self.likes),
                    "dislikes": self.fetch_proper_tags(self.dislikes),
                    "nlu_likes": self.likes,
                    "nlu_dislikes": self.dislikes,
                }
            )
        return results

    def get_organized_bus_route_list(self, cur: List) -> List:
        """Organizes SQL data into a list of bus route dictionaries.

        Args:
            cur: Result from SQL query.

        Returns:
            List: List of bus route dictionary objects.
        """
        results = []
        for (
            id,
            origin,
            destination,
            number,
            duration,
        ) in cur:
            results.append(
                {
                    "id": id,
                    "origin": origin,
                    "destination": destination,
                    "number": number,
                    "duration": duration,
                }
            )
        return results


class POIFunctions:
    @classmethod
    def get_match(cls, tracker: Tracker, is_cheap: bool = False) -> Dict:
        """Retrieves POI match based on slots and other preferences.

        Args:
            tracker: Class that maintains the state of a conversation.
            is_cheap: Prioririzes cheap places if set to true.

        Returns:
            Dict: POI dictionary object.
        """
        category = tracker.get_slot("poi_category")
        likes = cls.set_likes(tracker)
        dislikes = cls.set_dislikes(tracker)
        return cls.fetch_match(category, likes, dislikes, is_cheap)

    @classmethod
    def get_matches_by_likes(cls, tracker: Tracker) -> List:
        """Fetches all POI objects that has provided liked POI tags.

        Args:
            tracker: Class that maintains the state of a conversation.

        Returns:
            List: POI dictionary objects.
        """
        likes = tracker.get_slot("liked_poi_tags")
        poi_browser = POIResults(likes=likes)
        return poi_browser.get_poi_matches()

    @classmethod
    def get_bus_route(cls, tracker: Tracker) -> List:
        recommended_poi = tracker.get_slot("recommended_poi")
        if recommended_poi:
            poi_browser = POIResults()
            return poi_browser.get_full_bus_route(
                recommended_poi.get("bus_stop")
            )
        return []

    @classmethod
    def fetch_match(
        cls,
        category: Text,
        likes: List,
        dislikes: List,
        is_cheap: bool = False,
    ) -> Dict:
        """Retrieves POI match from database using POI results class.

        Args:
            category: POI Category
            likes: Liked POI tags.
            dislikes: Disliked POI tags.
            is_cheap: Prioririzes cheap places if set to true.

        Returns:
            Dict: POI dictionary object.
        """
        poi_browser = POIResults(category, likes, dislikes)
        if is_cheap:
            results = poi_browser.get_cheap_poi_matches()
        else:
            results = poi_browser.get_poi_matches()
        if results:
            return results[cls.random_first_index(len(results))]
        return {}

    @classmethod
    def proper_tags_string(cls, tags: List) -> Text:
        poi_browser = POIResults()
        proper_tags = poi_browser.fetch_proper_tags(tags)
        return cls.stringify_list(proper_tags)

    @classmethod
    def set_likes(cls, tracker: Tracker) -> List:
        """Sets up the list of liked POI tags based on circumstances.

        Args:
            tracker: Class that maintains the state of a conversation.

        Returns:
            List: List of liked POI tags.
        """
        if cls.has_new_category(tracker) and not cls.has_new_tags(tracker):
            return []
        return tracker.get_slot("liked_poi_tags")

    @classmethod
    def set_dislikes(cls, tracker: Tracker) -> List:
        """Sets up the list of disliked POI tags based on circumstances.

        Args:
            tracker: Class that maintains the state of a conversation.

        Returns:
            List: List of disliked POI tags.
        """
        if cls.has_new_category(tracker) and not cls.has_new_tags(tracker):
            return []
        return tracker.get_slot("disliked_poi_tags")

    @classmethod
    def has_new_tags(cls, tracker: Tracker) -> bool:
        """Checks if liked and disliked POI tags have changed since last
        recommendation.

        Args:
            tracker: Class that maintains the state of a conversation.

        Returns:
            bool: True if there are new tags.
        """
        previously_recommended_poi = tracker.get_slot("recommended_poi")
        if not previously_recommended_poi:
            return True
        old_likes = previously_recommended_poi.get("nlu_likes")
        old_dislikes = previously_recommended_poi.get("nlu_dislikes")
        new_likes = tracker.get_slot("liked_poi_tags")
        new_dislikes = tracker.get_slot("disliked_poi_tags")
        return cls.is_different_list(
            old_likes, new_likes
        ) or cls.is_different_list(old_dislikes, new_dislikes)

    @classmethod
    def has_new_category(cls, tracker: Tracker) -> bool:
        """Checks if POI category has changed since last recommendation.

        Args:
            tracker: Class that maintains the state of a conversation.

        Returns:
            bool: True if category has changed.
        """
        previously_recommended_poi = tracker.get_slot("recommended_poi")
        if not previously_recommended_poi:
            return True
        old_category = previously_recommended_poi.get("category")
        new_category = tracker.get_slot("poi_category")
        return old_category != new_category

    @classmethod
    def has_walking_distance(cls, tracker: Tracker) -> bool:
        recommended_poi = tracker.get_slot("recommended_poi")
        if (
            recommended_poi.get("bus_stop")
            in POIResults.BUS_STOPS_WITHIN_WALKING_DISTANCE
        ):
            return True
        return False

    @classmethod
    def is_different_list(cls, list1: List, list2: List) -> bool:
        """Checks if two list contain different items.

        Args:
            list1: First list.
            list2: Second list.

        Returns:
            bool: True if they do not contain the same items.
        """
        if not list1:
            return bool(list2)
        if not list2:
            return bool(list1)
        list1.sort()
        list2.sort()
        return list1 != list2

    @classmethod
    def recommend_by_category(
        cls, dispatcher: CollectingDispatcher, match: Dict, response: Text
    ) -> None:
        """Recommendes provided POI match with provided response utterance.
        Uses fields: name, category.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            match: POI Dictionary object.
            response: The utterance being called by the dispatcher.
        """
        dispatcher.utter_message(
            response=response,
            category=match.get("category"),
            name=match.get("name"),
        )

    @classmethod
    def recommend_by_likes(
        cls, dispatcher: CollectingDispatcher, match: Dict, response: Text
    ) -> None:
        """Recommendes provided POI match with provided response utterance.
        Uses fields: name, category, likes.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            match: POI Dictionary object.
            response: The utterance being called by the dispatcher.
        """
        dispatcher.utter_message(
            response=response,
            name=match.get("name"),
            category=match.get("category"),
            likes=cls.stringify_list(match.get("likes")),
        )

    @classmethod
    def recommend_by_likes_and_dislikes(
        cls, dispatcher: CollectingDispatcher, match: Dict, response: Text
    ) -> None:
        """Recommendes provided POI match with provided response utterance.
        Uses fields: name, category, likes, dislikes.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            match: POI Dictionary object.
            response: The utterance being called by the dispatcher.
        """
        dispatcher.utter_message(
            response=response,
            name=match.get("name"),
            category=match.get("category"),
            likes=cls.stringify_list(match.get("likes")),
            dislikes=cls.stringify_list(match.get("dislikes"), "or"),
        )

    @classmethod
    def stringify_list(cls, list: List, seperator: Text = "and") -> Text:
        """Turns list into human readable form.

        Args:
            list: List to be converted.
            seperator: 'and', 'or', 'nor' etc.

        Returns:
            Text: String with list items.
        """
        if not list:
            return ""
        if len(list) == 1:
            return str(list[0])
        result = ", ".join(list)
        last_comma_idx = result.rfind(",")
        return (
            result[:last_comma_idx]
            + f" {seperator}"
            + result[last_comma_idx + 1 :]
        )

    @classmethod
    def random_first_index(cls, idx_range: int) -> int:
        """Gives random value between 0 and 3 or 0 and idx_range.

        Args:
            idx_range: Maximun index allowed.

        Returns:
            int: Random index number.
        """
        max_value = min(3, idx_range)
        return randrange(max_value)

    @classmethod
    def generate_poi_template(cls, poi: Dict) -> Dict:
        """Template object to be passed to external screen.

        Args:
            poi: POI dictionary object.

        Returns:
            Dict: Template dictionary object.
        """
        pricecat = ""
        if poi.get("price"):
            pricecat = f"({'$' * int(poi.get('price'))})"
        return {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": poi.get("name") + " " + pricecat,
                        "subtitle": poi.get("address"),
                        "iframe_url": cls.get_osm_iframe_url(poi),
                        # "image_url": cls.get_google_maps_img_url(poi),
                    },
                    {
                        "title": "\n",
                        "subtitle": "Learn more:",
                        "image_url": cls.get_qr_code_url(poi.get("website")),
                    },
                ],
            },
        }

    @classmethod
    def get_google_maps_img_url(cls, poi: Dict) -> Text:
        """Gives URL to Google Maps static image based on POI data.

        Args:
            poi: POI entry used to generate URL.
            match: POI entry being recommended.
        """
        address = quote_plus(poi.get("address"))
        you_are_here = quote_plus(CONFERENCE_ADDRESS)
        height = 400
        width = 600
        url = """
            https://maps.googleapis.com/maps/api/staticmap?
            size={width}x{height}
            &markers=color:red%7C{marker1}
            &markers=color:green%7C{path_start}
            &path=color:red%7Cweight:5%7C{path_start}%7C{path_end}
            &key=AIzaSyD_gNJrznPD1R2tjMSqIi9m9IPQyPJ3JaE
        """.format(
            width=width,
            height=height,
            marker1=address,
            path_start=you_are_here,
            path_end=address,
        )
        url = "".join(url.split())
        return url

    @classmethod
    def get_osm_iframe_url(cls, poi: Dict) -> Text:
        """Gives URL to Open Street Map HTML file.

        Args:
            poi: POI entry used to generate URL.
            match: POI entry being recommended.
        """
        address = poi.get("address")
        you_are_here = CONFERENCE_ADDRESS
        filepath = MAPS.get_route_map(you_are_here, address)
        return filepath

    @classmethod
    def get_qr_code_url(cls, url: Text) -> Text:
        """Gives URL to QR code generated from provided URL.

        Args:
            url: Website to generate QR code for.

        Returns:
            Text: URL to QR-code image.
        """
        resolution = 140
        qr_code_api = """
                    https://api.qrserver.com/v1/create-qr-code/
                    ?size={}x{}&data=
        """.format(
            resolution, resolution
        )
        return "".join(qr_code_api.split()) + "".join(url.split())


class ActionRecommendPOI(Action):
    def name(self) -> Text:
        return "action_recommend_poi"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Gives top rated POI match based on provided entities.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'
        """
        match = POIFunctions.get_match(tracker)
        if match:
            return self.recommend_poi(dispatcher, match)
        dispatcher.utter_message(
            response="utter_no_poi_found",
        )
        return [
            SlotSet("recommended_poi", None),
            SlotSet("poi_category", None),
            SlotSet("liked_poi_tags", None),
            SlotSet("disliked_poi_tags", None),
        ]

    def recommend_poi(
        self, dispatcher: CollectingDispatcher, match: Dict
    ) -> List[Dict[Text, Any]]:
        """Utters recommendation based on highest rating.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            match: POI dictionary object.
        """
        if match.get("likes"):
            if match.get("dislikes"):
                POIFunctions.recommend_by_likes_and_dislikes(
                    dispatcher,
                    match,
                    "utter_recommend_poi_by_likes_and_dislikes",
                )
            else:
                POIFunctions.recommend_by_likes(
                    dispatcher, match, "utter_recommend_poi_by_likes"
                )
        else:
            POIFunctions.recommend_by_category(
                dispatcher, match, "utter_recommend_poi_by_category"
            )
        dispatcher.utter_message(
            attachment=POIFunctions.generate_poi_template(match)
        )
        return [
            SlotSet("recommended_poi", match),
            SlotSet("poi_category", match.get("category")),
            SlotSet("liked_poi_tags", match.get("nlu_likes")),
            SlotSet("disliked_poi_tags", match.get("nlu_dislikes")),
        ]


class ActionRecommendCheapPOI(Action):
    def name(self) -> Text:
        return "action_recommend_cheap_poi"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Gives cheap POI match based on provided entities.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'
        """
        match = POIFunctions.get_match(tracker, True)
        if match:
            return self.recommend_poi(dispatcher, match)
        dispatcher.utter_message(
            response="utter_no_poi_found",
        )
        return [
            SlotSet("recommended_poi", None),
            SlotSet("poi_category", None),
            SlotSet("liked_poi_tags", None),
            SlotSet("disliked_poi_tags", None),
        ]

    def recommend_poi(
        self, dispatcher: CollectingDispatcher, match: Dict
    ) -> None:
        """Utters recommendation based on lowest price and highest rating

        Args:
            dispatcher: Class responsible for sending messages back to user.
            match: POI dictionary object.
        """
        if match.get("likes"):
            if match.get("dislikes"):
                POIFunctions.recommend_by_likes_and_dislikes(
                    dispatcher,
                    match,
                    "utter_recommend_cheap_poi_by_likes_and_dislikes",
                )
            else:
                POIFunctions.recommend_by_likes(
                    dispatcher, match, "utter_recommend_cheap_poi_by_likes"
                )
        else:
            POIFunctions.recommend_by_category(
                dispatcher, match, "utter_recommend_cheap_poi_by_category"
            )
        dispatcher.utter_message(
            attachment=POIFunctions.generate_poi_template(match)
        )
        return [
            SlotSet("recommended_poi", match),
            SlotSet("poi_category", match.get("category")),
            SlotSet("liked_poi_tags", match.get("nlu_likes")),
            SlotSet("disliked_poi_tags", match.get("nlu_dislikes")),
        ]


class ActionDoesPOIHave(Action):
    def name(self) -> Text:
        return "action_does_poi_have"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Responds to question on whether a POI has wanted POI tag.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'
        """
        recommended_poi = tracker.get_slot("recommended_poi")
        if not recommended_poi or not POIFunctions.has_new_tags(tracker):
            dispatcher.utter_message(response="utter_nlu_fallback")
            return [
                SlotSet("recommended_poi", recommended_poi),
                SlotSet("poi_category", None),
                SlotSet("liked_poi_tags", None),
                SlotSet("disliked_poi_tags", None),
            ]
        matches = POIFunctions.get_matches_by_likes(tracker)
        if not matches:
            return self.no_matches_found(dispatcher, tracker, recommended_poi)
        for match in matches:
            if int(match.get("id")) == int(recommended_poi.get("id")):
                return self.affirmative(dispatcher, tracker, recommended_poi)
        return self.negative(dispatcher, tracker, recommended_poi, matches[0])

    def affirmative(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        recommended_poi: Dict,
    ) -> List[Dict[Text, Any]]:
        """Utters confirmation that place has POI tag.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            recommended_poi: The POI in question.
        """
        dispatcher.utter_message(
            response="utter_yes_poi_has_tags",
            name=recommended_poi.get("name"),
            likes=POIFunctions.proper_tags_string(
                tracker.get_slot("liked_poi_tags")
            ),
        )
        return [
            SlotSet("recommended_poi", recommended_poi),
            SlotSet("poi_category", None),
            SlotSet("liked_poi_tags", recommended_poi.get("nlu_likes")),
            SlotSet("disliked_poi_tags", None),
        ]

    def negative(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        recommended_poi: Dict,
        new_match: Dict,
    ) -> List[Dict[Text, Any]]:
        """Informs that the POI does not have the wanted POI tags.
        Goes on to recommend another POI that does have it.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            recommended_poi: The POI in question.
            new_match: New POI being recommended.
        """
        dispatcher.utter_message(
            response="utter_poi_does_not_have_tags",
            name=recommended_poi.get("name"),
            likes=POIFunctions.proper_tags_string(
                tracker.get_slot("liked_poi_tags")
            ),
        )
        POIFunctions.recommend_by_likes(
            dispatcher, new_match, "utter_but_this_poi_does_have"
        )
        dispatcher.utter_message(
            attachment=POIFunctions.generate_poi_template(new_match)
        )
        return [
            SlotSet("recommended_poi", new_match),
            SlotSet("poi_category", new_match.get("category")),
            SlotSet("liked_poi_tags", recommended_poi.get("nlu_likes")),
            SlotSet("disliked_poi_tags", None),
        ]

    def no_matches_found(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        recommended_poi: Dict,
    ) -> List[Dict[Text, Any]]:
        """No POI has the user's wanted POI tags.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            recommended_poi: The POI in question.
        """
        dispatcher.utter_message(
            response="utter_no_poi_has",
            likes=POIFunctions.stringify_list(
                tracker.get_slot("liked_poi_tags")
            ),
        )
        return [
            SlotSet("recommended_poi", recommended_poi),
            SlotSet("liked_poi_tags", recommended_poi.get("nlu_likes")),
            SlotSet("disliked_poi_tags", None),
        ]


class ActionRecommendPOITransport(Action):
    CATEGORY_TO_UTTERANCE_MAP = {
        "airport": "utter_route_to_airport",
        "hospital": "utter_route_to_hospital",
    }
    RECOGNIZED_MODES_OF_TRANSPORT = ["taxi", "bus", "walk"]

    def name(self) -> Text:
        return "action_recommend_poi_transport"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Responds to question on whether a POI has wanted POI tag.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'
        """
        transport_preference = tracker.get_slot("transport_preference")
        if not transport_preference:
            dispatcher.utter_message(
                response="utter_answer_other_transport_preferences"
            )
            return []
        if "taxi" in transport_preference:
            dispatcher.utter_message(response="utter_recommend_taxi")
            return []
        if transport_preference not in self.RECOGNIZED_MODES_OF_TRANSPORT:
            dispatcher.utter_message(
                response="utter_answer_other_transport_preferences"
            )
            return []
        recommended_poi = tracker.get_slot("recommended_poi")
        if not recommended_poi or POIFunctions.has_new_category(tracker):
            return self.recommend_transport_in_general(
                dispatcher, tracker, transport_preference
            )
        return self.recommend_transport_to_poi(
            dispatcher, tracker, transport_preference
        )

    def recommend_transport_to_poi(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        preference: Text,
    ) -> List[Dict[Text, Any]]:
        """Recommends transport to POI

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            preference: Transport preference.

        Returns:
            List: Events to be sent to Rasa.
        """
        if preference == "walk":
            self.recommend_transport_by_walking(dispatcher, tracker)
        if preference == "bus":
            self.recommend_transport_by_bus(dispatcher, tracker)
        return [
            SlotSet("liked_poi_tags", None),
            SlotSet("disliked_poi_tags", None),
        ]

    def recommend_transport_by_walking(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
    ) -> None:
        """Utters walking distance to POI or recommends bus.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
        """
        recommended_poi = tracker.get_slot("recommended_poi")
        if POIFunctions.has_walking_distance(tracker):
            dispatcher.utter_message(
                response="utter_walking_distance",
                name=recommended_poi.get("name"),
            )
        else:
            dispatcher.utter_message(response="utter_suggest_bus")
            self.recommend_transport_by_bus(dispatcher, tracker)

    def recommend_transport_by_bus(
        self, dispatcher: CollectingDispatcher, tracker: Tracker
    ) -> None:
        """Generates bus route recommendation to a POI.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
        """
        routes = POIFunctions.get_bus_route(tracker)
        poi = tracker.get_slot("recommended_poi")
        if routes.get("to_destination"):
            if routes.get("to_layover"):
                dispatcher.utter_message(
                    response="utter_layover_bus_route",
                    start=routes.get("to_layover").get("origin"),
                    bus0=routes.get("to_layover").get("number"),
                    dest0=routes.get("to_layover").get("destination"),
                    layover=routes.get("to_destination").get("origin"),
                    bus1=routes.get("to_destination").get("number"),
                    dest1=routes.get("to_destination").get("destination"),
                    distance=poi.get("distance"),
                    name=poi.get("name"),
                )
            else:
                dispatcher.utter_message(
                    response="utter_direct_bus_route",
                    start=routes.get("to_destination").get("origin"),
                    bus=routes.get("to_destination").get("number"),
                    destination=routes.get("to_destination").get("destination"),
                    distance=poi.get("distance"),
                    name=poi.get("name"),
                )
        elif poi.get("distance"):
            dispatcher.utter_message(
                response="utter_walking_distance",
                name=poi.get("name"),
                distance=poi.get("distance"),
            )
        dispatcher.utter_message(response="utter_see_more_bus_info")

    def recommend_transport_in_general(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        preference: Text,
    ) -> List[Dict[Text, Any]]:
        """Generates transport response not based on a specific POI

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            preference: Transport preference.

        Returns:
            List: Events to be sent to Rasa.
        """
        if preference == "walk":
            dispatcher.utter_message(response="utter_encourage_walking")
        if preference == "bus":
            for category, utterance in self.CATEGORY_TO_UTTERANCE_MAP.items():
                if tracker.get_slot("poi_category") == category:
                    dispatcher.utter_message(response=utterance)
                    return []
            dispatcher.utter_message(response="utter_general_bus_information")
        return [
            SlotSet("recommended_poi", None),
            SlotSet("liked_poi_tags", None),
            SlotSet("disliked_poi_tags", None),
        ]
