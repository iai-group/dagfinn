"""Script to import TripAdvisor POI into database."""

import argparse

import pandas as pd
from actions.db_connector import DBConnector

_DEFAULT_DATA_FILE = "db/data/poi.tsv"
_DEFAULT_DB_NAME = "poi"


def insert_poi(poi_path: str, db_name: str) -> None:
    """Inserts POI into database.

    Args:
        poi_path: Path to file with POI information.
        db_name: Name of the database.
    """
    df = pd.read_csv(poi_path, sep="\t")
    df = df.dropna(subset="name")
    db = DBConnector(db_name)

    for i, row in df.iterrows():
        db.insert_with_fields(
            "POI",
            {
                "name": row["name"],
                "category": row["category"],
                "rating": row["rating"],
                "price": row["price"],
                "address": row["address"],  # TODO check geocode of address
                "website": row["website"],
            },
        )

        poi_id = db.select_where("POI", "pid", f"name LIKE \"%{row['name']}%\"")

        if poi_id:
            tags = row["category"].split(" • ")
            for tag in tags:
                db.insert_with_fields(
                    "POITag",
                    {
                        "pid": poi_id[0][0],
                        "tag": tag,
                    },
                )


def parse_cmdline_arguments() -> argparse.Namespace:
    """Defines accepted arguments and returns the parsed values.

    Returns:
        Object with a property for each argument.
    """
    parser = argparse.ArgumentParser(prog="tripadvisor_poi_collection.py")
    parser.add_argument(
        "--data-file",
        type=str,
        default=_DEFAULT_DATA_FILE,
        help="Path to the file containing POIs.",
    )
    parser.add_argument(
        "--db-name",
        default=_DEFAULT_DB_NAME,
        help="Name of the database.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cmdline_arguments()

    insert_poi(args.data_file, args.db_name)
