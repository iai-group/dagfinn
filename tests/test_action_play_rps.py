import random

import pytest
from actions.action_play_rps import ActionPlayRPS
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


@pytest.mark.parametrize(
    "choice",
    [None, "scisor", "Rockk"],
)
def test_invalid_slot(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    domain: DomainDict,
    choice: str,
) -> None:
    tracker.slots["choice"] = choice
    action = ActionPlayRPS()

    actual_events = action.run(dispatcher, tracker, domain)

    assert actual_events == []
    assert len(dispatcher.messages) == 1
    assert dispatcher.messages[0]["template"] == "utter_rps_wrong_choice"


@pytest.mark.parametrize(
    "choice, outcome",
    [
        ("rock", "utter_rps_user_wins"),
        ("paper", "utter_rps_bot_wins"),
        ("scissors", "utter_rps_tie"),
    ],
)
def test_bot_chooses_scissors(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    domain: DomainDict,
    choice: str,
    outcome: str,
) -> None:
    tracker.slots["choice"] = choice
    random.seed(5)
    action = ActionPlayRPS()

    actual_events = action.run(dispatcher, tracker, domain)

    assert actual_events == []
    assert len(dispatcher.messages) == 3
    assert dispatcher.messages[2]["template"] == outcome


@pytest.mark.parametrize(
    "choice, outcome",
    [
        ("rock", "utter_rps_tie"),
        ("paper", "utter_rps_user_wins"),
        ("scissors", "utter_rps_bot_wins"),
    ],
)
def test_bot_chooses_rock(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    domain: DomainDict,
    choice: str,
    outcome: str,
) -> None:
    tracker.slots["choice"] = choice
    random.seed(1)
    action = ActionPlayRPS()

    actual_events = action.run(dispatcher, tracker, domain)

    assert actual_events == []
    assert len(dispatcher.messages) == 3
    assert dispatcher.messages[2]["template"] == outcome


@pytest.mark.parametrize(
    "choice, outcome",
    [
        ("rock", "utter_rps_bot_wins"),
        ("paper", "utter_rps_tie"),
        ("scissors", "utter_rps_user_wins"),
    ],
)
def test_bot_chooses_paper(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    domain: DomainDict,
    choice: str,
    outcome: str,
) -> None:
    tracker.slots["choice"] = choice
    random.seed(0)
    action = ActionPlayRPS()

    actual_events = action.run(dispatcher, tracker, domain)

    assert actual_events == []
    assert len(dispatcher.messages) == 3
    assert dispatcher.messages[2]["template"] == outcome
