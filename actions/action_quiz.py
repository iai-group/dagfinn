from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionQuiz(Action):
    def name(self) -> Text:
        return "action_quiz"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        message = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": "Question 1",
                        "subtitle": "What is my favorite color?",
                        "image_url": "https://tinyurl.com/mrh8akwp",
                        "buttons": [
                            {
                                "title": "Red",
                                "payload": "red",
                                "type": "postback",
                            },
                            {
                                "title": "Blue",
                                "payload": "blue",
                                "type": "postback",
                            },
                        ],
                    },
                    {
                        "title": "Question 2",
                        "subtitle": "What is your favorite color?",
                        "image_url": "https://tinyurl.com/mrh8akwp",
                        "buttons": [
                            {
                                "title": "Red",
                                "payload": "red",
                                "type": "postback",
                            },
                            {
                                "title": "Blue",
                                "payload": "blue",
                                "type": "postback",
                            },
                        ],
                    },
                ],
            },
        }
        dispatcher.utter_message(attachment=message)
        return []
