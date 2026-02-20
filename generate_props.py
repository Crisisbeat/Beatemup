import pygame
import os
from constants import *

def generate_prop_placeholders():
    folder = "textures/sprites/props"
    if not os.path.exists(folder): os.makedirs(folder)
    
    props = {
        "lamp_post": {"size": (80, 280), "color": (100, 100, 110)},
        "hydrant": {"size": (40, 60), "color": (200, 50, 50)},
        "trash_can": {"size": (50, 70), "color": (80, 85, 90)}
    }
    
    for name, data in props.items():
        w, h = data["size"]
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = data["color"]
        
        # Dibujar forma básica
        if name == "lamp_post":
            pygame.draw.rect(surf, color, (w//2 - 5, 40, 10, h - 40)) # Poste
            pygame.draw.circle(surf, (255, 255, 200), (w//2, 30), 20) # Luz
        elif name == "hydrant":
            pygame.draw.rect(surf, color, (5, 10, w - 10, h - 10), border_radius=5)
            pygame.draw.circle(surf, color, (w//2, 10), 15)
        elif name == "trash_can":
            pygame.draw.rect(surf, color, (5, 10, w - 10, h - 10))
            pygame.draw.rect(surf, (60, 60, 60), (0, 0, w, 15)) # Tapa
            
        pygame.draw.rect(surf, (0,0,0), (0,0,w,h), 2) # Borde
        
        path = os.path.join(folder, f"{name}.png")
        pygame.image.save(surf, path)
        print(f"Prop generado: {path}")

if __name__ == "__main__":
    pygame.init()
    generate_prop_placeholders()
