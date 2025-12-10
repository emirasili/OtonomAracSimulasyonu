# Dosya: src/create_assets.py
import pygame
import os

TILE_SIZE = 40
ASSET_DIR = "assets"

# --- KAMPÜS/SAÜ TEMASI RENKLERİ ---
ROAD_COLOR = (50, 50, 50)       # Koyu Asfalt
LINE_COLOR = (255, 255, 255)    # Beyaz Şeritler
BUILDING_COLOR = (160, 82, 45)  # Sienna (Daha doğal bir tuğla rengi)
WATER_COLOR = (0, 119, 190)     # Ocean Blue
WATER_RIPPLE = (0, 150, 220)    # Su dalgası
CAR_COLOR = (220, 20, 60)       # Crimson Red (Spor Kırmızı)
LINE_WIDTH = 3 

if not os.path.exists(ASSET_DIR):
    os.makedirs(ASSET_DIR)

pygame.init()
# Ekranı gizli modda açalım
screen = pygame.display.set_mode((100, 100)) 

def save_surface(surface, name):
    pygame.image.save(surface, os.path.join(ASSET_DIR, name))
    print(f"{name} oluşturuldu.")

def create_base_surface():
    s = pygame.Surface((TILE_SIZE, TILE_SIZE))
    s.fill(ROAD_COLOR) 
    return s

def draw_arm(surface, direction):
    mid = TILE_SIZE // 2
    if direction == "UP":
        pygame.draw.line(surface, LINE_COLOR, (mid, mid), (mid, mid - 8), LINE_WIDTH)
        pygame.draw.line(surface, LINE_COLOR, (mid, mid - 14), (mid, 0), LINE_WIDTH)
    elif direction == "DOWN":
        pygame.draw.line(surface, LINE_COLOR, (mid, mid), (mid, mid + 8), LINE_WIDTH) 
        pygame.draw.line(surface, LINE_COLOR, (mid, mid + 14), (mid, TILE_SIZE), LINE_WIDTH)
    elif direction == "LEFT":
        pygame.draw.line(surface, LINE_COLOR, (mid, mid), (mid - 8, mid), LINE_WIDTH)
        pygame.draw.line(surface, LINE_COLOR, (mid - 14, mid), (0, mid), LINE_WIDTH)
    elif direction == "RIGHT":
        pygame.draw.line(surface, LINE_COLOR, (mid, mid), (mid + 8, mid), LINE_WIDTH)
        pygame.draw.line(surface, LINE_COLOR, (mid + 14, mid), (TILE_SIZE, mid), LINE_WIDTH)

# --- YOL PARÇALARI ---
s = create_base_surface(); draw_arm(s, "UP"); draw_arm(s, "DOWN"); save_surface(s, "road_v.png")
s = create_base_surface(); draw_arm(s, "LEFT"); draw_arm(s, "RIGHT"); save_surface(s, "road_h.png")
s = create_base_surface(); draw_arm(s, "UP"); draw_arm(s, "RIGHT"); save_surface(s, "road_ur.png")
s = create_base_surface(); draw_arm(s, "RIGHT"); draw_arm(s, "DOWN"); save_surface(s, "road_rd.png")
s = create_base_surface(); draw_arm(s, "DOWN"); draw_arm(s, "LEFT"); save_surface(s, "road_dl.png")
s = create_base_surface(); draw_arm(s, "LEFT"); draw_arm(s, "UP"); save_surface(s, "road_lu.png")
s = create_base_surface(); draw_arm(s, "LEFT"); draw_arm(s, "RIGHT"); draw_arm(s, "DOWN"); save_surface(s, "road_t_down.png")
s = create_base_surface(); draw_arm(s, "LEFT"); draw_arm(s, "RIGHT"); draw_arm(s, "UP"); save_surface(s, "road_t_up.png")
s = create_base_surface(); draw_arm(s, "UP"); draw_arm(s, "DOWN"); draw_arm(s, "LEFT"); save_surface(s, "road_t_left.png")
s = create_base_surface(); draw_arm(s, "UP"); draw_arm(s, "DOWN"); draw_arm(s, "RIGHT"); save_surface(s, "road_t_right.png")
s = create_base_surface(); draw_arm(s, "UP"); draw_arm(s, "DOWN"); draw_arm(s, "LEFT"); draw_arm(s, "RIGHT"); save_surface(s, "road_cross.png")

