"""This files contains custom action to get capital of a country."""

from typing import Any, Dict, List, Text

from countryinfo import CountryInfo
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionGetCapital(Action):
    def __init__(self) -> None:
        self.country = CountryInfo()
        self.all_countries = list(self.country.all().keys())

    def name(self) -> Text:
        return "action_get_capital"

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
        location = next(tracker.get_latest_entity_values("GPE"), "Unknown")
        location = location.lower()
        print("Location from the user is", location)

        if location in self.all_countries:
            capital = CountryInfo(location).capital()
            dispatcher.utter_message(
                text=f"The capital of {location.title()} is {capital}."
            )

        else:
            dispatcher.utter_message(
                text=f"I do not know any country with the name {location.title()}."  # noqa
            )
        return []
