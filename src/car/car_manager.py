# Dosya: src/car/car_manager.py
import pygame
import os
from simulation.settings import *


class Car:
    def __init__(self, start_row, start_col):
        # Arabanın grid üzerindeki satır/sütun konumu
        self.row = start_row
        self.col = start_col

        # Araç görselini yükle
        asset_path = os.path.join("assets", "car.png")
        try:
            self.original_image = pygame.image.load(asset_path)
        except FileNotFoundError:
            self.original_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.original_image.fill((255, 0, 0))

        # Boyutlandır
        self.original_image = pygame.transform.scale(
            self.original_image, (TILE_SIZE, TILE_SIZE)
        )
        self.image = self.original_image
        self.angle = 0

        # Piksel konumu
        self.pixel_x = start_col * TILE_SIZE
        self.pixel_y = start_row * TILE_SIZE

        # Yol takip değişkenleri
        self.path = []
        self.path_index = 0
        self.base_speed = 4
        self.transition_speed = 2.5
        self.crosswalk_speed = 1
        self.crosswalk_cooldown_max = 30  # ~0.5 sn
        self.crosswalk_cooldown = 0
        self.speed = self.base_speed
        self.is_waiting_red = False
        



    # ---------------------------------------------------------
    # 🔍 DİNAMİK ENGEL ALGILAMA
    # ---------------------------------------------------------
    def detect_dynamic_obstacle(self, dynamic_obstacles):
        """
        Bir sonraki karede dinamik engel var mı kontrol eder.
        True → Engel var, rota değiştirilmelidir.
        """
        if self.path_index >= len(self.path):
            return False

        next_r, next_c = self.path[self.path_index]
        return (next_r, next_c) in dynamic_obstacles

    # ---------------------------------------------------------
    def set_path(self, path):
        """Algoritmadan gelen yeni rotayı yükler."""
        self.path = path
        self.path_index = 0

        if path:
            self.row, self.col = path[0]
            self.pixel_x = self.col * TILE_SIZE
            self.pixel_y = self.row * TILE_SIZE
    # ---------------------------------------------------------
    
    # ---------------------------------------------------------
    def update(self, game_map=None, traffic_lights=None, dynamic_obstacles=None):
        """
        Her karede çağrılan ana hareket fonksiyonu.
        - Önce bulunduğum karede kırmızı ışık var mı kontrol ediyorum.
        - İkinci adımda, sıradaki karede dinamik engel var mı diye bakıyorum.
        - Engel yoksa path üzerindeki hedef kareye doğru akıcı şekilde ilerliyorum.

        True dönerse: Dinamik engel tespit edildi, dışarıda yeniden rota planlanmalı.
        False dönerse: Normal ilerledi veya ışıkta bekledi, yeniden planlamaya gerek yok.
        """
        if traffic_lights is None:
            traffic_lights = []

        if dynamic_obstacles is None:
            dynamic_obstacles = []

        # Arabanın şu an bulunduğu grid karesini hesaplıyorum.
        current_row = int(self.pixel_y // TILE_SIZE)
        current_col = int(self.pixel_x // TILE_SIZE)

        # Bulunduğum karede kırmızı ışık varsa, bu frame'de hiç hareket etmiyorum.
        self.is_waiting_red = False  # her frame başında reset

        for tl in traffic_lights:
            if tl.row == current_row and tl.col == current_col and tl.state == "RED":
                self.is_waiting_red = True
                self.current_speed = 0.0
                return False

        # Takip edilecek bir yol yoksa ya da sona geldiysem hareket etmiyorum.
        if not self.path or self.path_index >= len(self.path):
            self.is_waiting_red = False
            self.current_speed = 0.0
            return False

        # --- Dinamik engel kontrolü ---
        # Sıradaki karede engel varsa bu frame'de ilerlemiyorum
        # ve dışarıya "yeniden rota planla" sinyali olarak True döndürüyorum.
        if self.detect_dynamic_obstacle(dynamic_obstacles):
            return True

        # Sıradaki hedef kare
        target_row, target_col = self.path[self.path_index]

        # Hedef karenin piksel koordinatları
        target_x = target_col * TILE_SIZE
        target_y = target_row * TILE_SIZE
        
        # --- HIZ KONTROLÜ (HAREKETTEN ÖNCE) ---
        if game_map is not None:
            current_tile = game_map[current_row][current_col]
            target_tile  = game_map[target_row][target_col]

            self.speed = self.base_speed

            if target_tile in [5, 6]:
                self.speed = self.transition_speed

            on_crosswalk = (current_tile == 7) or (target_tile == 7)
            if on_crosswalk:
                self.crosswalk_cooldown = self.crosswalk_cooldown_max
                self.speed = self.crosswalk_speed
            else:
                if self.crosswalk_cooldown > 0:
                    self.crosswalk_cooldown -= 1
                    self.speed = self.crosswalk_speed

        # panel için anlık hız (kırmızıda zaten 0 dönmüştük)
        self.current_speed = float(self.speed)

        # Hedefe olan mesafe ve yönü hesaplıyorum.
        dx = target_x - self.pixel_x
        dy = target_y - self.pixel_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < self.speed:
            # Hedef kareye yeterince yaklaştıysam direkt olarak oraya "yapışıyorum".
            self.pixel_x = target_x
            self.pixel_y = target_y
            self.row = target_row
            self.col = target_col
            self.path_index += 1
        else:
            # Hedefe doğru normalleştirilmiş bir vektörle ilerliyorum.
            move_x = (dx / distance) * self.speed
            move_y = (dy / distance) * self.speed

            self.pixel_x += move_x
            self.pixel_y += move_y

            # Hareket yönüne göre arabayı döndürüyorum.
            if abs(dx) > abs(dy):  # Yatay hareket baskın
                self.angle = -90 if dx > 0 else 90
            else:  # Dikey hareket baskın
                self.angle = 180 if dy > 0 else 0

            self.image = pygame.transform.rotate(
                self.original_image, self.angle)

        return False


    # ---------------------------------------------------------
    def draw(self, screen):
        """Aracı ekran üzerine çizer."""
        rect = self.image.get_rect(
            center=(
                self.pixel_x + TILE_SIZE // 2,
                self.pixel_y + TILE_SIZE // 2,
            )
        )
        screen.blit(self.image, rect)  # bu fonksiyon ekrana çizmeyi yapar
 