# --- BİNA (DAHA DETAYLI) ---
s = pygame.Surface((TILE_SIZE, TILE_SIZE))
s.fill(BUILDING_COLOR) 
# Çatı efekti (Hafif iç kare)
pygame.draw.rect(s, (160+20, 82+20, 45+20), (5, 5, 30, 30))
# Ortada havalandırma kutusu
pygame.draw.rect(s, (100, 50, 30), (15, 15, 10, 10))
save_surface(s, "wall.png")

# --- SU (DALGALI EFEKT) ---
s = pygame.Surface((TILE_SIZE, TILE_SIZE))
s.fill(WATER_COLOR)
# Küçük dalgalar çiz
for y in range(5, 40, 10):
    for x in range(0, 40, 15):
        offset = 5 if (y // 10) % 2 == 0 else 0
        pygame.draw.line(s, WATER_RIPPLE, (x + offset, y), (x + offset + 8, y), 2)
save_surface(s, "water.png")

# --- YAYA GEÇİDİ ZEMİNİ ---
s = pygame.Surface((TILE_SIZE, TILE_SIZE))
s.fill(ROAD_COLOR)
save_surface(s, "crosswalk.png")

# --- TRAFİK IŞIĞI (HİZALI VE DÜZGÜN) ---
s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
s.fill((0,0,0,0)) # Şeffaf

# 1. Ana Kasa (Siyah Dikdörtgen) - Tam ortada
box_w, box_h = 16, 36
box_x = (TILE_SIZE - box_w) // 2  # (40-16)/2 = 12
box_y = (TILE_SIZE - box_h) // 2  # (40-36)/2 = 2
pygame.draw.rect(s, (20, 20, 20), (box_x, box_y, box_w, box_h), border_radius=4)
# Çerçeve
pygame.draw.rect(s, (50, 50, 50), (box_x, box_y, box_w, box_h), 1, border_radius=4)

# 2. Sönük Işık Yuvaları (Koyu Gri)
# Koordinatlar: Merkez X = 20
# Y Konumları: Kırmızı=10, Sarı=20, Yeşil=30
center_x = TILE_SIZE // 2
pygame.draw.circle(s, (50, 0, 0), (center_x, 10), 5)  # Kırmızı Yeri
pygame.draw.circle(s, (50, 50, 0), (center_x, 20), 5) # Sarı Yeri
pygame.draw.circle(s, (0, 50, 0), (center_x, 30), 5)  # Yeşil Yeri

save_surface(s, "traffic_light.png")

# --- DİNAMİK ENGEL: ÇUKUR (Pothole) ---
s = pygame.Surface((TILE_SIZE, TILE_SIZE))
s.fill(ROAD_COLOR) # Yol rengi zemin
# Çukurun dışı (Açık gri)
pygame.draw.ellipse(s, (70, 70, 70), (5, 10, 30, 20))
# Çukurun içi (Siyah/Koyu)
pygame.draw.ellipse(s, (20, 20, 20), (8, 12, 24, 16))
# Uyarı Dubası (Turuncu Konik - Üstten görünüm)
pygame.draw.circle(s, (255, 140, 0), (30, 30), 6)
pygame.draw.circle(s, (255, 255, 255), (30, 30), 3)
save_surface(s, "obstacle.png")

# --- ARABA (DETAYLI) ---
s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
# Gölge
pygame.draw.rect(s, (30, 30, 30), (12, 6, 20, 32), border_radius=5) 
# Gövde
pygame.draw.rect(s, CAR_COLOR, (10, 4, 20, 32), border_radius=5) 
# Ön Cam
pygame.draw.rect(s, (50, 50, 70), (11, 10, 18, 5))
# Arka Cam
pygame.draw.rect(s, (50, 50, 70), (11, 28, 18, 4))
# Tavan
pygame.draw.rect(s, (200, 0, 0), (11, 16, 18, 11))
# Farlar (Sarı)
pygame.draw.rect(s, (255, 255, 200), (10, 2, 5, 3))
pygame.draw.rect(s, (255, 255, 200), (25, 2, 5, 3))
save_surface(s, "car.png")

# Start/Hedef
s = pygame.Surface((TILE_SIZE, TILE_SIZE)); s.fill((255, 215, 0)); font = pygame.font.SysFont("Arial", 24, bold=True); s.blit(font.render("S", True, (0,0,0)), (12, 8)); save_surface(s, "start.png")
s = pygame.Surface((TILE_SIZE, TILE_SIZE)); s.fill((220, 20, 60)); pygame.draw.circle(s, (255,255,255), (TILE_SIZE//2, TILE_SIZE//2), 10); save_surface(s, "target.png")

pygame.quit()
print("Görseller başarıyla güncellendi!")