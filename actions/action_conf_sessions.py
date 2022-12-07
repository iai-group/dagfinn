from datetime import datetime, timedelta
from typing import Any, Dict, List, Text, Tuple

from fuzzywuzzy import process
from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.db_connector import DBConnector

ENDDATE = datetime.strptime("08-11-2022", "%d-%m-%Y")

DB_NAME = "conference"


class ActionGiveSessionRecommendation(Action):
    def name(self) -> Text:
        return "action_recommend_session"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Clears the slots after giving recommendation

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'.
        """

        return [
            SlotSet("session_topic", None),
            SlotSet("session_new", None),
            SlotSet("session_number", 0),
        ]


class ValidateSessionRecommenderForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_session_recommender_form"

    def validate_session_topic(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        index=0,
    ) -> Dict[Text, Any]:
        """Checks the session topic

        Args:
            slot_value: What the slot contains
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'.
            index: Number to pick from the top 5 recommendations
        """

        if tracker.get_intent_of_latest_message() == "stop":
            dispatcher.utter_message(text="Stopping recommendation.")
            return {"session_new": False, "session_topic": slot_value}

        db = DBConnector(DB_NAME)
        matches = recommend_session(slot_value)
        match = matches[index]

        db.cur.execute(
            "SELECT presenter_name, Id, title FROM presentations WHERE "
            "keywords = ?",
            (match[0],),
        )
        session_info = db.cur.fetchall()

        dispatcher.utter_message(text=f"{session_info[0][2]}")

        return {"session_topic": slot_value}

    def validate_session_new(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Checks if user accepts or declines recommendation."""
        if tracker.get_intent_of_latest_message() == "affirm":
            db = DBConnector(DB_NAME)
            index = tracker.get_slot("session_number")
            matches = recommend_session(tracker.get_slot("session_topic"))
            match = matches[index]

            db.cur.execute(
                "SELECT presenter_name, Id, title FROM presentations WHERE "
                "keywords = ?",
                (match[0],),
            )

            presentation = db.cur.fetchall()

            session = db.select_where(
                "sessions",
                "timeslot_id, roomnumber",
                f"presentation_id = {presentation[0][1]}",
            )

            timeslot = db.select_where(
                "timeslots",
                "*",
                f"Id = {session[0][0]}",
            )

            if session[0][1]:
                dispatcher.utter_message(
                    text=f"""The session is hosted by {presentation[0][0]}
                    on {format_timeslot(timeslot[0])} in room
                    {session[0][1]}."""
                )
            else:
                dispatcher.utter_message(
                    text=f"""The session is hosted by {presentation[0][0]}
                    on {format_timeslot(timeslot[0])}."""
                )

            return {"session_new": False, "session_number": 0}

        if tracker.get_intent_of_latest_message() == "deny":
            index = tracker.get_slot("session_number") + 1

            if index > 4:
                topic = tracker.get_slot("session_topic")
                dispatcher.utter_message(
                    text=f"There are no more recommendations for {topic}."
                )
                return {"session_new": True}

            dispatcher.utter_message(
                text="Okay, here is another recommendation:"
            )

            self.validate_session_topic(
                tracker.get_slot("session_topic"),
                dispatcher,
                tracker,
                domain,
                index,
            )
            return {"session_new": None, "session_number": index}

        if tracker.get_intent_of_latest_message() == "stop":
            dispatcher.utter_message(text="Stopping recommendation.")
            return {"session_new": True}

        dispatcher.utter_message(text="I didn't get that.")
        return {"session_new": None}


