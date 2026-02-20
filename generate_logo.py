import pygame
import os

pygame.init()

def create_logo():
    path = r"c:\Users\user\Desktop\Melon\New folder\Beatemup\textures\ui\placeholder_logo.png"
    surf = pygame.Surface((400, 200), pygame.SRCALPHA)
    
    # Simple red rectangle with some style
    pygame.draw.rect(surf, (150, 0, 0), (0, 0, 400, 200), border_radius=10)
    pygame.draw.rect(surf, (200, 50, 50), (10, 10, 380, 180), width=5, border_radius=10)
    
    font = pygame.font.SysFont("Impact", 40)
    txt = font.render("LOGOTIPO DEL JUEGO", True, (255, 255, 255))
    rect = txt.get_rect(center=(200, 100))
    surf.blit(txt, rect)
    
    pygame.image.save(surf, path)
    print(f"Logo created at {path}")

if __name__ == "__main__":
    create_logo()
