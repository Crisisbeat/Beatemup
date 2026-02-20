import pygame
import os
from utils import load_gif

# Configuración
SPRITE_DIR = "textures/sprites"
OUTPUT_FILE = "textures/sprites/player_sprite_sheet.png"
FRAME_SIZE = (230, 230) # Tamaño estándar de los personajes en el juego
BACKGROUND_COLOR = (0, 0, 0, 0) # Transparente para uso real en el motor
TEXT_COLOR = (240, 240, 240) # Blanco para que se vea en el visor de archivos
LABEL_WIDTH = 250

def create_player_sheet():
    pygame.init()
    # Necesario para poder hacer .convert_alpha() y smoothscale correctamente
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    # Definir las animaciones a incluir
    animations = [
        ("Idle", "player_idle.gif"),
        ("Walk/Run", "player_run.gif"),
        ("Jump", "player_Jump.gif"),
        ("Attack 1", "player_hit.gif"),
        ("Attack 2", "player_hit2.gif"),
        ("Attack 3", "player_hit3.gif"),
        ("Damage", "player_damage.png"),
        ("Ground/KO", "player_ground.png")
    ]
    
    # Cargar todos los frames
    category_frames = []
    max_frames = 0
    
    for label, filename in animations:
        path = os.path.join(SPRITE_DIR, filename)
        frames = []
        if os.path.exists(path):
            if filename.endswith(".gif"):
                frames = load_gif(path, FRAME_SIZE)
            else:
                img = pygame.image.load(path).convert_alpha()
                frames = [pygame.transform.smoothscale(img, FRAME_SIZE)]
        
        category_frames.append((label, frames))
        if len(frames) > max_frames:
            max_frames = len(frames)
            
    if not category_frames:
        print("No se encontraron assets de Player.")
        return

    # Calcular tamaño de la hoja de sprites
    # LABEL_WIDTH + (max_frames * FRAME_SIZE[0])
    sheet_width = LABEL_WIDTH + (max_frames * FRAME_SIZE[0])
    sheet_height = len(category_frames) * FRAME_SIZE[1]
    
    sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
    sheet.fill(BACKGROUND_COLOR)
    
    # Fuente para las etiquetas
    try:
        font = pygame.font.Font("textures/fonts/BADABB_.TTF", 60)
    except:
        font = pygame.font.SysFont("Arial", 60, bold=True)
    
    # Dibujar todo
    for i, (label, frames) in enumerate(category_frames):
        y_pos = i * FRAME_SIZE[1]
        
        # Dibujar Etiqueta
        txt_surf = font.render(label, True, TEXT_COLOR)
        txt_rect = txt_surf.get_rect(midleft=(40, y_pos + FRAME_SIZE[1]//2))
        sheet.blit(txt_surf, txt_rect)
        
        # Dibujar Frames
        for j, frame in enumerate(frames):
            x_pos = LABEL_WIDTH + (j * FRAME_SIZE[0])
            # pygame.draw.rect(sheet, (255, 255, 255, 30), (x_pos, y_pos, FRAME_SIZE[0], FRAME_SIZE[1]), 1)
            sheet.blit(frame, (x_pos, y_pos))
            
    # Guardar la imagen
    pygame.image.save(sheet, OUTPUT_FILE)
    print(f"Hoja de sprites generada con éxito en: {OUTPUT_FILE}")
    pygame.quit()

if __name__ == "__main__":
    create_player_sheet()
