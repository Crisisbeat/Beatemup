import pygame

# --- Dimensiones ---
WIDTH, HEIGHT = 960, 540
FLOOR_START_Y = 340
FPS = 60

# --- Tamaño Visual de Personajes (Display Size) ---
CHAR_WIDTH = 230
CHAR_HEIGHT = 230
PORTRAIT_SIZE = 60 # Reducido a tamaño original

# --- Colores ---
SKY_TOP = (15, 15, 30)
SKY_BOTTOM = (45, 45, 65)
FLOOR_TOP = (30, 30, 35)
FLOOR_BOTTOM = (60, 60, 70)
CITY_COLOR = (25, 25, 40)

WHITE = (240, 240, 240)
BLACK = (10, 10, 12)
RED = (230, 60, 70)
BLUE = (60, 130, 255)
GREEN = (80, 220, 120)
YELLOW = (255, 220, 0)
SHADOW_COLOR = (0, 0, 0, 80)

# --- Física y Mecánicas ---
ACCEL = 0.6         
FRICTION = 0.85
BASE_SPEED = 4.0    
RUN_MULTIPLIER = 1.6
GRAVITY = 0.5
JUMP_POWER = 13.0
DIVE_POWER = -18.0

# --- Combate ---
COMBO_WINDOW = 700
ATTACK_DURATION = 14 
ENEMY_ATTACK_PREP = 20
ENEMY_COOLDOWN = 45
PLAYER_SPECIAL_COST = 15
HIT_RANGE_X = 225    
HIT_RANGE_Y = 80     
HIT_RANGE_Y_MULT = 1.3
DOWN_TIME = 90      

# --- Gestión de Escena ---
WAVE_SPAWN_INTERVAL = 240
DISTANCE_TO_NEXT_WAVE = [500, 750, 1000]
# --- Iluminación ---
SUN_POS = pygame.Vector2(WIDTH // 2, -500) # El sol está arriba
