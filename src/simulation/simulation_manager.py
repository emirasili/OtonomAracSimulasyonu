# Dosya: src/simulation/simulation_manager.py

import pygame
import sys
import os
from simulation.settings import *
from map.map_data import GAME_MAP
from ui.menu import Button
from car.car_manager import Car
from algorithms.pathfinding import PathFinder


# ------------------------------------------------------
# TRAFİK IŞIĞI SINIFI
# ------------------------------------------------------
class TrafficLight:
    """Trafik ışığının durum ve zaman kontrolünü yapıyorum."""

    def __init__(self, row, col, red_time=4, green_time=2.5):
        self.row = row
        self.col = col
        self.red_time = red_time
        self.green_time = green_time
        self.state = "RED"     # ilk durumda kırmızı
        self.timer = 0.0

    def update(self, dt):
        """Her karede zamanlayıcıyı yeniliyorum."""
        self.timer += dt

        if self.state == "RED" and self.timer >= self.red_time:
            self.state = "GREEN"
            self.timer = 0.0

        elif self.state == "GREEN" and self.timer >= self.green_time:
            self.state = "RED"
            self.timer = 0.0


# ------------------------------------------------------
# ANA OYUN SINIFI
# ------------------------------------------------------
class Game:

    def __init__(self):
        pygame.init()

        # Harita boyutları
        self.rows = len(GAME_MAP)
        self.cols = len(GAME_MAP[0])

        # Ekran ayarları
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))

        # Dinamik engeller
        self.dynamic_obstacles = []
        self.img_obstacle = pygame.image.load("assets/obstacle.png")
        self.img_obstacle = pygame.transform.scale(
            self.img_obstacle, (TILE_SIZE, TILE_SIZE)
        )

        pygame.display.set_caption("SAÜTONOM - Akıllı Araç Simülasyonu")
        self.clock = pygame.time.Clock()

        # Yol/duvar/resim yükleme
        self.images = {}
        assets = {
            "v": "road_v.png", "h": "road_h.png",
            "ur": "road_ur.png", "rd": "road_rd.png",
            "dl": "road_dl.png", "lu": "road_lu.png",
            "t_up": "road_t_up.png", "t_down": "road_t_down.png",
            "t_left": "road_t_left.png", "t_right": "road_t_right.png",
            "cross": "road_cross.png",
            1: "wall.png", 2: "water.png",
            3: "start.png", 4: "target.png"
        }

        for key, filename in assets.items():
            path = os.path.join("assets", filename)
            if os.path.exists(path):
                img = pygame.image.load(path)
                self.images[key] = pygame.transform.scale(
                    img, (TILE_SIZE, TILE_SIZE)
                )

        # Yazı tipleri
        self.title_font = pygame.font.SysFont("Verdana", 50, bold=True)
        self.subtitle_font = pygame.font.SysFont("Verdana", 20)
        self.ui_font = pygame.font.SysFont("Arial", 18, bold=True)

        # Menü araba logosu
        car_path = os.path.join("assets", "car.png")
        self.menu_car_img = None
        if os.path.exists(car_path):
            img = pygame.image.load(car_path)
            icon_img = pygame.transform.scale(img, (32, 32))
            pygame.display.set_icon(icon_img)
            img = pygame.transform.scale(img, (140, 140))
            self.menu_car_img = pygame.transform.rotate(img, 45)

        # Oyun durumu
        self.state = "MENU"
        self.selected_algorithm = None
        self.car = None
        self.pathfinder = PathFinder(GAME_MAP)
        self.current_path = []

        # Trafik ışıklarını tara
        self.traffic_lights = []
        for r, row in enumerate(GAME_MAP):
            for c, v in enumerate(row):
                if v == 6:
                    self.traffic_lights.append(TrafficLight(r, c))

        # Butonlar
        cx = self.width // 2 - 100
        cy = self.height // 2 + 70

        self.btn_bfs = Button(cx, cy, 200, 50, "BFS",
                              (0, 100, 200), (0, 150, 255))
        self.btn_dfs = Button(cx, cy + 60, 200, 50, "DFS",
                              (0, 150, 100), (0, 200, 150))
        self.btn_astar = Button(cx, cy + 120, 200, 50,
                                "A*", (200, 50, 50), (255, 80, 80))

        self.btn_back = Button(
            self.width - 120, self.height - 60,
            100, 40, "GERİ", (200, 50, 50), (255, 80, 80)
        )

        # Dinamik engel zamanlama
        self.obstacle_placed = False        # engel yerleştirildi mi?
        self.obstacle_delay = 6.0           # kaç saniye sonra engel gelsin?
        self.time_in_game = 0.0             # oyunda geçen süre

    # ------------------------------------------------------
    # (Şimdilik rastgele üretim kullanmıyoruz ama dursun)
    # ------------------------------------------------------
    def generate_dynamic_obstacles(self, count=1):
        import random
        self.dynamic_obstacles.clear()
        attempts = 0

        while len(self.dynamic_obstacles) < count and attempts < 200:
            attempts += 1
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)

            if GAME_MAP[r][c] == 0:
                self.dynamic_obstacles.append((r, c))

    # ------------------------------------------------------
    def find_pos(self, value):
        for r, row in enumerate(GAME_MAP):
            for c, v in enumerate(row):
                if v == value:
                    return (r, c)
        return None

    # ------------------------------------------------------
    # SİMÜLASYONU BAŞLAT
    # ------------------------------------------------------
    def start_simulation(self, algo_name):
        self.selected_algorithm = algo_name
        self.state = "GAME"

        # Başlangıçta HİÇ DİNAMİK ENGEL YOK
        self.dynamic_obstacles = []
        self.obstacle_placed = False
        self.time_in_game = 0.0

        start = self.find_pos(3)
        goal = self.find_pos(4)

        if not start or not goal:
            print("Start veya hedef bulunamadı.")
            return

        if self.car is None:
            self.car = Car(start[0], start[1])
        else:
            self.car.row, self.car.col = start
            self.car.pixel_x = start[1] * TILE_SIZE
            self.car.pixel_y = start[0] * TILE_SIZE

        # Başlangıç rotasını, seçili algoritmaya göre ENGELSİZ hesapla
        if algo_name == "BFS":
            path = self.pathfinder.bfs(start, goal)
        elif algo_name == "DFS":
            path = self.pathfinder.dfs(start, goal)
        else:  # A*
            path = self.pathfinder.a_star(start, goal)

        self.current_path = path

        if path:
            self.car.set_path(path)
        else:
            print("Yol bulunamadı!")

    # ------------------------------------------------------
    # Araç ilerledikten ve biraz süre geçtikten sonra önüne engel koy
    # ------------------------------------------------------
    def maybe_spawn_obstacle_after_delay(self):
        """
        Hedef:
        - Hoca önce normal rotayı görsün.
        - Araç biraz yürüsün (path_index >= 4 gibi) ve
          ekranda 3–4 saniye geçsin.
        - Sonra, ilerideki bir kareye engel koyulsun.
        """
        if self.obstacle_placed:
            return
        if not self.car or not self.car.path:
            return

        # Hâlâ erken: birkaç saniyelik gecikme
        if self.time_in_game < self.obstacle_delay:
            return

        # Araç path üzerinde biraz yürümüş olsun
        if self.car.path_index < 4:
            return

        # Araçtan İLERİDE bir kare seç (örnek: +6 adım sonrası)
        idx = self.car.path_index + 6
        if idx >= len(self.car.path):
            idx = len(self.car.path) - 2  # hedefe çok yakınsa biraz geriye al

        # Seçilen indeksten ileriye doğru ilk uygun yolu bul
        chosen_cell = None
        for i in range(idx, len(self.car.path) - 1):
            r, c = self.car.path[i]
            # Sadece normal yol hücresi (0) üzerine engel koy
            if GAME_MAP[r][c] == 0:
                chosen_cell = (r, c)
                break

        if not chosen_cell:
            return

        self.dynamic_obstacles = [chosen_cell]
        self.obstacle_placed = True
        print(f"🔴 Dinamik engel yerleştirildi: {chosen_cell}")

    # ------------------------------------------------------
    # ENGEL SONRASI ROTAYI TEKRAR HESAPLA
    # ------------------------------------------------------
    def recalculate_path_after_obstacle(self):
        if not self.car:
            return

        current_pos = (self.car.row, self.car.col)
        goal = self.find_pos(4)

        if not goal:
            print("Hedef bulunamadı!")
            return

        # Seçili algoritmaya göre, artık ENGEL varken yeniden rota hesapla
        if self.selected_algorithm == "BFS":
            new_path = self.pathfinder.bfs(
                current_pos, goal, self.dynamic_obstacles
            )
        elif self.selected_algorithm == "DFS":
            new_path = self.pathfinder.dfs(
                current_pos, goal, self.dynamic_obstacles
            )
        else:
            new_path = self.pathfinder.a_star(
                current_pos, goal, self.dynamic_obstacles
            )

        if new_path:
            print("✅ Yeni rota bulundu.")
            self.current_path = new_path
            self.car.set_path(new_path)
        else:
            print("❌ Yeni rota bulunamadı, araç olduğu yerde kalacak.")

    # ------------------------------------------------------
    # GAME LOOP
    # ------------------------------------------------------
    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == "MENU":
                    if self.btn_bfs.is_clicked(event):
                        self.start_simulation("BFS")
                    elif self.btn_dfs.is_clicked(event):
                        self.start_simulation("DFS")
                    elif self.btn_astar.is_clicked(event):
                        self.start_simulation("A*")

                elif self.state == "GAME":
                    if self.btn_back.is_clicked(event):
                        self.state = "MENU"

            self.screen.fill(BLACK)

            dt = self.clock.tick(FPS) / 1000.0

            # Oyun süresini takip et (GAME modunda)
            if self.state == "GAME":
                self.time_in_game += dt

            for tl in self.traffic_lights:
                tl.update(dt)

            if self.state == "MENU":
                self.draw_menu(mouse_pos)
            else:
                self.draw_game(mouse_pos)

            pygame.display.flip()

    # ------------------------------------------------------
    # MENÜ ÇİZİMİ
    # ------------------------------------------------------
    def draw_menu(self, mouse_pos):
        self.screen.fill((25, 30, 40))

        title = self.title_font.render("SAÜTONOM", True, (255, 215, 0))
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 70)))

        sub = self.subtitle_font.render(
            "Otonom Araç Simülasyonu", True, (200, 200, 200)
        )
        self.screen.blit(sub, sub.get_rect(center=(self.width // 2, 115)))

        if self.menu_car_img:
            self.screen.blit(
                self.menu_car_img,
                self.menu_car_img.get_rect(center=(self.width // 2, 230))
            )

        self.btn_bfs.check_hover(mouse_pos)
        self.btn_dfs.check_hover(mouse_pos)
        self.btn_astar.check_hover(mouse_pos)

        self.btn_bfs.draw(self.screen)
        self.btn_dfs.draw(self.screen)
        self.btn_astar.draw(self.screen)

    # ------------------------------------------------------
    # OYUN ÇİZİMİ
    # ------------------------------------------------------
    def draw_game(self, mouse_pos):
        self.draw_map()
        self.draw_traffic_lights()

        # Araba güncelleme
        if self.car:
            # Önce zamanı ve alınan yolu kontrol edip GECİKMELİ engel koy
            self.maybe_spawn_obstacle_after_delay()

            # Sonra arabayı güncelle (engel varsa Car.update True döndürecek)
            must_replan = self.car.update(
                GAME_MAP, self.traffic_lights, self.dynamic_obstacles
            )

            if must_replan:
                self.recalculate_path_after_obstacle()

            self.car.draw(self.screen)

        # Dinamik engelleri çiz
        for (r, c) in self.dynamic_obstacles:
            x = c * TILE_SIZE
            y = r * TILE_SIZE
            self.screen.blit(self.img_obstacle, (x, y))

        self.draw_path()

        self.btn_back.check_hover(mouse_pos)
        self.btn_back.draw(self.screen)

    # ------------------------------------------------------
    def is_road(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return GAME_MAP[r][c] in [0, 3, 4, 5, 6]
        return False

    # ------------------------------------------------------
    def draw_map(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = GAME_MAP[r][c]
                img = None

                if cell in (0, 5, 6):
                    mask = 0
                    if self.is_road(r - 1, c):
                        mask += 1
                    if self.is_road(r, c + 1):
                        mask += 2
                    if self.is_road(r + 1, c):
                        mask += 4
                    if self.is_road(r, c - 1):
                        mask += 8

                    mapping = {
                        5: "v", 1: "v", 4: "v",
                        10: "h", 2: "h", 8: "h",
                        3: "ur", 6: "rd", 12: "dl",
                        9: "lu", 14: "t_down", 11: "t_up",
                        7: "t_right", 13: "t_left", 15: "cross"
                    }

                    img = self.images.get(mapping.get(mask, "h"))

                else:
                    img = self.images.get(cell)

                if img:
                    self.screen.blit(img, (c * TILE_SIZE, r * TILE_SIZE))

    # ------------------------------------------------------
    def draw_traffic_lights(self):
        for tl in self.traffic_lights:
            x = tl.col * TILE_SIZE
            y = tl.row * TILE_SIZE

            rect = pygame.Rect(
                x + TILE_SIZE // 4,
                y + TILE_SIZE // 4,
                TILE_SIZE // 2,
                TILE_SIZE // 2
            )

            color = (220, 0, 0) if tl.state == "RED" else (0, 180, 0)
            pygame.draw.rect(self.screen, color, rect)

    # ------------------------------------------------------
    def draw_path(self):
        if len(self.current_path) < 2:
            return

        pts = []
        for (r, c) in self.current_path:
            x = c * TILE_SIZE + TILE_SIZE // 2
            y = r * TILE_SIZE + TILE_SIZE // 2
            pts.append((x, y))

        if len(pts) >= 2:
            pygame.draw.lines(self.screen, (255, 255, 255), False, pts, 2)
            pygame.draw.lines(self.screen, (255, 215, 0), False, pts, 4)
