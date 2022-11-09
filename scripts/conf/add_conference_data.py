"""Script to import RecSys info in conference database."""

import argparse
import re
from datetime import datetime

import pandas as pd
from actions.db_connector import DBConnector

_DEFAULT_DB_NAME = "conference"
_DEFAULT_TIMETABLE_FILE = "db/conf/data/toy_example_timetable.csv"
_DEFAULT_CONTRIBUTIONS_FILE = "db/conf/data/toy_example_contributions.csv"


def get_session_id(db_name: str, date: str, time="") -> int:
    """Gets the id of the session the presentation belongs to.

    Args:
        db_name: Name of the database.
        date: The date in a DD.MM.YYYY format.
        time: The time in HH:MM format.

    Returns:
        The session id.
    """
    db = DBConnector(db_name)

    if time == "":
        where = f"Date = '{date}' AND Type = 'Poster' OR Type"
    else:
        where = f"Date = '{date}' AND Start_time = '{time}'"

    data = db.select_where(
        "timeslots",
        "Date, Start_time, Id",
        where,
    )

    return data[0][2]


def insert_timeslots(timetable_file: str, db_name: str) -> None:
    """Inserts timeslots into timeslots table.

    Args:
        timetable_file: Path to CSV file with timetable.
        db_name: Name of the database.
    """
    df = pd.read_csv(timetable_file).set_index("timeslot")
    db = DBConnector(db_name)

    for i, col in enumerate(df.columns):
        col = re.sub(r"\.\d+", "", col)
        col = f"{col}, {datetime.now().date().year}"
        date = datetime.strptime(col, "%a, %b %d, %Y").date().isoformat()

        serie = df.iloc[:, i].reset_index()
        groups = serie.groupby(serie.columns[-1])
        for name, group in groups:
            group = group.dropna()
            timeslots = group.iloc[:, 0].values.tolist()
            if len(timeslots) == 1:
                split = timeslots[0].split(" – ")
                db.insert_with_fields(
                    "timeslots",
                    {
                        "Date": date,
                        "Start_time": split[0],
                        "End_time": split[1] if len(split) > 1 else None,
                    },
                )
            else:
                start_time = timeslots[0].split(" – ")[0]
                end_time = timeslots[-1].split(" – ")[1]
                db.insert_with_fields(
                    "timeslots",
                    {
                        "Date": date,
                        "Start_time": start_time,
                        "End_time": end_time,
                    },
                )


def insert_overview(timetable_file: str, db_name: str) -> None:
    """Inserts program overview into overview table.

    Args:
        timetable_file: Path to CSV file with timetable.
        db_name: Name of the database.
    """
    df = pd.read_csv(timetable_file).set_index("timeslot")
    db = DBConnector(db_name)

    for i, col in enumerate(df.columns):
        col = re.sub(r"\.\d+", "", col)
        col = f"{col}, {datetime.now().date().year}"
        date = datetime.strptime(col, "%a, %b %d, %Y").date().isoformat()

        serie = df.iloc[:, i].reset_index()
        groups = serie.groupby(serie.columns[-1])
        for name, group in groups:
            group = group.dropna()
            timeslots = group.iloc[:, 0].values.tolist()
            if len(timeslots) == 1:
                split = timeslots[0].split(" – ")
                timeslot_id = get_session_id(db_name, date, split[0])

                db.insert_with_fields(
                    "overview",
                    {
                        "Date": date,
                        "Start_time": split[0],
                        "End_time": split[1] if len(split) > 1 else None,
                        "Type": name,
                        "timeslot_id": timeslot_id,
                    },
                )
            else:
                start_time = timeslots[0].split(" – ")[0]
                end_time = timeslots[-1].split(" – ")[1]
                timeslot_id = get_session_id(db_name, date, start_time)
                db.insert_with_fields(
                    "overview",
                    {
                        "Date": date,
                        "Start_time": start_time,
                        "End_time": end_time,
                        "Type": name,
                        "timeslot_id": timeslot_id,
                    },
                )


def insert_contributions(contribution_file: str, db_name: str) -> None:
    """Inserts contributions into presentations table.

    Args:
        contribution_file: Path to CSV file with contributions.
        db_name: Name of the database.
    """
    df = pd.read_csv(contribution_file)
    db = DBConnector(db_name)

    for i, row in df.iterrows():
        first_author = row["authors"].replace(" and ", ",").split(" ,")[0]
        db.insert_with_fields(
            "presentations",
            {
                "title": row["title"],
                "authors": row["authors"],
                "presenter_name": first_author.strip(),
                "presenter_bio": row["bio"] if "bio" in row else None,
                "picture": row["picture"] if "picture" in row else None,
                "keywords": row["keywords"] if "keywords" in row else None,
            },
        )
        if "Keynote" in row["session_name"]:
            session_data = db.select_where(
                "overview",
                "Type, timeslot_id",
                f"Type LIKE '%{row['session_name']}%{row['authors']}%'",
            )
        else:
            session_data = db.select_where(
                "overview",
                "Type, timeslot_id",
                f"Type LIKE '%{row['session_name']}%'",
            )

        pid = db.select_where(
            "presentations",
            "Id",
            f"title LIKE '{row['title']}' AND authors LIKE '{row['authors']}'"
            if row["title"] == "nan"
            else f"authors LIKE '{row['authors']}'",
        )
        if session_data and pid:
            db.insert_with_fields(
                "sessions",
                {
                    "type": session_data[0][0],
                    "timeslot_id": session_data[0][1],
                    "presentation_id": pid[0][0],
                },
            )


def parse_cmdline_arguments() -> argparse.Namespace:
    """Defines accepted arguments and returns the parsed values.

    Returns:
        Object with a property for each argument.
    """
    parser = argparse.ArgumentParser(prog="add_conference_data.py")
    parser.add_argument(
        "--timetable-file",
        type=str,
        default=_DEFAULT_TIMETABLE_FILE,
        help="Path to the file containing the timetable.",
    )
    parser.add_argument(
        "--contributions-file",
        type=str,
        default=_DEFAULT_CONTRIBUTIONS_FILE,
        help="Path to the file containing the accepted contributions.",
    )
    parser.add_argument(
        "--db-name",
        default=_DEFAULT_DB_NAME,
        help="Name of the database.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cmdline_arguments()

    insert_timeslots(args.timetable_file, args.db_name)
    insert_overview(args.timetable_file, args.db_name)
    insert_contributions(args.contributions_file, args.db_name)
