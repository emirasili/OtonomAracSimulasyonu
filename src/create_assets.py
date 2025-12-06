# Dosya: src/create_assets.py
import pygame
import os

TILE_SIZE = 40
ASSET_DIR = "assets"
ROAD_COLOR = (50, 50, 50)
LINE_COLOR = (255, 255, 255)
LINE_WIDTH = 3 

if not os.path.exists(ASSET_DIR):
    os.makedirs(ASSET_DIR)

pygame.init()
screen = pygame.display.set_mode((100, 100)) 

def save_surface(surface, name):
    pygame.image.save(surface, os.path.join(ASSET_DIR, name))
    print(f"{name} oluşturuldu.")

def create_base_surface():
    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Arka planı tamamen boyama, sadece yolu boya (Opsiyonel, şimdilik kare yapıyoruz)
    s.fill(ROAD_COLOR) 
    return s

def draw_arm(surface, direction):
    """
    Merkezden belirtilen yöne doğru kesikli çizgi çizer.
    Bu sayede tüm parçalar merkezde kusursuz birleşir.
    """
    mid = TILE_SIZE // 2
    center = (mid, mid)
    
    # Çizgi Ayarları (Merkezden uca 20px mesafe var)
    # Desen: 8px Dolu + 4px Boş + 8px Dolu
    
    if direction == "UP":
        # Merkezden Yukarı: (mid, mid) -> (mid, 0)
        pygame.draw.line(surface, LINE_COLOR, (mid, mid), (mid, mid - 8), LINE_WIDTH) # İlk parça
        pygame.draw.line(surface, LINE_COLOR, (mid, mid - 14), (mid, 0), LINE_WIDTH)  # İkinci parça
        
    elif direction == "DOWN":
        # Merkezden Aşağı: (mid, mid) -> (mid, 40)
        pygame.draw.line(surface, LINE_COLOR, (mid, mid), (mid, mid + 8), LINE_WIDTH) 
        pygame.draw.line(surface, LINE_COLOR, (mid, mid + 14), (mid, TILE_SIZE), LINE_WIDTH)

    elif direction == "LEFT":
        # Merkezden Sola: (mid, mid) -> (0, mid)
        pygame.draw.line(surface, LINE_COLOR, (mid, mid), (mid - 8, mid), LINE_WIDTH)
        pygame.draw.line(surface, LINE_COLOR, (mid - 14, mid), (0, mid), LINE_WIDTH)

    elif direction == "RIGHT":
        # Merkezden Sağa: (mid, mid) -> (40, mid)
        pygame.draw.line(surface, LINE_COLOR, (mid, mid), (mid + 8, mid), LINE_WIDTH)
        pygame.draw.line(surface, LINE_COLOR, (mid + 14, mid), (TILE_SIZE, mid), LINE_WIDTH)

# --- YENİ PARÇALARIN OLUŞTURULMASI ---

# 1. Düz Yollar
s = create_base_surface(); draw_arm(s, "UP"); draw_arm(s, "DOWN"); save_surface(s, "road_v.png")
s = create_base_surface(); draw_arm(s, "LEFT"); draw_arm(s, "RIGHT"); save_surface(s, "road_h.png")

# 2. Köşeler
s = create_base_surface(); draw_arm(s, "UP"); draw_arm(s, "RIGHT"); save_surface(s, "road_ur.png") # Up-Right
s = create_base_surface(); draw_arm(s, "RIGHT"); draw_arm(s, "DOWN"); save_surface(s, "road_rd.png") # Right-Down
s = create_base_surface(); draw_arm(s, "DOWN"); draw_arm(s, "LEFT"); save_surface(s, "road_dl.png") # Down-Left
s = create_base_surface(); draw_arm(s, "LEFT"); draw_arm(s, "UP"); save_surface(s, "road_lu.png") # Left-Up

# 3. T-Kavşaklar (3 Kollu)
s = create_base_surface(); draw_arm(s, "LEFT"); draw_arm(s, "RIGHT"); draw_arm(s, "DOWN"); save_surface(s, "road_t_down.png")
s = create_base_surface(); draw_arm(s, "LEFT"); draw_arm(s, "RIGHT"); draw_arm(s, "UP"); save_surface(s, "road_t_up.png")
s = create_base_surface(); draw_arm(s, "UP"); draw_arm(s, "DOWN"); draw_arm(s, "LEFT"); save_surface(s, "road_t_left.png")
s = create_base_surface(); draw_arm(s, "UP"); draw_arm(s, "DOWN"); draw_arm(s, "RIGHT"); save_surface(s, "road_t_right.png")

# 4. Dört Yol (4 Kollu)
s = create_base_surface()
draw_arm(s, "UP"); draw_arm(s, "DOWN"); draw_arm(s, "LEFT"); draw_arm(s, "RIGHT")
save_surface(s, "road_cross.png")

# --- DİĞER STANDART ASSETLER ---
# Duvar
s = pygame.Surface((TILE_SIZE, TILE_SIZE))
s.fill((139, 69, 19)) 
pygame.draw.rect(s, (100, 50, 10), (0, 0, TILE_SIZE, TILE_SIZE), 2)
pygame.draw.line(s, (100, 50, 10), (0, 10), (40, 10), 2)
pygame.draw.line(s, (100, 50, 10), (0, 20), (40, 20), 2)
save_surface(s, "wall.png")

# Su
s = pygame.Surface((TILE_SIZE, TILE_SIZE))
s.fill((0, 150, 255))
pygame.draw.arc(s, (200, 200, 255), (5, 5, 30, 20), 0, 3.14, 2)
save_surface(s, "water.png")

# Araba
s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
pygame.draw.rect(s, (200, 0, 0), (5, 2, 30, 36), border_radius=5) 
pygame.draw.rect(s, (50, 50, 50), (8, 8, 24, 6))
pygame.draw.rect(s, (50, 50, 50), (8, 24, 24, 4))
pygame.draw.circle(s, (255, 255, 0), (8, 4), 2)
pygame.draw.circle(s, (255, 255, 0), (32, 4), 2)
save_surface(s, "car.png")

# Start/Hedef
s = pygame.Surface((TILE_SIZE, TILE_SIZE)); s.fill((255, 215, 0)); font = pygame.font.SysFont("Arial", 30, bold=True); s.blit(font.render("S", True, (0,0,0)), (10, 5)); save_surface(s, "start.png")
s = pygame.Surface((TILE_SIZE, TILE_SIZE)); s.fill((255, 0, 0)); pygame.draw.rect(s, (255, 255, 255), (0, 0, 20, 20)); pygame.draw.rect(s, (255, 255, 255), (20, 20, 20, 20)); save_surface(s, "target.png")

pygame.quit()