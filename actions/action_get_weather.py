"""This files contains custom action to get temperature at a certain location.
"""

from typing import Any, Dict, List, Text

from pyowm import OWM
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Returns

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'.
        """
        location = next(tracker.get_latest_entity_values("GPE"), "Stavanger")
        first_name = tracker.get_slot("first_name") or ""
        user_origin = tracker.get_slot("user_origin") or ""
        # user_id = tracker.get_slot("user_ID") or ""

        # TODO #107 Add checks for failed connection and unknown location
        owm = OWM("ccdd2a5f161ff858d26e1ac49e155222")
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(location)
        temp = observation.weather.temperature("celsius")["temp"]

        if user_origin == "":
            dispatcher.utter_message(
                text=f"It is {temp} degrees in {location}."
            )
        elif user_origin.lower() == location.lower():
            dispatcher.utter_message(
                text=f"It is {temp} degrees in {location}."
            )
            dispatcher.utter_message(
                text=f"""I always wanted to visit {location}.
                         Shall I buy tickets for 2 of us, {first_name}?"""
            )
        else:
            observation2 = mgr.weather_at_place(user_origin)
            temp2 = observation2.weather.temperature("celsius")["temp"]
            if temp2 < temp:
                dispatcher.utter_message(
                    text=f"""It is {temp} degrees in {location}.
                             By the way, it is a bit colder in {user_origin}.
                             It is {temp2} degrees there!"""
                )
            else:
                dispatcher.utter_message(
                    text=f"""It is {temp} degrees in {location}.
                             By the way, it is a bit warmer in {user_origin}.
                             It is {temp2} degrees there!"""
                )
        return []
