from typing import (
    Set,
    Literal,
    List,
    Optional
)

from dataclasses import dataclass

from .ansi import format_ansi


STATION_TYPE = Literal["middle", "endpoint", "connector"]

class Station:
    """
    A class to hold the station's information.
    This station object can be constructed directly by passing a row of csv data.
    """
    name: str
    code: str
    type: STATION_TYPE
    line: str
    neighbours: Set["Station"]

    def __init__(self, name: str, line: str, type: STATION_TYPE):
        self.name = name
        self.type = type
        self.line = line

        self.neighbours = set() # I am gonna use BFS to go through these stations to find the shortest path and reconstruct, so it doesn't really matter who is "prev" and "next" for my station

    @classmethod
    def from_list(cls, ls: List[str]) -> "Station":
        return cls(ls[1], ls[0].split(".")[0], ls[2]) #type: ignore here the ls[2] does not get casted into STATION_TYPE

    def add_connection(self, station: "Station"):
        self.neighbours.add(station)
        station.neighbours.add(self)

    
class Line:
    """
    Very simple Line object, stores it's own list of stations and it's own color, useful to show routes.
    """
    def __init__(self, color: str) -> None:
        self.color = color
        self.stations: List[Station] = [] # My csv has all this data in an order, so it gets loaded in order as well

    def add_station(self, station: Station):
        """Adds a station to this line's list."""
        self.stations.append(station)

    def print_route(self):
        """Prints all stations on this line."""
        print(format_ansi(f"--- {self.color.upper()} LINE ---", text_color=self.color))
        print("-" * 20)
        for station in self.stations:
            print(f"  - {station.name}")


@dataclass
class Ticket:
    """
    A simple data class to hold a purchased ticket's information.
    """
    ticket_id: str
    stops: int
    fare: float
    start_station: Station
    end_station: Station
    path: List[Station]


    def display(self, display: Optional[bool]= None):
            """Prints a nice readable version of the ticket."""
            WIDTH = 50
            LEFT_PADDING = " " * 2
            LABEL_WIDTH = 10

            print("-" * WIDTH)
            print(f"{LEFT_PADDING}{'TICKET ID:':{LABEL_WIDTH}} {self.ticket_id}")
            print(f"{LEFT_PADDING}{'FROM:':{LABEL_WIDTH}} {format_ansi(text=self.start_station.name, text_color=self.start_station.line)}")
            print(f"{LEFT_PADDING}{'TO:':{LABEL_WIDTH}} {format_ansi(text=self.end_station.name, text_color=self.end_station.line)}")
            print(f"{LEFT_PADDING}{'STOPS:':{LABEL_WIDTH}} {self.stops}")
            print(f"{LEFT_PADDING}{'FARE:':{LABEL_WIDTH}} ₹{self.fare:.2f}")
            print("-" * WIDTH)
            
            if not self.path:
                print(f"{LEFT_PADDING}ROUTE:")

                print(f"{LEFT_PADDING}No path found.")
                print("-" * WIDTH)
                return
            
            # When the person is viewing their tickets, we don't necesarrily need to show the entire path to them, so this is just an Optional[bool] param
            if not display:
                ROUTE_PADDING = " " * 4 
                
                start_station = self.path[0]


                current_line = start_station.line

                print(f"{ROUTE_PADDING}Start at {start_station.name} on the {format_ansi(current_line.upper(), text_color=current_line)} line.\n")

                for i in range(1, len(self.path)):
                    current_station = self.path[i]

                    if current_station.line != current_line:
                        transfer_station = self.path[i-1]
                        
                        print(f"\n{ROUTE_PADDING}(Transfer at {transfer_station.name} to {format_ansi(current_station.line.upper(), text_color=current_station.line)} line)\n")
                        
                        current_line = current_station.line
                        print(f"{ROUTE_PADDING} -> {current_station.name}")

                    else:
                        print(f"{ROUTE_PADDING} -> {current_station.name}")

                print("-" * WIDTH)