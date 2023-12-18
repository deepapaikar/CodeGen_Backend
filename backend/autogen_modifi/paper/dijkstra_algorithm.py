# filename: dijkstra_algorithm.py

import heapq

def dijkstra(graph, start):
    # Initialize distances with infinity and set the distance to the start node to 0
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    
    # Priority queue to hold nodes and their current distances
    priority_queue = [(0, start)]
    
    while priority_queue:
        # Get the node with the smallest distance
        current_distance, current_node = heapq.heappop(priority_queue)
        
        # If this distance is already larger than the stored one, we can skip this node
        if current_distance > distances[current_node]:
            continue
        
        # Check all neighbors of the current node
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            
            # If the calculated distance is less than the known distance, update it
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances

# Example usage:
# Define a graph as a dictionary where keys are node names and values are dictionaries of neighbors with edge weights
graph_example = {
    'A': {'B': 1, 'C': 4},
    'B': {'A': 1, 'C': 2, 'D': 5},
    'C': {'A': 4, 'B': 2, 'D': 1},
    'D': {'B': 5, 'C': 1}
}

# Call the dijkstra function with the graph and the starting node
shortest_paths = dijkstra(graph_example, 'A')
print(shortest_paths)