from typing import (
    Dict,
    List,
    Tuple,
    Optional,
)

import os
import csv
import uuid
from fuzzywuzzy import process 

from .ansi import format_ansi
from .objects import Station, Line, Ticket
from .search import find_path_bfs


def load_data(csv_path: str) -> Tuple[Dict[str, Station], Dict[str, Line]]:

    lines: Dict[str, Line] = {}
    stations_by_name: Dict[str, List[Station]] = {}
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=",")
            next(reader) # just to skip the header row
            
            for row in reader:
                station = Station.from_list(row)

                if station.line not in lines:
                    lines[station.line] = Line(station.line)
                
                # I have stored my stations in order,
                # so like I can do this without worrying
                lines[station.line].add_station(station)
                
                if station.name not in stations_by_name:
                    stations_by_name[station.name] = []

                stations_by_name[station.name].append(station)

    except FileNotFoundError:
        print(f"Error: The file '{csv_path}' was not found.")
        return {}, {}
    
    except Exception as e:
        print(f"An error occurred while reading the CSV: {e}")
        return {}, {}

    for line in lines.values():
        for i in range(len(line.stations) - 1):
            line.stations[i].add_connection(line.stations[i+1])

    # these stations have the same name but different line, each transfer is also considered as "one stop"

    for station_name, station_list in stations_by_name.items():
        if len(station_list) > 1: # basically checking if it's a connector and connecting the connectors to each other
            for i in range(len(station_list)):
                for j in range(i + 1, len(station_list)):
                    station_list[i].add_connection(station_list[j])

    final_station_lookup: Dict[str, Station] = {}
    for name, station_list in stations_by_name.items():
        if station_list:
            final_station_lookup[name] = station_list[0]
            
    return final_station_lookup, lines


class MetroCLI:
    """
    The main application class that runs the ticket machine.
    """
    FARE_PER_STOP = 10

    def __init__(self, stations: Dict[str, Station], lines: Dict[str, Line]):
        self.stations = stations
        self.lines = lines
        self.purchased_tickets: List[Ticket] = []
        print("\nWelcome to the Namma Metro CLI Ticket System!")

    def _get_station_from_input(self, prompt: str) -> Optional[Station]:
        """
        Helper to get a valid station name from the user,
        with fuzzy matching.
        """
        station_name = input(prompt).strip()
        
        for s_name in self.stations:
            if s_name.lower() == station_name.lower():
                return self.stations[s_name]

        matches = process.extract(station_name, self.stations.keys())
        
        valid_matches = [(m, score) for m, score in matches if score >= 65] #type: ignore

        if valid_matches:
            for i in range(len(valid_matches)):
                match_name = valid_matches[i][0]
            
                confirm = input(f"Did you mean '{match_name}'? (y/n): ").strip().lower()

                if confirm == "y":
                    return self.stations[match_name] 
                
                if confirm == "n":
                    continue

                else:
                    print(format_ansi("Invalid Input. Returning to Main Menu...", text_color="red"))
                    return None

        print(format_ansi(f"Station '{station_name}' not found. Please enter a valid metro station. Returning to Main Menu...", text_color="yellow"))
        return None

    def purchase_ticket(self):
        print("\n--- Purchase New Ticket ---")
        
        start_station = self._get_station_from_input("Enter START station: ")
        if not start_station:
            return

        end_station = self._get_station_from_input("Enter END station: ")
        if not end_station:
            return
            
        if start_station == end_station:
            print("Start and end stations must be different.")
            return

        path = find_path_bfs(start_station, end_station)
        
        if not path:
            print(f"Sorry, no route could be found from {start_station.name} to {end_station.name}.")
            return
        
        if start_station.name == path[1].name:
                path.pop(0)
                start_station = path[0]

        stops = len(path) - 1
        fare = stops * self.FARE_PER_STOP
        ticket_id = start_station.line.upper()[:2] + str(uuid.uuid4()).split('-')[0].upper() + end_station.line.upper()[:2]
        
        new_ticket = Ticket(
            ticket_id=ticket_id,
            start_station=start_station,
            end_station=end_station,
            stops=stops,
            fare=fare,
            path=path
        )
        
        self.purchased_tickets.append(new_ticket)
        
        print(format_ansi(f"\n\nTicket Purchased Successfully!", text_color="green"))
        new_ticket.display()

    def view_tickets(self):
        print("\n--- Your Purchased Tickets ---")
        if not self.purchased_tickets:
            print("You have not purchased any tickets yet.")
            return
        
        for ticket in self.purchased_tickets:
            ticket.display(display=True)

    def list_stations(self):
        print("\n--- All Namma Metro Stations ---")
        print("-" * 20)
        
        for i, line in enumerate(self.lines.values()):
            if i > 0:
                print("-" * 20)
            line.print_route()

    def save_tickets_to_csv(self):
        """
        Saves all purchased tickets to 'data/my_tickets.csv'.
        """
        if not self.purchased_tickets:
            print("No tickets to save. Purchase a ticket by pressing Option 1")
            return

        file_name = "data/my_tickets.csv"
        
        file_exists = os.path.isfile(file_name)

        try:
            with open(file_name, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                if not file_exists:
                    writer.writerow(["TicketID", "From", "To", "Stops", "Fare"])
                
                for ticket in self.purchased_tickets:
                    writer.writerow([
                        ticket.ticket_id,
                        ticket.start_station.name,
                        ticket.end_station.name,
                        ticket.stops,
                        ticket.fare,
                    ])

            print(f"\nSuccessfully saved {len(self.purchased_tickets)} tickets to {file_name}")
        
        except Exception as e:
            print(f"Error saving tickets: {e}")

    def run(self):
        """
        The main application loop.
        """
        try:
            while True:
                print("\n" + "=" * 30)
                print("       MAIN MENU")
                print("=" * 30)
                print("1. Purchase Ticket")
                print("2. View My Tickets")
                print("3. List All Stations by Line")
                print("4. Save My Tickets to CSV")
                print("Q. Quit")
                choice = input("Enter your choice: ").strip().upper()

                match choice:
                    case '1':
                        self.purchase_ticket()
                    case '2':
                        self.view_tickets()
                    case '3':
                        self.list_stations()
                    case '4':
                        self.save_tickets_to_csv()
                    case 'Q':
                        print("Thank you for using Namma Metro CLI.")
                        break
                    case _:
                        print(format_ansi("Invalid choice. Please try again.", text_color="yellow"))

        except KeyboardInterrupt:
            print(format_ansi("\nKeyboard interruption detected", text_color="red"))
            print("\nExiting application... Thank you for using Namma Metro CLI.")
            

def main():
    """
    Loads data and runs the MetroCLI application.
    """
    stations, lines = load_data("data/metro_stations.csv") 
    
    if not stations or not lines:
        print("Failed to load metro data. Exiting.")
        return

    app = MetroCLI(stations=stations, lines=lines)
    app.run()
