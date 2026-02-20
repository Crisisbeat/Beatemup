import pygame
import os

def create_placeholder(filename, text, color):
    pygame.init()
    width, height = 1280, 720
    surface = pygame.Surface((width, height))
    surface.fill(color)
    
    font = pygame.font.SysFont("Arial", 60, bold=True)
    text_surf = font.render(text, True, (255, 255, 255))
    rect = text_surf.get_rect(center=(width//2, height//2))
    
    # Draw some random rectangles to make it look like a "scene"
    import random
    for _ in range(10):
        w, h = random.randint(100, 300), random.randint(100, 300)
        x, y = random.randint(0, width-w), random.randint(0, height-h)
        c = [max(0, min(255, v + random.randint(-50, 50))) for v in color]
        pygame.draw.rect(surface, c, (x, y, w, h))
    
    surface.blit(text_surf, rect)
    
    # Save in slides folder
    if not os.path.exists("slides"):
        os.makedirs("slides")
    
    pygame.image.save(surface, os.path.join("slides", filename))
    print(f"Generated {filename}")

if __name__ == "__main__":
    create_placeholder("slide1.png", "A CITY UNDER THE SHADOW OF CRIME", (30, 30, 50))
    create_placeholder("slide2.png", "THE PUNKS ARE REIGNING THE STREETS", (50, 30, 30))
    create_placeholder("slide3.png", "BUT ONE MAN WILL STAND AGAINST THEM", (30, 50, 30))
    create_placeholder("slide4.png", "EL CHAPULIN ARRIVES...", (100, 100, 20))
    pygame.quit()
