import pygame

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color,
                 image=None, hover_image=None):
        # Temel dikdörtgen yapısı
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text if text is not None else ""
        self.base_color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.SysFont("Verdana", 24, bold=True)
        self.is_hovered = False

        # Gölge rect'i
        self.shadow_rect = pygame.Rect(x + 4, y + 4, width, height)

        # Görsel tabanlı buton için ek alanlar
        self.image = image
        self.hover_image = hover_image
        self.current_image = image

        # Eğer görsel verildiyse, rect'i görsel boyutuna göre ayarla
        if self.image is not None:
            self.rect = self.image.get_rect(topleft=(x, y))
            self.shadow_rect = self.rect.copy()
            self.shadow_rect.x += 4
            self.shadow_rect.y += 4

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if self.image is not None:
            # Görsel tabanlı buton
            if self.is_hovered and self.hover_image is not None:
                self.current_image = self.hover_image
            else:
                self.current_image = self.image
        else:
            # Eski renk tabanlı buton
            self.current_color = self.hover_color if self.is_hovered else self.base_color

    def draw(self, screen):
        # Görsel tabanlı buton
        if self.image is not None:
            # Hafif gölge
            pygame.draw.rect(screen, (20, 20, 20), self.shadow_rect, border_radius=12)
            if self.current_image:
                screen.blit(self.current_image, self.rect.topleft)
            return

        # Eski stil dikdörtgen buton
        pygame.draw.rect(screen, (20, 20, 20), self.shadow_rect, border_radius=12)
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=12)

        if self.text:
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False
