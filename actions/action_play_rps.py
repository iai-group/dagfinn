"""Custom action for playing rock-paper-scissors. """


import random
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

CHOICES = ["rock", "paper", "scissors"]


class ActionPlayRPS(Action):
    def name(self) -> Text:
        return "action_play_rps"

    def computer_choice(self) -> Text:
        """Returns a random choice between 'rock', 'paper', and 'scissors'."""
        return random.choice(CHOICES)

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Plays a round of 'rock', 'paper', 'scissors' given user choice stored
        in the 'choice' slot.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'

        """
        user_choice = tracker.get_slot("choice")
        if user_choice not in CHOICES:
            dispatcher.utter_message(response=("utter_rps_wrong_choice"))
            return []

        dispatcher.utter_message(text=f"You chose {user_choice}")
        comp_choice = self.computer_choice()
        dispatcher.utter_message(text=f"The computer chose {comp_choice}")

        if user_choice == comp_choice:
            dispatcher.utter_message(response="utter_rps_tie")
        elif CHOICES.index(user_choice) == (CHOICES.index(comp_choice) + 1) % 3:
            dispatcher.utter_message(response="utter_rps_user_wins")
        else:
            dispatcher.utter_message(response="utter_rps_bot_wins")

        return []
