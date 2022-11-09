"""Script to collect POIs from Tripadvisor."""
import argparse

from scripts.poi.tripadvisor_scraper import TripAdvisorScraper

_DEFAULT_ATTRACTION_LINK = "https://www.tripadvisor.com/Attractions-g190511-Activities-Stavanger_Stavanger_Municipality_Rogaland_Western_Norway.html"  # noqa
_DEFAULT_RESTAURANT_LINK = "https://www.tripadvisor.com/Restaurants-g190511-Stavanger_Stavanger_Municipality_Rogaland_Western_Norway.html" # noqa
_DEFAULT_OUTPUT_FILE = "db/data/poi.tsv"


def parse_cmdline_arguments() -> argparse.Namespace:
    """Defines accepted arguments and returns the parsed values.

    Returns:
        Object with a property for each argument.
    """
    parser = argparse.ArgumentParser(prog="tripadvisor_poi_collection.py")
    parser.add_argument(
        "--attraction-link",
        type=str,
        default=_DEFAULT_ATTRACTION_LINK,
        help="Link with list of attractions to scrape.",
    )
    parser.add_argument(
        "--restaurant-link",
        default=_DEFAULT_RESTAURANT_LINK,
        help="Link with list of restaurants to scrape.",
    )
    parser.add_argument(
        "--output-file",
        default=_DEFAULT_OUTPUT_FILE,
        help="Path to the file to save POIs.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cmdline_arguments()

    scraper = TripAdvisorScraper()
    df_attractions = scraper.get_city_attractions(args.attraction_link)
    df_restaurants = scraper.get_city_restaurants(args.restaurant_link)
    df_poi = df_attractions.append(df_restaurants, ignore_index=True)
    df_poi.to_csv(args.output_file, sep="\t")
