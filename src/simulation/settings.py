# Dosya: src/simulation/settings.py

# --- RENKLER (RGB Formatı) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)         # Arka plan
GRAY = (50, 50, 50)       # 0: Yol (Sürülebilir alan)
GREEN = (34, 139, 34)     # 1: Duvar / Bina (Geçilemez)
BLUE = (0, 191, 255)      # 2: Su / Göl (Geçilemez - Görsel farkı var)
YELLOW = (255, 215, 0)    # 3: Başlangıç Noktası
RED = (220, 20, 60)       # 4: Hedef Noktası
ORANGE = (255, 165, 0)    # 5: Kavşak / Meydan (Yol gibi davranır)

# Grid çizgilerini biraz daha koyu yapalım ki göz yormasın
GRID_COLOR = (40, 40, 40) 

# --- EKRAN AYARLARI ---
# Haritamız 20x20 olduğu için TILE_SIZE 40 olursa ekran 800x800 olur.
# Bu boyut hem nettir hem de çoğu ekrana sığar.
TILE_SIZE = 40
FPS = 60