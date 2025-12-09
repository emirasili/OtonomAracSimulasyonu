# Dosya: src/algorithms/pathfinding.py
import heapq
from map.map_data import GAME_MAP


class PathFinder:

    def __init__(self, game_map):
        self.map = game_map
        self.rows = len(game_map)
        self.cols = len(game_map[0])

    # --------------------------------------------------------
    # Kare yürünebilir mi?
    # --------------------------------------------------------
    def is_walkable(self, r, c):
        return GAME_MAP[r][c] in [0, 3, 4, 5, 6]

    # --------------------------------------------------------
    # Komşu kareleri bul
    # --------------------------------------------------------
    def get_neighbors(self, node, dynamic_obstacles=None):
        neighbors = []
        r, c = node

        directions = [
            (-1, 0),  # yukarı
            (1, 0),   # aşağı
            (0, -1),  # sol
            (0, 1)    # sağ
        ]

        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            # sınır kontrolü
            if 0 <= nr < self.rows and 0 <= nc < self.cols:

                # Yol değilse geçilmez
                if not self.is_walkable(nr, nc):
                    continue

                # Dinamik engel varsa geçilmez
                if dynamic_obstacles and (nr, nc) in dynamic_obstacles:
                    continue

                neighbors.append((nr, nc))

        return neighbors

    # --------------------------------------------------------
    # PATH YENİDEN OLUŞTURMA
    # --------------------------------------------------------
    def reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    # --------------------------------------------------------
    # BFS
    # --------------------------------------------------------
    def bfs(self, start, goal):
        queue = [start]
        came_from = {start: None}

        while queue:
            current = queue.pop(0)

            if current == goal:
                return self.reconstruct_path(came_from, goal)

            for next_node in self.get_neighbors(current):
                if next_node not in came_from:
                    came_from[next_node] = current
                    queue.append(next_node)

        return []

    # --------------------------------------------------------
    # DFS
    # --------------------------------------------------------
    def dfs(self, start, goal):
        stack = [start]
        came_from = {start: None}

        while stack:
            current = stack.pop()

            if current == goal:
                return self.reconstruct_path(came_from, goal)

            for next_node in self.get_neighbors(current):
                if next_node not in came_from:
                    came_from[next_node] = current
                    stack.append(next_node)

        return []

    # --------------------------------------------------------
    # HEURISTIC (Manhattan)
    # --------------------------------------------------------
    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # --------------------------------------------------------
    # A* (Dinamik engel destekli)
    # --------------------------------------------------------
    def a_star(self, start, goal, dynamic_obstacles=None):
        open_set = []
        heapq.heappush(open_set, (0, start))

        came_from = {start: None}
        cost_so_far = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            # Hedef bulundu
            if current == goal:
                return self.reconstruct_path(came_from, goal)

            # Komşular
            for next_node in self.get_neighbors(current, dynamic_obstacles):

                new_cost = cost_so_far[current] + 1

                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self.heuristic(goal, next_node)
                    heapq.heappush(open_set, (priority, next_node))
                    came_from[next_node] = current

        return []
