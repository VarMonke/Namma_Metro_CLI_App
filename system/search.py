
from typing import (
    List,
    Dict,
    Optional,
)

from collections import deque

from .objects import Station

def find_path_bfs(start_station: Station, end_station: Station) -> List[Station]:
    """
    Finds the shortest path between two stations using Breadth First Search.
    """
    queue = deque([start_station])
    visited = {start_station}
    parent_map: Dict[Station, Optional[Station]] = {start_station: None}

    while queue:
        current_station = queue.popleft()

        if current_station == end_station:
            break

        for neighbour in current_station.neighbours:
            
            if neighbour not in visited:
                
                visited.add(neighbour)
                
                parent_map[neighbour] = current_station
                
                queue.append(neighbour)

    if end_station not in parent_map:
        return []  

    path = []
    current = end_station
    
    while current is not None:
        path.append(current)
        current = parent_map[current]
    
    path.reverse()
    return path