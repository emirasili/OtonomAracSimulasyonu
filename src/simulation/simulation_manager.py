# Dosya: src/simulation/simulation_manager.py

import pygame
import sys
import os
from simulation.settings import *
from map.map_data import GAME_MAP
from ui.menu import Button
from car.car_manager import Car
from algorithms.pathfinding import PathFinder
import time

class SimulationMetrics:
    def __init__(self, algorithm_name):
        self.algorithm_name = algorithm_name
        self.start_time = time.time()
        self.end_time = None
        self.frame_count = 0
        self.total_distance = 0
        self.last_cell = None
        self.finished = False

    def update(self, car):
        self.frame_count += 1

        cell = (car.row, car.col)
        if self.last_cell is not None:
            self.total_distance += abs(cell[0] - self.last_cell[0]) + abs(cell[1] - self.last_cell[1])

        self.last_cell = cell

    def finish(self):
        if self.finished:
            return

        self.finished = True
        self.end_time = time.time()
        total_time = self.end_time - self.start_time

        print("\n==============================")
        print("🚗 SİMÜLASYON RAPORU")
        print("==============================")
        print(f"Algoritma        : {self.algorithm_name}")
        print(f"Toplam Süre      : {total_time:.2f} saniye")
        print(f"Toplam Kare      : {self.frame_count}")
        print(f"Yol Uzunluğu     : {self.total_distance} birim")
        print("==============================\n")


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
        
        # --- MÜZİK AYARLARI ---
        try:
            pygame.mixer.init()
            music_path = os.path.join("assets", "menuMusic.mp3")  # dosya adını kendine göre ayarla
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.4)  # 0.0 - 1.0 arası
                pygame.mixer.music.play(-1)         # -1 = sonsuz döngü
            else:
                print("Müzik dosyası bulunamadı:", music_path)
        except Exception as e:
            print("Müzik başlatılamadı:", e)


        # Harita boyutları
        self.rows = len(GAME_MAP)
        self.cols = len(GAME_MAP[0])

       # Ekran ayarları
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))

        # --- PENCERE AYARLARI ---
        pygame.display.set_caption("SAÜTONOM - Akıllı Araç Simülasyonu")
        self.clock = pygame.time.Clock()  # FPS kontrolü için saat nesnesi
        
         # --- MENÜ ARKA PLANI ---
        self.menu_bg = None
        bg_path = os.path.join("assets", "menuBackground.png")
        if os.path.exists(bg_path):
            bg_img = pygame.image.load(bg_path).convert()
            self.menu_bg = pygame.transform.scale(bg_img, (self.width, self.height))

        # Dinamik engeller
        self.dynamic_obstacles = []
        
        # Engel görseli yükleme (obstacle.png)
        obstacle_path = "assets/obstacle.png"
        self.img_obstacle = None
        if os.path.exists(obstacle_path):
             self.img_obstacle = pygame.image.load(obstacle_path)
             self.img_obstacle = pygame.transform.scale(self.img_obstacle, (TILE_SIZE, TILE_SIZE))
        else:
             self.img_obstacle = pygame.Surface((TILE_SIZE, TILE_SIZE))
             self.img_obstacle.fill((200, 50, 50))


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
            3: "start.png", 4: "target.png",
            7: "crosswalk.png", # Yaya geçidi ana zemini
            "traffic_light_img": "traffic_light.png" # Işık direği
        }

        for key, filename in assets.items():
            path = os.path.join("assets", filename)
            if os.path.exists(path):
                img = pygame.image.load(path)
                self.images[key] = pygame.transform.scale(
                    img, (TILE_SIZE, TILE_SIZE)
                )

        # Yaya geçidi zemini (Eğer crosswalk.png yoksa)
        if 7 not in self.images:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((50, 50, 50)) 
            self.images[7] = s
        
        # --- MENÜ TASARIM ÖGELERİ ---
        # Yazı Tipleri (Fontlar)
        self.title_font = pygame.font.SysFont("Verdana", 50, bold=True)
        self.subtitle_font = pygame.font.SysFont("Verdana", 20)
        self.ui_font = pygame.font.SysFont("Arial", 18, bold=True)

        # Menüdeki Büyük Araba Logosu
        car_path = os.path.join("assets", "car.png")
        self.menu_car_img = None
        if os.path.exists(car_path):
            img = pygame.image.load(car_path)

            # Pencere İkonunu Ayarla (Sol üstteki küçük ikon)
            icon_img = pygame.transform.scale(img, (32, 32))
            pygame.display.set_icon(icon_img)

            # Menü logosunu büyüt ve hafif döndür
            img = pygame.transform.scale(img, (140, 140))
            self.menu_car_img = pygame.transform.rotate(img, 45)

        # --- OYUN DURUM DEĞİŞKENLERİ ---
        self.state = "MENU"  # Başlangıç durumu (MENU veya GAME olabilir)
        self.selected_algorithm = None
        self.car = None
        self.pathfinder = PathFinder(GAME_MAP)  # Yol bulma motorunu başlat
        self.metrics = None


        # Trafik ışıklarını tara
        self.traffic_lights = []
        for r, row in enumerate(GAME_MAP):
            for c, v in enumerate(row):
                if v == 6:
                    self.traffic_lights.append(TrafficLight(r, c))

       # --- BUTON GÖRSELLERİNİN YÜKLENMESİ ---
        def load_button_images(base_filename, hover_filename):
            base_img = hover_img = None
            base_path = os.path.join("assets", base_filename)
            hover_path = os.path.join("assets", hover_filename)

            if os.path.exists(base_path):
                base_img = pygame.image.load(base_path).convert_alpha()
            if os.path.exists(hover_path):
                hover_img = pygame.image.load(hover_path).convert_alpha()
            return base_img, hover_img

        bfs_img, bfs_hover = load_button_images("arayuzButton1.png", "arayuzButton1hover.png")
        dfs_img, dfs_hover = load_button_images("arayuzButton2.png", "arayuzButton2hover.png")
        astar_img, astar_hover = load_button_images("arayuzButton3.png", "arayuzButton3hover.png")

        # Referans görsele göre konumlar (1280x720 tasarım)
        # Tasarımda butonların kapladığı dikdörtgenler:
        # x = 910, w ≈ 240
        # y = 376 / 466 / 555, h ≈ 70
        OFFSET_X = -60  # sola kaydırma miktarı
        bfs_x, bfs_y   = 910 + OFFSET_X, 376
        dfs_x, dfs_y   = 910 + OFFSET_X, 466
        astar_x, astar_y = 910 + OFFSET_X, 555
        btn_w, btn_h = 240, 70

        # Algoritma Seçim Butonları (görsel tabanlı)py
        # Button sınıfı image verilirse kendi rect'ini image boyutuna göre
        # ayarlıyor ama topleft bu x,y değerlerinde kalıyor.
        self.btn_bfs = Button(
            bfs_x, bfs_y, btn_w, btn_h,
            "", (0, 0, 0), (0, 0, 0),
            image=bfs_img, hover_image=bfs_hover
        )
        self.btn_dfs = Button(
            dfs_x, dfs_y, btn_w, btn_h,
            "", (0, 0, 0), (0, 0, 0),
            image=dfs_img, hover_image=dfs_hover
        )
        self.btn_astar = Button(
            astar_x, astar_y, btn_w, btn_h,
            "", (0, 0, 0), (0, 0, 0),
            image=astar_img, hover_image=astar_hover
        )

        # Oyun içi "GERİ DÖN" Butonu (Sağ Alt Köşe) - eski stil dikdörtgen
        self.btn_back = Button(
            self.width - 110, self.height - 50,
            100, 40, "GERİ",
            (200, 50, 50), (255, 80, 80)
        )

        # Dinamik engel zamanlama
        self.obstacle_placed = False        
        self.obstacle_delay = 6.0           
        self.time_in_game = 0.0             

    # ------------------------------------------------------
    def find_pos(self, value):
        for r, row in enumerate(GAME_MAP):
            for c, v in enumerate(row):
                if v == value:
                    return (r, c)
        return None
    
    def find_water_center_px(self):
        """Haritadaki su hücrelerinin (2) ağırlık merkezini piksel olarak döndürür."""
        cells = []
        for r, row in enumerate(GAME_MAP):
            for c, v in enumerate(row):
                if v == 2:
                    cells.append((r, c))

        if not cells:
            # su yoksa ekran ortası
            return (self.width // 2, 40)

        avg_r = sum(r for r, _ in cells) / len(cells)
        avg_c = sum(c for _, c in cells) / len(cells)

        x = int(avg_c * TILE_SIZE + TILE_SIZE // 2)
        y = int(avg_r * TILE_SIZE + TILE_SIZE // 2)

        # üstte kalsın diye biraz yukarı çekelim
        y = max(30, y - 120)

        return (x, y)


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
            self.metrics = SimulationMetrics(self.selected_algorithm)

        else:
            print("Yol bulunamadı!")

    # ------------------------------------------------------
    # Araç ilerledikten ve biraz süre geçtikten sonra önüne engel koy
    # ------------------------------------------------------
    def maybe_spawn_obstacle_after_delay(self):
        """Dinamik engeli gecikmeyle yerleştirir."""
        if self.obstacle_placed:
            return
        if not self.car or not self.car.path:
            return

        if self.time_in_game < self.obstacle_delay:
            return

        if self.car.path_index < 4:
            return

        idx = self.car.path_index + 6
        if idx >= len(self.car.path):
            idx = len(self.car.path) - 2  

        chosen_cell = None
        for i in range(idx, len(self.car.path) - 1):
            r, c = self.car.path[i]
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
        """Menü ekranını çizer (Arkaplan, Başlık, Butonlar)"""
        # Yeni arka plan
        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill((25, 30, 40))  # Yedek Koyu Gri/Lacivert

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
            if self.metrics:
                self.metrics.update(self.car)

            self.maybe_spawn_obstacle_after_delay()

            must_replan = self.car.update(
                GAME_MAP, self.traffic_lights, self.dynamic_obstacles
            )

            if must_replan:
                self.recalculate_path_after_obstacle()

            self.car.draw(self.screen)
            if self.metrics and self.car.path and self.car.path_index >= len(self.car.path):
                self.metrics.finish()


        # Dinamik engelleri çiz
        for (r, c) in self.dynamic_obstacles:
            x = c * TILE_SIZE
            y = r * TILE_SIZE
            self.screen.blit(self.img_obstacle, (x, y))

        self.draw_path()

        # -------------------------------
        # ALFORİTMA PANELİ (Üst Orta)
        # -------------------------------
        panel_w, panel_h = 240, 45
        info_surf = pygame.Surface((panel_w, panel_h))
        info_surf.set_alpha(200)
        info_surf.fill((20, 20, 20))

        cx, cy = self.find_water_center_px()
        panel_x = (self.width - panel_w) // 2 - 70
        panel_y = 15  # üstten boşluk

        self.screen.blit(info_surf, (panel_x, panel_y))
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_w, panel_h), 2)

        text = self.ui_font.render(f"Algoritma: {self.selected_algorithm}", True, ORANGE)
        text_rect = text.get_rect(center=(panel_x + panel_w // 2, panel_y + panel_h // 2))
        self.screen.blit(text, text_rect)
        
        # -------------------------------
        # HIZ PANELİ (Alt Orta)
        # -------------------------------
        speed_w, speed_h = 240, 45
        speed_surf = pygame.Surface((speed_w, speed_h))
        speed_surf.set_alpha(220)
        speed_surf.fill((20, 20, 20))

        speed_x = (self.width - panel_w) // 2 - 70
        speed_y = self.height - speed_h - 5   # alt boşluk (istersen 25 yap)

        self.screen.blit(speed_surf, (speed_x, speed_y))
        pygame.draw.rect(self.screen, WHITE, (speed_x, speed_y, speed_w, speed_h), 2)

        # aktif hız (car yoksa 0 göster)
        active_speed = self.car.current_speed if (self.car and hasattr(self.car, "current_speed")) else 0
        speed_text = self.ui_font.render(f"Hız: {active_speed:.1f}", True, ORANGE)
        # ortala
        speed_rect = speed_text.get_rect(center=(speed_x + speed_w // 2, speed_y + speed_h // 2))
        self.screen.blit(speed_text, speed_rect)
        
    # "Geri Dön" Butonunu Çiz
        self.btn_back.check_hover(mouse_pos)
        self.btn_back.draw(self.screen)

    # ------------------------------------------------------
    def is_road(self, r, c):
        # Yaya geçidi (7) de yol sayılır
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return GAME_MAP[r][c] in [0, 3, 4, 5, 6, 7]
        return False

    # ------------------------------------------------------
    def draw_map(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = GAME_MAP[r][c]
                img = None

                # YOL, KAVŞAK, IŞIK veya YAYA GEÇİDİ için yol çiz
                if cell in (0, 5, 6, 7):
                    mask = 0
                    if self.is_road(r - 1, c): mask += 1
                    if self.is_road(r, c + 1): mask += 2
                    if self.is_road(r + 1, c): mask += 4
                    if self.is_road(r, c - 1): mask += 8

                    mapping = {
                        5: "v", 1: "v", 4: "v",
                        10: "h", 2: "h", 8: "h",
                        3: "ur", 6: "rd", 12: "dl",
                        9: "lu", 14: "t_down", 11: "t_up",
                        7: "t_right", 13: "t_left", 15: "cross"
                    }

                    # Yaya Geçidi (7) için zemin yolunu seç, diğerleri için normal maske
                    img_key = mapping.get(mask, "h")
                    if cell == 7:
                        img = self.images.get(7) # Yaya geçidi zemini
                    else:
                        img = self.images.get(img_key)
                else:
                    img = self.images.get(cell)

                if img:
                    self.screen.blit(img, (c * TILE_SIZE, r * TILE_SIZE))
        
        # Yaya geçitlerinin çizgilerini en üstte çiz (Yolun üzerine)
        self.draw_crosswalk_lines()


    def draw_crosswalk_lines(self):
        """Yaya geçitlerinin beyaz çizgilerini haritanın üzerine çizer."""
        for r in range(self.rows):
            for c in range(self.cols):
                if GAME_MAP[r][c] == 7:
                    x = c * TILE_SIZE
                    y = r * TILE_SIZE
                    
                    # Yolun yatay mı dikey mi olduğunu kontrol et
                    is_horizontal = self.is_road(r, c-1) or self.is_road(r, c+1)
                    
                    if is_horizontal:
                        # Yatay yol üzerinde DİKEY çizgiler çiz (Klasik yaya geçidi)
                        for i in range(5, TILE_SIZE, 8):
                            pygame.draw.rect(self.screen, WHITE, (x, y + i, TILE_SIZE, 4))
                    else:
                        # Dikey yol üzerinde YATAY çizgiler çiz
                        for i in range(5, TILE_SIZE, 8):
                            pygame.draw.rect(self.screen, WHITE, (x + i, y, 4, TILE_SIZE))

   # ------------------------------------------------------
    def draw_traffic_lights(self):
        for tl in self.traffic_lights:
            x = tl.col * TILE_SIZE
            y = tl.row * TILE_SIZE
            
            # 1. Önce "Sönük" Trafik Işığı Resmini Çiz (Direk ve Kutu)
            if "traffic_light_img" in self.images:
                 img = self.images.get("traffic_light_img")
                 # Resmi olduğu gibi karenin üzerine oturt
                 self.screen.blit(img, (x, y))
            
            # 2. Şimdi YANAN ışığı (parlak daireyi) resmin üzerine çiz
            # create_assets.py'de hesaplanan: Merkez X=20, Kırmızı Y=10, Yeşil Y=30
            # x, y karenin sol üst köşesidir. Merkezler buna göre kaydırılır.
            
            light_x = x + 20 
            
            if tl.state == "RED":
                # Kırmızı Işık (Üst - y+10)
                # Parlama efekti için önce biraz büyük şeffaf, sonra küçük parlak
                pygame.draw.circle(self.screen, (255, 0, 0), (light_x, y + 10), 5)
                # Orta noktaya beyazımsı parlaklık
                pygame.draw.circle(self.screen, (255, 100, 100), (light_x, y + 10), 2)
            else:
                # Yeşil Işık (Alt - y+30)
                pygame.draw.circle(self.screen, (0, 255, 0), (light_x, y + 30), 5)
                # Orta noktaya beyazımsı parlaklık
                pygame.draw.circle(self.screen, (100, 255, 100), (light_x, y + 30), 2)


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
            # Beyaz dış çizgi (gölge)
            pygame.draw.lines(self.screen, (255, 255, 255), False, pts, 2)
            # Sarı/Turuncu iç çizgi (rota)
            pygame.draw.lines(self.screen, (255, 215, 0), False, pts, 4)