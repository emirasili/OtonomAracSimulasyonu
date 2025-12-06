# Dosya: src/ui/menu.py
import pygame

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.SysFont("Verdana", 24, bold=True) # Daha modern font
        self.is_hovered = False
        
        # Gölge için rect (Hafif derinlik hissi)
        self.shadow_rect = pygame.Rect(x + 4, y + 4, width, height)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.is_hovered else self.base_color

    def draw(self, screen):
        # 1. Gölgeyi çiz (Siyah, yarı saydam olması için ayrı surface gerekirdi ama basitlik için gri)
        pygame.draw.rect(screen, (20, 20, 20), self.shadow_rect, border_radius=12)

        # 2. Butonun kendisini çiz
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=12)
        
        # 3. Kenar Çizgisi (Border) - Beyaz
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=12)
        
        # 4. Metni Yaz
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False