"""This files contains custom action to get local time."""

from datetime import datetime
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionGetTime(Action):
    def name(self) -> Text:
        return "action_get_time"

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
        current_time = datetime.now()
        time_transformed = current_time.time().strftime("%H:%M")
        dispatcher.utter_message(
            text=f"Local time in Stavanger is {time_transformed}."
        )
        return []