class ActionGiveSpeakerName(Action):
    def name(self) -> Text:
        return "action_find_speaker"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Finds information about a speaker.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'.
        """

        db = DBConnector(DB_NAME)
        db_names = db.select("presentations", "presenter_name")
        names = []

        for i in db_names:
            names.append(i[0])

        text = tracker.get_slot("speaker_name") or ""
        top = process.extract(text, names)

        for i in top:
            db.cur.execute(
                "SELECT title, Id FROM presentations WHERE "
                "presenter_name = ?",
                (i[0],),
            )

            session_info = db.cur.fetchall()

            sessions = db.select_where(
                "sessions", "*", f"presentation_id = {session_info[0][1]}"
            )

            session_time = db.select_where(
                "timeslots", "start_time, date", f"Id = {sessions[0][3]}"
            )

            dispatcher.utter_message(
                text=f"""{i[0]} is hosting {session_info[0][0]}
                 that starts at {session_time[0][0]} on the
                  {session_time[0][1]}"""
            )
            break

        return [SlotSet("speaker_name", None)]


class ActionInfoNextSession(Action):
    def name(self) -> Text:
        return "action_info_next_session"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Finds information about next session

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'.
        """

        time_and_date = get_current_date_and_time()
        curdate = time_and_date.date()

        if curdate > ENDDATE.date():
            dispatcher.utter_message(text="There are no more sessions.")
            return

        db = DBConnector(DB_NAME)
        sessions = get_session_information(db)

        session_types = []

        for session in sessions:
            session_types.append(session[1])

        session_types = set(session_types)

        new_session_types = []
        for i in session_types:
            new_session_types.append(i)

        type = new_session_types[0].split()
        type = type[0]

        sessions = []
        for i in new_session_types:
            temp_sessions = db.select_where(
                "sessions",
                "img, timeslot_id, roomnumber",
                f"LOWER(type) = LOWER('{i}')",
            )
            sessions.append(temp_sessions)

        if type == "Tutorial" or type == "Workshop":
            dispatcher.utter_message(
                text="""The next sessions are Workshop
                 and Tutorial"""
            )

        if len(session_types) == 1:
            message = {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": check_day("today"),
                            "subtitle": f"Room: {sessions[0][0][2]}",
                            "image_url": f"{sessions[0][0][0]}",
                        },
                    ],
                },
            }
            if sessions[0][0][0]:
                dispatcher.utter_message(
                    text=f"The next session is {new_session_types[0]}.",
                    attachment=message,
                )
            else:
                dispatcher.utter_message(
                    text=f"The next session is {new_session_types[0]}."
                )
        elif len(session_types) == 2:
            message = {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": check_day("today"),
                            "subtitle": f"Room: {sessions[0][0][2]}",
                            "image_url": f"{sessions[0][0][0]}",
                        },
                        {
                            "title": check_day("today"),
                            "subtitle": f"Room: {sessions[1][0][2]}",
                            "image_url": f"{sessions[1][0][0]}",
                        },
                    ],
                },
            }

            if sessions[0][0][0] and sessions[1][0][0]:
                dispatcher.utter_message(
                    text=f"""The next sessions are {new_session_types[0]}
                    and {new_session_types[1]}""",
                    attachment=message,
                )
            else:
                dispatcher.utter_message(
                    text=f"""The next sessions are {new_session_types[0]}
                    and {new_session_types[1]}""",
                )

        return []


class ActionKeynoteSpeakers(Action):
    def name(self) -> Text:
        return "action_keynote_speakers"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Gives information about the keynotes.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'.
        """
        db = DBConnector(DB_NAME)
        keynotes = db.select_where(
            "sessions",
            "timeslot_id, presentation_id",
            "LOWER(type) LIKE '%keynote%' ORDER BY timeslot_id ASC",
        )

        if keynotes:
            dispatcher.utter_message(
                text=(
                    f"There are {len(keynotes)} keynotes during the conference."
                ),
            )
            response = ""
            for timeslot_id, presentation_id in keynotes:
                timeslot = db.select_where(
                    "timeslots", "*", f"Id={timeslot_id}"
                )
                speaker = db.select_where(
                    "presentations", "authors", f"Id={presentation_id}"
                )
                if timeslot and speaker:
                    response += f"""{speaker[0][0]} will give a talk on
                     {format_timeslot(timeslot[0])}.\n"""
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(
                text="Sorry I don't have information regarding the keynotes.",
            )

        return []


class ActionKeynoteInfo(Action):
    def name(self) -> Text:
        return "action_keynote_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Gives more information about keynotes.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'.
        """
        db = DBConnector(DB_NAME)

        day = tracker.get_slot("conference_day")
        type = tracker.get_slot("keynote_number")
        if type == "keynote 1" or type == "keynote one":
            day = "tuesday"

        date = check_day(day)

        keynote = db.cur.execute(
            "SELECT sessions.presentation_id, sessions.img, "
            "sessions.timeslot_id, timeslots.Date, timeslots.Start_time, "
            "timeslots.End_time from sessions JOIN timeslots ON "
            "sessions.timeslot_id=timeslots.id where LOWER(sessions.type) "
            f"LIKE '%keynote%' AND timeslots.Date='{date}'"
        )
        keynote = db.cur.fetchall()

        if keynote:
            timeslot = format_timeslot(tuple(keynote[0][2:]))
            image_url = keynote[0][1]
            speaker = db.select_where(
                "presentations", "authors", f"Id={keynote[0][0]}"
            )
            if speaker:
                message = {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": date,
                                "image_url": image_url,
                            },
                        ],
                    },
                }
                dispatcher.utter_message(attachment=message)
                dispatcher.utter_message(
                    text=(
                        f"The keynote is hosted by {speaker[0][0]} on "
                        f"{timeslot}."
                    )
                )
            else:
                dispatcher.utter_message(
                    text=(
                        "Sorry I could not find the keynote you are referring "
                        "to."
                    ),
                )
        else:
            dispatcher.utter_message(
                text="Sorry I could not find the keynote you are referring to.",
            )

        return []


