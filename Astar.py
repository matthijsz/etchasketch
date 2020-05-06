class AStarGraph(object):
    # Define a class board like grid with two barriers
    def __init__(self,img):
        self.barriers = []
        self.img=img
    def heuristic(self, start, goal):
        # Use Chebyshev distance heuristic if we can move one square either
        # adjacent or diagonal
        D = 1
        D2 = 1
        dx = abs(start[0] - goal[0])
        dy = abs(start[1] - goal[1])
        return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)
    def get_vertex_neighbours(self, pos):
        n = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            x2 = pos[0] + dx
            y2 = pos[1] + dy
            if self.img[y2,x2] != 1:
                continue
            n.append((x2, y2))
        return n
def AStarSearch(start, end, graph):
    G = {}  # Actual movement cost to each position from the start position
    F = {}  # Estimated movement cost of start to end going via this position
    # Initialize starting values
    G[start] = 0
    F[start] = graph.heuristic(start, end)
    closedVertices = set()
    openVertices = set([start])
    cameFrom = {}
    while len(openVertices) > 0:
        current = None
        currentFscore = None
        for pos in openVertices:
            if current is None or F[pos] < currentFscore:
                currentFscore = F[pos]
                current = pos
        if current == end:
            # Retrace our route backward
            path = [current]
            while current in cameFrom:
                current = cameFrom[current]
                path.append(current)
            path.reverse()
            return path, F[end]  # Done!
        openVertices.remove(current)
        closedVertices.add(current)
        for neighbour in graph.get_vertex_neighbours(current):
            if neighbour in closedVertices:
                continue  # We have already processed this node exhaustively
            candidateG = G[current] + 1
            if neighbour not in openVertices:
                    openVertices.add(neighbour)  # Discovered a new vertex
            elif candidateG >= G[neighbour]:
                continue  # This G score is worse than previously found
            cameFrom[neighbour] = current
            G[neighbour] = candidateG
            H = graph.heuristic(neighbour, end)
            F[neighbour] = G[neighbour] + H
    raise RuntimeError("Even A* failed to find a solution")
#Read in monochrome B-W image, the pointer will walk over black cells (therefore bitwise_not)

