"""Interface to retrieve itinerary."""
from typing import Tuple

import folium
import osmnx as ox


class DirectionMap:
    def __init__(self, conference_city: str) -> None:
        """Class using Open Street Map to display directions between 2 points.

        Args:
            conference_city: Conference city.
        """
        self.G = ox.graph_from_place(conference_city, network_type="drive")

    def get_latlong(self, address: str) -> Tuple[float, float]:
        """Retrieves latitude and longitude from an address.

        Args:
            address: Address to get coordinates from.

        Returns:
            Latitude and longitude.
        """
        return ox.geocoder.geocode(address)

    def get_route_map(self, origin: str, destination: str) -> str:
        """Create HTML file with interative maps showing the route between 2
        points.

        Args:
            origin: Origin address.
            destination: Destination address.
            output_file: Path to output HTML file.

        Returns:
            Path to HTML file with the map.
        """
        origin_latlong = self.get_latlong(origin)
        destination_latlong = self.get_latlong(destination)
        orig = ox.distance.nearest_nodes(
            self.G, X=origin_latlong[1], Y=origin_latlong[0]
        )
        dest = ox.distance.nearest_nodes(
            self.G, X=destination_latlong[1], Y=destination_latlong[0]
        )
        route = ox.shortest_path(self.G, orig, dest, weight="travel_time")

        shortest_route_map = ox.plot_route_folium(self.G, route)
        start_marker = folium.Marker(
            location=origin_latlong,
            popup=origin,
            icon=folium.Icon(color="green"),
        )
        end_marker = folium.Marker(
            location=destination_latlong,
            popup=destination,
            icon=folium.Icon(color="red"),
        )
        # add the circle marker to the map
        start_marker.add_to(shortest_route_map)
        end_marker.add_to(shortest_route_map)

        shortest_route_map.save("ui/furhat-screen/assets/map/route.html")
        return "assets/map/route.html"
