# Dosya: src/car/car_manager.py
import pygame
import os
from simulation.settings import *

class Car:
    def __init__(self, start_row, start_col):
        self.row = start_row
        self.col = start_col
        
        # GÖRSEL YÜKLEME
        asset_path = os.path.join("assets", "car.png")
        try:
            self.original_image = pygame.image.load(asset_path)
        except FileNotFoundError:
            self.original_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.original_image.fill((255, 0, 0))

        self.original_image = pygame.transform.scale(self.original_image, (TILE_SIZE, TILE_SIZE))
        self.image = self.original_image
        self.angle = 0
        
        # --- AKICI HAREKET DEĞİŞKENLERİ ---
        # Artık aracın "Piksel" cinsinden hassas bir konumu var
        self.pixel_x = start_col * TILE_SIZE
        self.pixel_y = start_row * TILE_SIZE
        
        self.path = []      
        self.path_index = 0 
        self.speed = 4  # Hız Ayarı (Piksel/Frame). Artırırsan hızlanır.

    def set_path(self, path):
        """Algoritmadan gelen rotayı yükler"""
        self.path = path
        self.path_index = 0
        # Yeni rota başladığında piksel konumunu grid konumuna eşitle (Reset)
        if path:
            self.row, self.col = path[0]
            self.pixel_x = self.col * TILE_SIZE
            self.pixel_y = self.row * TILE_SIZE

    def update(self):
        """Her karede çalışır, hedefe doğru kayarak ilerler"""
        
        # Eğer gidilecek bir yol varsa ve henüz bitmediyse
        if self.path and self.path_index < len(self.path):
            # Hedef karenin koordinatlarını al
            target_node = self.path[self.path_index]
            target_row, target_col = target_node
            
            # Hedefin piksel karşılığı
            target_x = target_col * TILE_SIZE
            target_y = target_row * TILE_SIZE
            
            # Hedefe olan uzaklığı ve yönü hesapla
            dx = target_x - self.pixel_x
            dy = target_y - self.pixel_y
            distance = (dx**2 + dy**2)**0.5
            
            # Eğer hedefe çok yaklaştıysak (Hızımızdan daha yakınsak)
            if distance < self.speed:
                # Hedefe "yapış" ve sıradaki adıma geç
                self.pixel_x = target_x
                self.pixel_y = target_y
                self.row = target_row
                self.col = target_col
                self.path_index += 1
            else:
                # Hedefe doğru "speed" kadar ilerle (Vektör matematiği)
                move_x = (dx / distance) * self.speed
                move_y = (dy / distance) * self.speed
                
                self.pixel_x += move_x
                self.pixel_y += move_y
                
                # --- DÖNÜŞ (ROTATION) ---
                # Hangi yöne gidiyorsak ona göre dönelim
                # dx pozitifse SAĞA gidiyoruz, negatifse SOLA
                if abs(dx) > abs(dy): # Yatay hareket baskınsa
                    self.angle = -90 if dx > 0 else 90
                else: # Dikey hareket baskınsa
                    self.angle = 180 if dy > 0 else 0

                self.image = pygame.transform.rotate(self.original_image, self.angle)

    def draw(self, screen):
        # Artık self.col * TILE_SIZE yerine hassas pixel_x kullanıyoruz
        rect = self.image.get_rect(center=(self.pixel_x + TILE_SIZE//2, self.pixel_y + TILE_SIZE//2))
        screen.blit(self.image, rect)