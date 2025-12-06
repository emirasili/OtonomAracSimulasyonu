# Dosya: src/algorithms/pathfinding.py
import heapq

class PathFinder:
    def __init__(self, game_map):
        self.map = game_map
        self.rows = len(game_map)
        self.cols = len(game_map[0])

    def get_neighbors(self, node):
        """Bir karenin (node) etrafındaki gidilebilir komşuları bulur."""
        neighbors = []
        r, c = node
        # Yukarı, Aşağı, Sol, Sağ
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            # Harita sınırları içinde mi?
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                # Engel (1) veya Su (2) DEĞİLSE geçilebilir
                if self.map[nr][nc] not in [1, 2]:
                    neighbors.append((nr, nc))
        return neighbors

    def reconstruct_path(self, came_from, current):
        """Bulunan yolu geriye doğru takip ederek listeyi oluşturur."""
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse() # Tersten geldiğimiz için düzeltiyoruz
        return path

    # --- 1. BFS (Genişlik Öncelikli Arama) ---
    def bfs(self, start, goal):
        queue = [start]
        came_from = {start: None}

        while queue:
            current = queue.pop(0) # Kuyruğun başından al
            
            if current == goal:
                return self.reconstruct_path(came_from, goal)

            for next_node in self.get_neighbors(current):
                if next_node not in came_from:
                    came_from[next_node] = current
                    queue.append(next_node)
        return [] # Yol bulunamadı

    # --- 2. DFS (Derinlik Öncelikli Arama) ---
    def dfs(self, start, goal):
        stack = [start]
        came_from = {start: None}

        while stack:
            current = stack.pop() # Yığının tepesinden al (Son giren ilk çıkar)
            
            if current == goal:
                return self.reconstruct_path(came_from, goal)

            for next_node in self.get_neighbors(current):
                if next_node not in came_from:
                    came_from[next_node] = current
                    stack.append(next_node)
        return []

    # --- 3. A* (A Yıldız) ---
    def heuristic(self, a, b):
        # Manhattan Mesafesi (Kareli haritalar için ideal)
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, start, goal):
        # Priority Queue (Öncelikli Kuyruk)
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {start: None}
        cost_so_far = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, goal)

            for next_node in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1 # Her adımın maliyeti 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self.heuristic(goal, next_node)
                    heapq.heappush(open_set, (priority, next_node))
                    came_from[next_node] = current
        return []