class ActionConferenceSchedule(Action):
    def name(self) -> Text:
        return "action_find_schedule"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Gets the schedule for the conference.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'.
        """
        day = tracker.get_slot("conference_day")

        date = check_day(day)

        pic = None
        if date == "2022-11-07":
            pic = "assets/conf_images/schedule_mon.jpg"

        if date == "2022-11-08":
            pic = "assets/conf_images/schedule_tue.jpg"

        if pic:
            message = {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": date,
                            "image_url": f"{pic}",
                        },
                    ],
                },
            }
            dispatcher.utter_message(
                attachment=message,
                text=f"Here is the schedule for the {date}.",
            )
        else:
            dispatcher.utter_message(
                text=f"Sorry I cannot find the schedule for the {date}."
            )
        return [SlotSet("conference_day", None)]


class ActionSessionInformation(Action):
    def name(self) -> Text:
        return "action_find_session_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Gets information about a session.

        Args:
            dispatcher: Class responsible for sending messages back to user.
            tracker: Class that maintains the state of a conversation.
            domain: Dictionary containing information stored in 'domain.yml'.
        """
        type = tracker.get_slot("session_type")
        type = check_session_number(type)
        type = type.lower() if type else type

        db = DBConnector(DB_NAME)

        sessions = db.select_where(
            "sessions",
            "img, timeslot_id, roomnumber",
            f'type LIKE "%{type}%"',
        )

        if len(sessions) == 0:
            dispatcher.utter_message(text="Please use a valid session.")
            return

        timeslot = db.select_where(
            "timeslots",
            "date",
            f"Id = {sessions[0][1]}",
        )

        message = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": timeslot[0][0],
                        "subtitle": f"Room: {sessions[0][2]}"
                        if sessions[0][2]
                        else "",
                        "image_url": f"{sessions[0][0]}",
                    },
                ],
            },
        }
        dispatcher.utter_message(attachment=message)

        return [SlotSet("session_id", None)]


def check_day(day) -> str:
    """Matches the name of a day to a date.

    Args:
        day: The day

    Returns:
        The date.
    """
    day = day or "today"

    curdate = get_current_date_and_time()

    if day.lower() == "today" or day.lower() == "todays":
        date = curdate.date().strftime("%Y-%m-%d")

    if day.lower() == "tomorrow" or day.lower() == "tomorrows":
        date = curdate + timedelta(days=1)
        date = date.date().strftime("%Y-%m-%d")

    if day.lower() == "monday" or day.lower() == "mondays":
        date = "2022-11-07"

    if day.lower() == "tuesday" or day.lower() == "tuesdays":
        date = "2022-11-08"

    return date


def get_session_information(db) -> list:
    """Gets information about sessions.

    Args:
        db: The database it will use.

    Returns:
        A list of sessions.
    """

    start_time = db.select("timeslots", "Id, start_time, date")

    time_and_date = get_current_date_and_time()
    curdate = time_and_date.date().isoformat()
    curtime = time_and_date.time()

    for i in start_time:
        date = i[2].split("-")
        date = f"{date[0]}-{date[1]}-{date[2]}"
        date = datetime.strptime(date, "%Y-%m-%d")
        date = date.date().isoformat()
        starttime = datetime.strptime(i[1], "%H:%M")
        starttime = starttime.time()
        if curdate == date:
            if curtime < starttime:
                sessions = db.select_where(
                    "sessions", "*", f"timeslot_id = {i[0]}"
                )
                if len(sessions) == 0:
                    continue
                break
        elif curdate < date:
            sessions = db.select_where("sessions", "*", f"timeslot_id = {i[0]}")
            if len(sessions) == 0:
                continue
            break
        else:
            sessions = []

    return sessions


def recommend_session(phrase) -> list:
    """Matches entered phrase with keywords and recommends session.

    Returns:
        A list with the 5 most relevant sessions.
    """
    db = DBConnector(DB_NAME)
    time_and_date = get_current_date_and_time()
    date = time_and_date.date().strftime("%Y-%m-%d")
    time = time_and_date.time().strftime("%H:%M")
    timeslots = db.select_where(
        "timeslots",
        "Id",
        f"date > '{date}' OR (date = '{date}' AND start_time >= '{time}')",
    )

    sessions = db.select_where(
        "sessions", "presentation_id", f"timeslot_id >= {timeslots[0][0]}"
    )

    sessions = set(sessions)
    keywords = []

    for id in sessions:
        keyword = db.select_where("presentations", "keywords", f"Id = {id[0]}")
        keywords.append(keyword[0][0])

    top = process.extract(phrase or "", keywords)
    return top


def get_current_date_and_time() -> datetime:
    """Returns current date and time."""
    return datetime.now()


def check_session_number(type) -> str:
    """Matches words and numbers.

    Args:
        type: A session type.

    Returns:
        A session type with appropriate number.
    """

    type_split = type.split()
    num = type_split[-1]
    word_numbers = {
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
        "eleven": "11",
    }

    if num.isdigit():
        return type
    else:
        for k, v in word_numbers.items():
            if num == k:
                type = " ".join(type_split[:-1])
                type = f"{type} {v}"
                return type


def format_timeslot(timeslot: Tuple) -> str:
    """Formats timeslot extracted from DB to text.

    Args:
        timeslot: DB entry.

    Returns:
        Timeslot formatted in plain text.
    """
    date_start = datetime.fromisoformat(f"{timeslot[1]}").strftime("%b %d")
    return f"{date_start} between {timeslot[2]} and {timeslot[3]}"
