import pygame
import os
import random
from constants import *

def generate_all_placeholders():
    bg_folder = "textures/background"
    sp_folder = "textures/sprites"
    for folder in [bg_folder, sp_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    font = pygame.font.SysFont("Arial", 22, bold=True)

    # backgrounds
    bg_folder = "textures/background"
    if not os.path.exists(bg_folder): os.makedirs(bg_folder)
    
    # 1. Suelo con cuadrícula (para ver mejor el 3D)
    fl_w, fl_h = 1024, 1024
    fl_surf = pygame.Surface((fl_w, fl_h))
    fl_surf.fill((35, 35, 40))
    # Dibujar baldosas
    for i in range(0, fl_w, 64):
        pygame.draw.line(fl_surf, (55, 55, 65), (i, 0), (i, fl_h), 2)
        pygame.draw.line(fl_surf, (55, 55, 65), (0, i), (fl_w, i), 2)
    
    # Detalle de sidewalk top
    pygame.draw.rect(fl_surf, (50, 50, 60), (0, 0, fl_w, 40))
    pygame.draw.line(fl_surf, (80, 80, 90), (0, 40), (fl_w, 40), 3)

    pygame.image.save(fl_surf, os.path.join(bg_folder, "street_pavement_texture_with_sidewalk.png"))
    pygame.image.save(fl_surf, os.path.join(bg_folder, "ground.png"))
    
    # 2. Fondo con edificios y ventanas (Noche urbana)
    bg_w, bg_h = 1024, 1024
    bg_surf = pygame.Surface((bg_w, bg_h))
    bg_surf.fill((10, 10, 20)) # Cielo nocturno profundo
    for x in range(20, bg_w, 120):
        h = random.randint(400, 900)
        pygame.draw.rect(bg_surf, (20, 20, 30), (x, bg_h - h, 100, h))
        # Ventanas iluminadas
        for wy in range(bg_h - h + 40, bg_h - 40, 60):
            if random.random() > 0.4:
                color = (255, 255, 150) if random.random() > 0.2 else (200, 150, 50)
                pygame.draw.rect(bg_surf, color, (x+15, wy, 30, 30))
            if random.random() > 0.4:
                color = (255, 255, 150) if random.random() > 0.2 else (200, 150, 50)
                pygame.draw.rect(bg_surf, color, (x+55, wy, 30, 30))
    pygame.image.save(bg_surf, os.path.join(bg_folder, "city_background_texture.png"))

    print("Templates de background regenerados con éxito.")

    # sprites (230x230)
    sprites_to_gen = [("player", BLUE), ("enemy", RED)]
    states = [("idle", "IDLE"), ("hit", "ATTACK"), ("damage", "DAMAGE"), ("ground", "GROUND")]

    # UI Folder
    ui_folder = "textures/ui"
    if not os.path.exists(ui_folder):
        os.makedirs(ui_folder)

    # 3. UI Elements
    # Health Bar Frame (204x25)
    bar_w, bar_h = 204, 25
    frame = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
    pygame.draw.rect(frame, WHITE, (0, 0, bar_w, bar_h), 2)
    pygame.image.save(frame, os.path.join(ui_folder, "health_frame.png"))

    # Health Bar Fill (200x21)
    fill = pygame.Surface((200, 21))
    fill.fill(BLUE)
    pygame.draw.line(fill, (100, 150, 255), (0, 0), (200, 0), 2) # Brillo
    pygame.image.save(fill, os.path.join(ui_folder, "health_fill_player.png"))
    
    fill.fill(RED)
    pygame.draw.line(fill, (255, 100, 100), (0, 0), (200, 0), 2) # Brillo
    pygame.image.save(fill, os.path.join(ui_folder, "health_fill_enemy.png"))

    for prefix, color in sprites_to_gen:
        port = pygame.Surface((PORTRAIT_SIZE, PORTRAIT_SIZE))
        port.fill((color[0]//2, color[1]//2, color[2]//2))
        pygame.draw.rect(port, WHITE, (0,0,PORTRAIT_SIZE,PORTRAIT_SIZE), 3)
        port.blit(font.render("FACE", True, WHITE), (10, 30))
        pygame.image.save(port, os.path.join(sp_folder, f"{prefix}_portrait.png"))

        for s_name, label in states:
            surf = pygame.Surface((CHAR_WIDTH, CHAR_HEIGHT), pygame.SRCALPHA)
            c = color
            if s_name == "hit": c = WHITE
            if s_name == "damage": c = YELLOW
            pygame.draw.rect(surf, c, (0, 0, CHAR_WIDTH, CHAR_HEIGHT))
            pygame.draw.rect(surf, BLACK, (0, 0, CHAR_WIDTH, CHAR_HEIGHT), 4)
            txt = font.render(label, True, BLACK)
            surf.blit(txt, (CHAR_WIDTH//2 - 40, CHAR_HEIGHT//2))
            pygame.image.save(surf, os.path.join(sp_folder, f"{prefix}_{s_name}.png"))

    print("Placeholders regenerados a tamaño 230x230.")

if __name__ == "__main__":
    pygame.init()
    generate_all_placeholders()
