# Dosya: src/simulation/simulation_manager.py
import pygame
import sys
import os
from simulation.settings import *
from map.map_data import GAME_MAP
from ui.menu import Button
from car.car_manager import Car
from algorithms.pathfinding import PathFinder

class Game:
    def __init__(self):
        """
        Oyunun başlatıldığı ve temel ayarların yapıldığı kurucu fonksiyon.
        Ekranı, haritayı, görselleri ve menü elemanlarını hazırlar.
        """
        pygame.init()
        
        # Harita boyutlarını hesapla (Satır x Sütun)
        self.rows = len(GAME_MAP)
        self.cols = len(GAME_MAP[0])
        
        # Pencere boyutunu harita boyutuna göre ayarla (Piksel cinsinden)
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # --- PENCERE AYARLARI ---
        pygame.display.set_caption("SAÜTONOM - Akıllı Araç Simülasyonu") 
        self.clock = pygame.time.Clock() # FPS kontrolü için saat nesnesi

        # --- GÖRSELLERİN YÜKLENMESİ (ASSETS) ---
        # Harita elemanları için resim dosyalarını (PNG) yükleyip sözlüğe atıyoruz.
        self.images = {}
        assets = {
            # Yol Parçaları (v: dikey, h: yatay, ur: yukarı-sağ köşe vb.)
            "v": "road_v.png", "h": "road_h.png",
            "ur": "road_ur.png", "rd": "road_rd.png",
            "dl": "road_dl.png", "lu": "road_lu.png",
            "t_up": "road_t_up.png", "t_down": "road_t_down.png",
            "t_left": "road_t_left.png", "t_right": "road_t_right.png",
            "cross": "road_cross.png",
            # Diğer Elemanlar (1: Duvar, 2: Su, 3: Start, 4: Hedef)
            1: "wall.png", 2: "water.png",
            3: "start.png", 4: "target.png"
        }
        
        for key, filename in assets.items():
            path = os.path.join("assets", filename)
            if os.path.exists(path):
                img = pygame.image.load(path)
                # Resimleri kare boyutuna (TILE_SIZE) ölçekle
                self.images[key] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

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
        self.pathfinder = PathFinder(GAME_MAP) # Yol bulma motorunu başlat
        
        # --- BUTONLARIN OLUŞTURULMASI ---
        # Ekranın ortasını hesapla
        cx = self.width // 2 - 100
        cy = self.height // 2 + 70 
        
        # Algoritma Seçim Butonları
        self.btn_bfs = Button(cx, cy, 200, 50, "BFS", (0, 100, 200), (0, 150, 255))
        self.btn_dfs = Button(cx, cy + 60, 200, 50, "DFS", (0, 150, 100), (0, 200, 150))
        self.btn_astar = Button(cx, cy + 120, 200, 50, "A*", (200, 50, 50), (255, 80, 80))

        # Oyun içi "GERİ DÖN" Butonu (Sağ Alt Köşe)
        self.btn_back = Button(self.width - 120, self.height - 60, 100, 40, "GERİ", (200, 50, 50), (255, 80, 80))

    def find_pos(self, value):
        """
        Harita matrisinde belirli bir değerin (örn: 3=Start) konumunu bulur.
        Return: (satır, sütun) veya None
        """
        for r, row in enumerate(GAME_MAP):
            for c, val in enumerate(row):
                if val == value: return (r, c)
        return None

    def start_simulation(self, algo_name):
        """
        Bir algoritma butonuna basıldığında çalışır.
        Arabayı oluşturur, algoritmayı çalıştırır ve rotayı hesaplar.
        """
        self.selected_algorithm = algo_name
        self.state = "GAME" # Oyun ekranına geç
        print(f"{algo_name} Hesaplanıyor...")

        # Başlangıç ve Hedef noktalarını bul
        start = self.find_pos(3)
        goal = self.find_pos(4)
        if not start or not goal: return # Hata kontrolü

        # Arabayı oluştur veya varsa konumunu sıfırla
        if self.car is None: 
            self.car = Car(start[0], start[1])
        else:
             self.car.row, self.car.col = start[0], start[1]
             self.car.image = self.car.original_image
             # Akıcı hareket için piksel konumunu da sıfırla
             if hasattr(self.car, 'pixel_x'):
                 self.car.pixel_x = start[1] * TILE_SIZE
                 self.car.pixel_y = start[0] * TILE_SIZE

        # --- ALGORİTMA ÇALIŞTIRMA ---
        path = []
        if algo_name == "BFS": path = self.pathfinder.bfs(start, goal)
        elif algo_name == "DFS": path = self.pathfinder.dfs(start, goal)
        elif algo_name == "A*": path = self.pathfinder.a_star(start, goal)

        # Bulunan yolu arabaya yükle
        if path: self.car.set_path(path)
        else: print("Yol Bulunamadı!")

    def run(self):
        """
        Oyunun Ana Döngüsü (Game Loop).
        Sürekli çalışarak ekranı günceller ve olayları dinler.
        """
        while True:
            mouse_pos = pygame.mouse.get_pos() # Fare konumunu al
            events = pygame.event.get()        # Klavye/Fare olaylarını al

            for event in events:
                # Çarpıya basılırsa kapat
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Menüdeysek buton tıklamalarını kontrol et
                if self.state == "MENU":
                    if self.btn_bfs.is_clicked(event): self.start_simulation("BFS")
                    elif self.btn_dfs.is_clicked(event): self.start_simulation("DFS")
                    elif self.btn_astar.is_clicked(event): self.start_simulation("A*")
                
                # Oyundaysak "Geri Dön" butonunu kontrol et
                elif self.state == "GAME":
                    if self.btn_back.is_clicked(event):
                        self.state = "MENU"

            # Arka planı temizle (Siyah)
            self.screen.fill(BLACK)

            # Duruma göre ekranı çiz
            if self.state == "MENU":
                self.draw_menu(mouse_pos)
            elif self.state == "GAME":
                self.draw_game(mouse_pos)

            # Ekranı yenile ve FPS'i sabitle
            pygame.display.flip()
            self.clock.tick(FPS)

    def draw_menu(self, mouse_pos):
        """Menü ekranını çizer (Arkaplan, Başlık, Butonlar)"""
        self.screen.fill((25, 30, 40)) # Koyu Gri/Lacivert Arkaplan
        
        # Başlık ve Gölgesi
        shadow = self.title_font.render("SAÜTONOM", True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(self.width // 2 + 3, 73))
        self.screen.blit(shadow, shadow_rect)

        title_surf = self.title_font.render("SAÜTONOM", True, (255, 215, 0)) # Altın Sarısı
        title_rect = title_surf.get_rect(center=(self.width // 2, 70))
        self.screen.blit(title_surf, title_rect)
        
        # Alt Başlık
        sub_surf = self.subtitle_font.render("Otonom Araç Simülasyonu", True, (200, 200, 200))
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(self.width // 2, 115)))

        # Logo
        if self.menu_car_img:
            self.screen.blit(self.menu_car_img, self.menu_car_img.get_rect(center=(self.width // 2, 230)))

        # Butonları Çiz (Fare üzerine gelince renk değişimi için check_hover)
        self.btn_bfs.check_hover(mouse_pos)
        self.btn_dfs.check_hover(mouse_pos)
        self.btn_astar.check_hover(mouse_pos)
        self.btn_bfs.draw(self.screen)
        self.btn_dfs.draw(self.screen)
        self.btn_astar.draw(self.screen)

        # Alt Bilgi (Footer)
        footer_surf = self.subtitle_font.render("Sakarya Üniversitesi - 2025", True, (100, 100, 100))
        self.screen.blit(footer_surf, footer_surf.get_rect(center=(self.width // 2, self.height - 30)))

    def draw_game(self, mouse_pos):
        """Oyun ekranını çizer (Harita, Araba, Bilgi Paneli)"""
        self.draw_map()
        
        # Arabayı çiz
        if self.car:
            self.car.update() # Arabanın yeni konumunu hesapla
            self.car.draw(self.screen)
        
        # --- BİLGİ PANELİ (Sol Üst) ---
        info_surf = pygame.Surface((220, 45))
        info_surf.set_alpha(220) # Yarı saydamlık
        info_surf.fill((20, 20, 20))
        self.screen.blit(info_surf, (10, 10))
        pygame.draw.rect(self.screen, WHITE, (10, 10, 220, 45), 2) # Çerçeve
        
        # Hangi algoritmanın çalıştığını yaz
        text = self.ui_font.render(f"Algoritma: {self.selected_algorithm}", True, ORANGE)
        self.screen.blit(text, (25, 22))

        # "Geri Dön" Butonunu Çiz
        self.btn_back.check_hover(mouse_pos)
        self.btn_back.draw(self.screen)

    def is_road(self, r, c):
        """Verilen koordinatın yol olup olmadığını kontrol eder."""
        if 0 <= r < self.rows and 0 <= c < self.cols:
            # 0: Yol, 3: Start, 4: Hedef, 5: Kavşak -> Hepsi yol sayılır
            return GAME_MAP[r][c] in [0, 3, 4, 5]
        return False

    def draw_map(self):
        """
        Haritayı ekrana çizer.
        Bitmasking yöntemi kullanarak yolların doğru şekilde birleşmesini sağlar.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                cell = GAME_MAP[r][c]
                img = None
                
                # --- AKILLI YOL ÇİZİMİ (Auto-Tiling) ---
                if cell == 0 or cell == 5:
                    mask = 0
                    # Komşuları kontrol et: Yukarı(1), Sağ(2), Aşağı(4), Sol(8)
                    if self.is_road(r-1, c): mask += 1 
                    if self.is_road(r, c+1): mask += 2 
                    if self.is_road(r+1, c): mask += 4 
                    if self.is_road(r, c-1): mask += 8 
                    
                    # Maske değerine göre doğru resmi seç
                    # Örn: mask=3 (Yukarı+Sağ) -> Sağ-Üst Köşe (ur)
                    if mask in [5, 1, 4]: img = self.images.get("v")   # Dikey
                    elif mask in [10, 2, 8]: img = self.images.get("h") # Yatay
                    elif mask == 3: img = self.images.get("ur")  # Sağ-Üst
                    elif mask == 6: img = self.images.get("rd")  # Sağ-Alt
                    elif mask == 12: img = self.images.get("dl") # Sol-Alt
                    elif mask == 9: img = self.images.get("lu")  # Sol-Üst
                    elif mask == 14: img = self.images.get("t_down") # T Aşağı
                    elif mask == 11: img = self.images.get("t_up")   # T Yukarı
                    elif mask == 7: img = self.images.get("t_right") # T Sağ
                    elif mask == 13: img = self.images.get("t_left") # T Sol
                    elif mask == 15: img = self.images.get("cross")  # Dört Yol
                    else: img = self.images.get("h") # Varsayılan
                else:
                    # Yol değilse normal resmini al (Duvar, Su vb.)
                    img = self.images.get(cell)

                # Resmi ekrana bas
                if img:
                    self.screen.blit(img, (c*TILE_SIZE, r*TILE_SIZE))