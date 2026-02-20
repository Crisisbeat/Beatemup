import pygame
import sys
import random
import os
import math
from constants import *
from utils import draw_gradient_rect, render_gradient_text, blur_surface
from entities import Character

class CinematicManager:
    def __init__(self, screen):
        self.screen = screen
        self.slides = []
        self.current_slide_idx = 0
        self.frame = 0
        self.active = False
        self.finished = False
        self.load_slides()

    def load_slides(self):
        slide_dir = "slides"
        if os.path.exists(slide_dir):
            files = sorted([f for f in os.listdir(slide_dir) if f.endswith(".png")])
            for f in files:
                try:
                    img = pygame.image.load(os.path.join(slide_dir, f)).convert_alpha()
                    # Definimos efectos predeterminados por slide
                    slide_data = {
                        "image": img,
                        "duration": 180, # 3 segundos aprox
                        "start_pos": (0.5, 0.5),
                        "end_pos": (0.5, 0.5),
                        "start_scale": 1.0,
                        "end_scale": 1.1,
                        "shake": False
                    }
                    # Personalización según el nombre del archivo
                    if "slide1" in f:
                        slide_data["end_pos"] = (0.48, 0.52)
                    elif "slide2" in f:
                        slide_data["start_scale"] = 1.2
                        slide_data["end_scale"] = 1.0
                    elif "slide3" in f:
                        slide_data["shake"] = True
                        slide_data["duration"] = 120 # Más rápido para acción
                    
                    self.slides.append(slide_data)
                except:
                    print(f"Error cargando slide: {f}")
        
        if not self.slides:
            # Fallback: Crear un slide vacío con texto si no hay imágenes
            surf = pygame.Surface((WIDTH, HEIGHT))
            surf.fill((20, 20, 30))
            self.slides.append({
                "image": surf, "duration": 60, "start_pos": (0.5, 0.5),
                "end_pos": (0.5, 0.5), "start_scale": 1.0, "end_scale": 1.0, "shake": False
            })

    def start(self):
        self.active = True
        self.current_slide_idx = 0
        self.frame = 0
        self.finished = False

    def skip(self):
        self.active = False
        self.finished = True

    def update(self):
        if not self.active: return
        
        self.frame += 1
        current_slide = self.slides[self.current_slide_idx]
        
        if self.frame >= current_slide["duration"]:
            self.current_slide_idx += 1
            self.frame = 0
            if self.current_slide_idx >= len(self.slides):
                self.active = False
                self.finished = True

    def draw(self):
        if not self.active: return
        
        slide = self.slides[self.current_slide_idx]
        progress = self.frame / slide["duration"]
        
        # Paneo (Interpolación Lineal entre posiciones)
        x_pos = slide["start_pos"][0] + (slide["end_pos"][0] - slide["start_pos"][0]) * progress
        y_pos = slide["start_pos"][1] + (slide["end_pos"][1] - slide["start_pos"][1]) * progress
        
        # Zoom (Interpolación entre escalas)
        scale = slide["start_scale"] + (slide["end_scale"] - slide["start_scale"]) * progress
        
        # Temblor
        off_x, off_y = 0, 0
        if slide["shake"]:
            off_x = random.randint(-4, 4)
            off_y = random.randint(-4, 4)
            
        scaled_w = int(WIDTH * scale)
        scaled_h = int(HEIGHT * scale)
        
        try:
            # Dibujamos centrado según las coordenadas de paneo
            img_to_draw = pygame.transform.smoothscale(slide["image"], (scaled_w, scaled_h))
            rect = img_to_draw.get_rect(center=(int(WIDTH * x_pos) + off_x, int(HEIGHT * y_pos) + off_y))
            self.screen.blit(img_to_draw, rect)
        except:
             self.screen.blit(slide["image"], (0, 0))

        # Overlay negro suave en los bordes para estilo cinematográfico
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, WIDTH, 40))
        pygame.draw.rect(self.screen, (0, 0, 0), (0, HEIGHT - 40, WIDTH, 40))

class Prop:
    def __init__(self, name, x, y):
        self.name = name
        self.world_pos = pygame.Vector2(x, y)
        self.z = 0
        self.z_priority = 0
        self.image = None
        self.load_image()
        
    def load_image(self):
        path = f"textures/sprites/props/{self.name}.png"
        if os.path.exists(path):
            self.image = pygame.image.load(path).convert_alpha()
        else:
            self.image = pygame.Surface((40, 40))
            self.image.fill((200, 0, 200))

    def draw(self, screen, camera_x, scale):
        if not self.image: return
        
        # 1. Calcular Profundidad según Y (0.0 en el horizonte, 1.0 al frente)
        v = (self.world_pos.y - FLOOR_START_Y) / (HEIGHT - FLOOR_START_Y)
        # Factor de escala horizontal idéntico al del suelo para sincronización total
        h_scale = 0.4 + v * 2.2 
        
        # 2. Posición X con Perspectiva
        # El centro de la pantalla es el punto de fuga (Vanishing Point)
        center_offset = WIDTH // 2
        rel_world_x = self.world_pos.x - (camera_x + WIDTH // 2)
        screen_x = center_offset + (rel_world_x * h_scale)
        
        # 3. No dibujar si está fuera de pantalla
        if screen_x < -300 or screen_x > WIDTH + 300: return
        
        # 4. Escalar imagen
        # Usamos 'scale' que viene del loop central (sincronizado con personajes)
        img_w = int(self.image.get_width() * scale)
        img_h = int(self.image.get_height() * scale)
        if img_w <= 0 or img_h <= 0: return
        
        try:
            img = pygame.transform.smoothscale(self.image, (img_w, img_h))
            rect = img.get_rect()
            rect.midbottom = (int(screen_x), int(self.world_pos.y))
            screen.blit(img, rect)
        except:
            pass

class GameEngine:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Beat 'em Up 2.5D - Sound & Scale Update")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        
        # --- SOPORTE MÓVIL Y MANDOS ---
        self.mobile_mode = False # Se activa si detecta touch o mando
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks: j.init()
        
        # Rectángulos de botones virtuales (ajustados a WIDTH, HEIGHT)
        btn_s = 80
        self.v_btns = {
            "up": pygame.Rect(100, HEIGHT - 180, btn_s, btn_s),
            "down": pygame.Rect(100, HEIGHT - 80, btn_s, btn_s),
            "left": pygame.Rect(30, HEIGHT - 130, btn_s, btn_s),
            "right": pygame.Rect(170, HEIGHT - 130, btn_s, btn_s),
            "attack": pygame.Rect(WIDTH - 110, HEIGHT - 110, btn_s + 20, btn_s + 20),
            "special": pygame.Rect(WIDTH - 220, HEIGHT - 100, btn_s, btn_s),
            "jump": pygame.Rect(WIDTH - 110, HEIGHT - 220, btn_s, btn_s),
            "pause": pygame.Rect(WIDTH - 60, 20, 40, 40)
        }
        self.active_touches = {} # ID: ButtonName
        
        self.player = Character(200, 480, BLUE, is_player=True)
        self.enemies = []
        self.props = []
        
        # Generar algunos props decorativos (distribuidos en las aceras)
        for i in range(25):
            px = 400 + i * 450 + random.randint(-100, 100)
            
            # Distribución: Postes abajo, otros en los bordes
            prob = random.random()
            if prob < 0.35: # Postes: Siempre en el borde inferior (cerca de cámara)
                ptype = "lamp_post"
                py = random.randint(HEIGHT - 25, HEIGHT - 5)
            else: # Solo canecas: Arriba o Abajo, lejos de la zona de combate
                ptype = "trash_can"
                if random.random() > 0.5:
                    py = random.randint(FLOOR_START_Y + 5, FLOOR_START_Y + 40) # Aceras fondo
                else:
                    py = random.randint(HEIGHT - 60, HEIGHT - 20) # Aceras frente
            
            self.props.append(Prop(ptype, px, py))
        
        self.last_tap_time = 0
        self.last_key = None
        
        self.wave_active = False
        self.wave_enemies_to_spawn = 0
        self.wave_spawn_timer = 0
        
        self.camera_x = 0
        self.target_wave_x = 800 
        self.world_end_x = 20000
        
        # Sistema de Iluminación
        self.light_pos = pygame.Vector2(WIDTH // 2, 200)
        self.light_strength = 200 # Radio de luz
        
        self.load_textures()
        
        # --- VOLUMEN Y PAUSA ---
        self.paused = False
        self.menu_index = 0
        self.music_volume = 0.3
        self.sfx_volume = 0.5 # Reducido un 25% extra (aprox 0.75 * original)
        self.menu_options = ["CONTINUAR", "REINICIAR", "VOL MUSICA", "VOL SFX"]
        
        # Ajustar volúmenes iniciales según petición
        self.music_volume = 0.25 # Antes 0.3
        self.sfx_volume = 0.4   # Antes 0.5 (Reducido un poco más)
        
        self.load_sounds()
        self.apply_volumes()
        
        # Iniciar Música
        if "music" in self.sounds:
            self.sounds["music"].play(-1) # Loop infinito
        
        # Sistema de Combo
        font_path = "textures/fonts/BADABB_.TTF"
        if not os.path.exists(font_path): # Fallback if folder name is different
            font_path = "fonts/BADABB_.TTF"
            
        if os.path.exists(font_path):
            self.combo_font = pygame.font.Font(font_path, 110)
            self.combo_label_font = pygame.font.Font(font_path, 70)
            self.ui_name_font = pygame.font.Font(font_path, 25) # Nueva fuente para nombres
        else:
            self.combo_font = pygame.font.SysFont("Impact", 110)
            self.combo_label_font = pygame.font.SysFont("Impact", 70)
            self.ui_name_font = pygame.font.SysFont("Arial", 25, bold=True)
        
        # Estado de Combo
        self.combo_vis_timer = 0
        self.combo_vis_count = 0
        self.combo_vis_pos = pygame.Vector2(0, 0)
        self.current_combo_hits = 0
        self.last_combo_hit_time = 0
        self.combo_timeout = 1000 # 1 segundo para resetear el combo
        
        # Pre-renderizado de UI estática para rendimiento
        # Nombres con la misma fuente de GO! y degradado blanco/gris para legibilidad
        self.ui_name_player = render_gradient_text(self.ui_name_font, "Chapulin", (255, 255, 255), (180, 180, 180), outline_width=3)
        self.ui_name_enemy = render_gradient_text(self.ui_name_font, "PUNK", (255, 255, 255), (180, 180, 180), outline_width=3)
        self.ui_go_text = render_gradient_text(self.combo_label_font, "GO!", (255, 255, 0), (255, 40, 0), outline_width=4)
        self.last_go_blink_tick = -1
        
        # Colores para el degradado del combo (Amarillo a Rojo)
        C_TOP = (255, 255, 0)
        C_BOTTOM = (255, 40, 0)
        
        self.ui_combo_label = render_gradient_text(self.combo_label_font, "HITS", C_TOP, C_BOTTOM, outline_width=4)
        
        # Pre-renderizar números para mayor flexibilidad
        self.combo_num_surfs = {}
        for i in range(2, 51):
            self.combo_num_surfs[i] = render_gradient_text(self.combo_font, str(i), C_TOP, C_BOTTOM, outline_width=5)
            
        # --- PRE-CACHEO DE ENEMIGOS ---
        # Crear un enemigo temporal para forzar la carga de todos sus assets (GIFs/Sprites) en el cache global
        # Esto evita el mini-congelamiento la primera vez que aparece uno.
        temp_enemy = Character(-1000, -1000, RED) 
        del temp_enemy
        
        # --- ESTADO INICIAL DEL JUEGO ---
        self.game_state = "MENU" # MENU, PLAYING
        self.menu_logo = None
        logo_path = "textures/ui/placeholder_logo.png"
        if os.path.exists(logo_path):
            self.menu_logo = pygame.image.load(logo_path).convert_alpha()
        
        self.menu_button_rect = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 130, 220, 70) # Bajado un ~10% de la pantalla (50px aprox)
        self.menu_button_pressed = False
        self.menu_button_hover = False
        self.disclaimer_font = pygame.font.SysFont("Arial", 14)
        self.disclaimer_text = "Esto es una demo en estado de propuesta inicial, no representa la calidad del producto final"
        
        self.cinematic = CinematicManager(self.screen)
        
        self.city_buildings = []
        for i in range(100):
            w = random.randint(100, 300)
            h = random.randint(150, 400)
            x = i * 200 + random.randint(-50, 50)
            self.city_buildings.append(pygame.Rect(x, FLOOR_START_Y - h, w, h))

    def load_textures(self):
        self.bg_tex = None
        self.floor_tex = None
        
        bg_path = "textures/background/city_background_texture.png"
        floor_path = "textures/background/ground.png"
        if not os.path.exists(floor_path):
            floor_path = "textures/background/street_pavement_texture_with_sidewalk.png"
        
        if os.path.exists(bg_path):
            raw_bg = pygame.image.load(bg_path).convert()
            # ESCALADO DE ALTA CALIDAD: Ajustar altura pero preservar ancho para nitidez
            target_h = FLOOR_START_Y
            aspect_ratio = raw_bg.get_width() / raw_bg.get_height()
            target_w = int(target_h * aspect_ratio)
            self.bg_tex = pygame.transform.smoothscale(raw_bg, (target_w, target_h))
            
        if os.path.exists(floor_path):
            raw_floor = pygame.image.load(floor_path).convert()
            # Mantenemos el suelo con alta resolución para evitar pixelación en las tiras
            # Si es extremadamente grande, lo limitamos, pero 1024 o 2048 está bien.
            if raw_floor.get_height() > 1024:
                raw_floor = pygame.transform.smoothscale(raw_floor, (int(1024 * (raw_floor.get_width() / raw_floor.get_height())), 1024))
            self.floor_tex = raw_floor
        else:
            # Generar placeholder de suelo detallado si no existe
            self.generate_background_placeholders()

        # Cargar Texturas de UI
        self.ui_frame = None
        self.ui_fill_p = None
        self.ui_fill_e = None
        
        ui_path = "textures/ui/"
        if os.path.exists(ui_path + "health_frame.png"):
            self.ui_frame = pygame.image.load(ui_path + "health_frame.png").convert_alpha()
            self.ui_fill_p = pygame.image.load(ui_path + "health_fill_player.png").convert_alpha()
            self.ui_fill_e = pygame.image.load(ui_path + "health_fill_enemy.png").convert_alpha()

    def load_sounds(self):
        self.sounds = {}
        sound_path = "sounds/"
        if not os.path.exists(sound_path):
            os.makedirs(sound_path)
            
        files = {
            "hit1": "player_hit1.wav",
            "hit2": "player_hit2.wav",
            "hit3": "player_hit3.wav",
            "p_damage": "player_damage.wav",
            "e_damage": "enemy_damage.wav",
            "e_hit": "enemy_hit.wav",
            "powerup": "power_up.wav",
            "music": "music.wav",
            "go_bell": "go_bell.wav",
            "hit_special": "player_hit_special.wav"
        }
        
        for key, filename in files.items():
            path = os.path.join(sound_path, filename)
            
            # Soporte para MP3 en la música
            if key == "music":
                mp3_path = os.path.join(sound_path, "music.mp3")
                if os.path.exists(mp3_path):
                    path = mp3_path
            
            if os.path.exists(path):
                self.sounds[key] = pygame.mixer.Sound(path)
                if key == "music": self.sounds[key].set_volume(self.music_volume)
                else: self.sounds[key].set_volume(self.sfx_volume)

    def apply_volumes(self):
        """Aplica los volúmenes actuales a todos los sonidos cargados."""
        for key, sound in self.sounds.items():
            if key == "music":
                sound.set_volume(self.music_volume)
            else:
                sound.set_volume(self.sfx_volume)

    def generate_background_placeholders(self):
        bg_folder = "textures/background"
        if not os.path.exists(bg_folder): os.makedirs(bg_folder)
        
        # Suelo con cuadrícula (para ver mejor el 3D)
        fl_w, fl_h = 1024, 1024
        fl_surf = pygame.Surface((fl_w, fl_h))
        fl_surf.fill((35, 35, 40))
        # Dibujar baldosas con un poco más de detalle
        for i in range(0, fl_w, 64):
            # Líneas verticales (profundidad en el juego)
            pygame.draw.line(fl_surf, (55, 55, 65), (i, 0), (i, fl_h), 2)
            # Líneas horizontales
            pygame.draw.line(fl_surf, (55, 55, 65), (0, i), (fl_w, i), 2)
            
        # Añadir un "sidewalk" o borde
        pygame.draw.rect(fl_surf, (50, 50, 60), (0, 0, fl_w, 40))
        pygame.draw.line(fl_surf, (80, 80, 90), (0, 40), (fl_w, 40), 3)

        pygame.image.save(fl_surf, os.path.join(bg_folder, "street_pavement_texture_with_sidewalk.png"))
        # Guardo también como ground.png por si el usuario lo prefiere
        pygame.image.save(fl_surf, os.path.join(bg_folder, "ground.png"))
        
        # Fondo con edificios/ventanas
        bg_w, bg_h = 512, 512
        bg_surf = pygame.Surface((bg_w, bg_h))
        bg_surf.fill((15, 15, 25))
        for x in range(30, bg_w, 100):
            pygame.draw.rect(bg_surf, (25, 25, 35), (x, 100, 70, 412))
            for wy in range(120, 400, 40):
                pygame.draw.rect(bg_surf, (60, 60, 40), (x+10, wy, 20, 20))
                pygame.draw.rect(bg_surf, (60, 60, 40), (x+40, wy, 20, 20))
        pygame.image.save(bg_surf, os.path.join(bg_folder, "city_background_texture.png"))
        
        # Recargar
        self.load_textures()

    def trigger_wave(self):
        self.wave_active = True
        self.wave_enemies_to_spawn = random.randint(2, 4)
        self.wave_spawn_timer = 0

    def spawn_enemy(self):
        offsets = [pygame.Vector2(75, -15), pygame.Vector2(-75, 15), pygame.Vector2(0, 45)]
        spawn_x = self.camera_x + (WIDTH + 100 if random.random() > 0.5 else -100)
        e = Character(spawn_x, random.randint(FLOOR_START_Y + 40, HEIGHT - 40), RED)
        e.target_offset = random.choice(offsets)
        self.enemies.append(e)
        self.wave_enemies_to_spawn -= 1

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Eventos de Menú (MOUSE)
            if self.game_state == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.menu_button_rect.collidepoint(event.pos):
                        self.menu_button_pressed = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.menu_button_pressed and self.menu_button_rect.collidepoint(event.pos):
                        self.game_state = "CINEMATIC"
                        self.cinematic.start()
                    self.menu_button_pressed = False
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                        self.game_state = "CINEMATIC"
                        self.cinematic.start()
                continue

            if self.game_state == "CINEMATIC":
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z, pygame.K_ESCAPE]:
                        self.cinematic.skip()
                        self.game_state = "PLAYING"
                continue

            if event.type == pygame.KEYDOWN:
                # Pausa con Enter
                if event.key == pygame.K_RETURN:
                    self.paused = not self.paused
                    return

                if self.paused:
                    if event.key == pygame.K_UP:
                        self.menu_index = (self.menu_index - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_index = (self.menu_index + 1) % len(self.menu_options)
                    elif event.key == pygame.K_LEFT:
                        if self.menu_index == 2: # Vol Musica
                            self.music_volume = max(0.0, self.music_volume - 0.05)
                            self.apply_volumes()
                        elif self.menu_index == 3: # Vol SFX
                            self.sfx_volume = max(0.0, self.sfx_volume - 0.05)
                            self.apply_volumes()
                    elif event.key == pygame.K_RIGHT:
                        if self.menu_index == 2: # Vol Musica
                            self.music_volume = min(1.0, self.music_volume + 0.05)
                            self.apply_volumes()
                        elif self.menu_index == 3: # Vol SFX
                            self.sfx_volume = min(1.0, self.sfx_volume + 0.05)
                            self.apply_volumes()
                    elif event.key in [pygame.K_z, pygame.K_p, pygame.K_SPACE]:
                        if self.menu_index == 0: # Continuar
                            self.paused = False
                        elif self.menu_index == 1: # Reiniciar
                            self.restart_game()
                    return

                if event.key in [pygame.K_RIGHT, pygame.K_d, pygame.K_LEFT, pygame.K_a]:
                    now = pygame.time.get_ticks()
                    if self.last_key == event.key and now - self.last_tap_time < 450:
                        self.player.is_running = True
                    self.last_tap_time = now
                    self.last_key = event.key
                
                if event.key in [pygame.K_z, pygame.K_p] and self.player.state not in ["STUN", "KNOCKBACK", "DOWN"]:
                    self.execute_player_attack()
                
                if event.key in [pygame.K_x, pygame.K_o] and self.player.state not in ["STUN", "KNOCKBACK", "DOWN"]:
                    self.execute_player_special()
                
                if event.key == pygame.K_SPACE and self.player.state not in ["STUN", "KNOCKBACK", "DOWN"]:
                    if self.player.jumps_done < 2:
                        self.player.velocity_z = JUMP_POWER
                        self.player.state = "JUMP"
                        self.player.jumps_done += 1
                        self.player.jump_anim_timer = 0
                
                if event.key == pygame.K_k and self.player.state not in ["STUN", "KNOCKBACK", "DOWN"]:
                     # Agregamos salto con K también por comodidad si se usa WASD/P
                     if self.player.jumps_done < 2:
                        self.player.velocity_z = JUMP_POWER
                        self.player.state = "JUMP"
                        self.player.jumps_done += 1
                        self.player.jump_anim_timer = 0

            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_RIGHT, pygame.K_d, pygame.K_LEFT, pygame.K_a]:
                    self.player.is_running = False

            # --- EVENTOS TACTILES (ANDROID/IOS) ---
            if event.type in [pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP]:
                self.mobile_mode = True # Activar UI móvil al tocar
                fx, fy = event.x * WIDTH, event.y * HEIGHT
                
                if event.type == pygame.FINGERDOWN:
                    for name, rect in self.v_btns.items():
                        if rect.collidepoint(fx, fy):
                            self.active_touches[event.finger_id] = name
                            self._handle_mobile_input(name, True)
                
                elif event.type == pygame.FINGERUP:
                    if event.finger_id in self.active_touches:
                        name = self.active_touches.pop(event.finger_id)
                        self._handle_mobile_input(name, False)

            # --- EVENTOS DE MANDO (BLUETOOTH) ---
            if event.type == pygame.JOYBUTTONDOWN:
                self.mobile_mode = True
                if event.button == 0: self.execute_player_attack() # A / X
                if event.button == 1: self.execute_player_special() # B / O
                if event.button == 2: # X / []
                     if self.player.jumps_done < 2:
                        self.player.velocity_z = JUMP_POWER
                        self.player.state = "JUMP"
                        self.player.jumps_done += 1
                if event.button == 7: self.paused = not self.paused # Start
            
            if event.type == pygame.JOYAXISMOTION:
                self.mobile_mode = True
                if event.axis == 0: # X-axis
                    if event.value > 0.5: self.player.move_dir.x = 1
                    elif event.value < -0.5: self.player.move_dir.x = -1
                    else: self.player.move_dir.x = 0
                if event.axis == 1: # Y-axis
                    if event.value > 0.5: self.player.move_dir.y = 1
                    elif event.value < -0.5: self.player.move_dir.y = -1
                    else: self.player.move_dir.y = 0

    def _handle_mobile_input(self, name, pressed):
        """Maneja las pulsaciones de botones virtuales."""
        if name == "attack" and pressed: self.execute_player_attack()
        elif name == "special" and pressed: self.execute_player_special()
        elif name == "jump" and pressed:
             if self.player.jumps_done < 2:
                self.player.velocity_z = JUMP_POWER
                self.player.state = "JUMP"
                self.player.jumps_done += 1
        elif name == "pause" and pressed: self.paused = not self.paused
        elif name == "up": self.player.move_dir.y = -1 if pressed else 0
        elif name == "down": self.player.move_dir.y = 1 if pressed else 0
        elif name == "left": self.player.move_dir.x = -1 if pressed else 0
        elif name == "right": self.player.move_dir.x = 1 if pressed else 0

    def execute_player_attack(self):
        now = pygame.time.get_ticks()
        
        # 1. ANTISPAM / BUFFER: No interrumpir si el GIF actual no ha terminado
        # O si estamos en tiempo de recuperación (recovery)
        if self.player.recovery_timer > 0:
            return
            
        if self.player.state == "ATTACK":
            anim_key = f"ATTACK_{self.player.combo_index}"
            if anim_key in self.player.animations:
                # Exigimos que llegue al último frame antes de permitir el siguiente input
                if self.player.anim_frame < len(self.player.animations[anim_key]) - 1:
                    return

        # 2. LOGICA DE COMBO: Decidir el siguiente golpe
        # Si pasó mucho tiempo, volvemos al golpe 1
        if now - self.player.last_attack_time > 800: # Ventana un poco más generosa (800ms)
            self.player.combo_index = 0
        else:
            # Avanzar: 0 -> 1 -> 2 -> 0...
            self.player.combo_index = (self.player.combo_index + 1) % 3
        
        self.player.last_attack_time = now

        # 3. CONFIGURAR ATAQUE SELECCIONADO
        self.player.anim_frame = 0
        self.player.anim_timer = 0
        self.player.state = "ATTACK"
        self.player.hit_connected = False # Reset para la nueva detección en update
        self.player.swing_done = False    # Reset para que el sonido suene en el frame 1
        # Recovery: Bloquea el siguiente input por 3 tics extra tras terminar el GIF
        self.player.recovery_timer = 0 
        
        anim_key = f"ATTACK_{self.player.combo_index}"
        if anim_key in self.player.animations:
            num_frames = len(self.player.animations[anim_key])
            duration = num_frames * 5
            self.player.state_timer = duration
            
            # El recovery_timer BLOQUEA nuevos ataques. 
            # Debe ser: [duración de la animación actual] + [tiempo de descanso]
            # Si es el 3er golpe, damos 40 tics (~0.6s) de descanso real DESPUÉS de que acabe el GIF
            # Para los golpes 1 y 2, reducimos el delay a 2 para mayor fluidez
            delay = 40 if self.player.combo_index == 2 else 2
            self.player.recovery_timer = duration + delay
        else:
            self.player.state_timer = ATTACK_DURATION

    def check_player_hit_logic(self):
        """Nueva detección de colisión basada en frames para sincronización perfecta."""
        if self.player.state != "ATTACK":
            return
            
        # 1. SONIDO DE SWING: Sincronizado con el inicio del movimiento (Frame 1)
        if self.player.anim_frame >= 1 and not self.player.swing_done:
            self.player.swing_done = True
            s_key = f"hit{self.player.combo_index + 1}"
            if s_key in self.sounds:
                self.sounds[s_key].play()

        if self.player.hit_connected:
            return
            
        # Determinar el frame "activo" donde el golpe debe conectar.
        # Bajamos el del finisher de 3 a 2 para que el hit (y el sonido de muerte) sea más inmediato
        active_frame = 2 # Sincronizado para todos los hits en el frame 2 (el 3er frame físico)
        
        anim_key = f"ATTACK_{self.player.combo_index}"
        if anim_key not in self.player.animations:
            active_frame = 0 # Fallback si no hay anim
            
        if self.player.anim_frame >= active_frame:
            # 4. DETECCIÓN DE HITBOX (Múltiples enemigos)
            hit_targets = []
            for e in self.enemies:
                if e.state == "DOWN": continue
                distvec = e.world_pos - self.player.world_pos
                # Rango de detección
                if distvec.length() < HIT_RANGE_X and abs(distvec.y) < (HIT_RANGE_Y * HIT_RANGE_Y_MULT):
                    if (self.player.facing_right and distvec.x > -15) or (not self.player.facing_right and distvec.x < 15):
                        hit_targets.append(e)

            # 5. APLICAR DAÑO Y EFECTOS A TODOS LOS ALCANZADOS
            if hit_targets:
                self.player.hit_connected = True # Marcar como conectado
                
                is_finisher = (self.player.combo_index == 2)
                dmg_to_apply = 10 if not is_finisher else 35
                
                # REVISAR SI ALGÚN ENEMIGO VA A MORIR PARA EL SONIDO ESPECIAL
                any_will_die = any(e.hp <= dmg_to_apply for e in hit_targets)
                
                # Sonidos de impacto: Si alguien muere, usamos el especial directamente para que sea instantáneo
                if any_will_die and "hit_special" in self.sounds:
                    self.sounds["hit_special"].play()
                elif "e_hit" in self.sounds:
                    self.sounds["e_hit"].play()
                
                now_hit = pygame.time.get_ticks()
                knk_dir = pygame.Vector2(1 if self.player.facing_right else -1, 0)
                
                avg_x = 0
                avg_y = 0
                
                for target_enemy in hit_targets:
                    # Gestión de Combo persistente (suma por cada enemigo golpeado)
                    if now_hit - self.last_combo_hit_time < self.combo_timeout:
                        self.current_combo_hits += 1
                    else:
                        self.current_combo_hits = 1
                    self.last_combo_hit_time = now_hit
                    
                    dmg = dmg_to_apply
                    target_enemy.apply_damage(dmg, knockback=is_finisher, knk_dir=knk_dir)
                    
                    if is_finisher:
                        target_enemy.velocity_z = 12 
                        
                    avg_x += target_enemy.world_pos.x
                    avg_y += target_enemy.world_pos.y

                # Mostrar UI de Combo si hay más de 1 golpe total
                if self.current_combo_hits >= 2:
                    self.combo_vis_count = self.current_combo_hits
                    self.combo_vis_timer = 60 
                    # Posición promedio de los impactos para el texto de combo
                    mid_x = (avg_x / len(hit_targets) + self.player.world_pos.x) * 0.5
                    mid_y = (avg_y / len(hit_targets))
                    self.combo_vis_pos = pygame.Vector2(mid_x, mid_y - 250)

    def execute_player_special(self):
        if self.player.hp > PLAYER_SPECIAL_COST:
            self.player.hp -= PLAYER_SPECIAL_COST
            self.player.combo_index = 0 # Reiniciar combo en especial por consistencia
            if self.player.state != "ATTACK":
                self.player.anim_frame = 0
                self.player.anim_timer = 0
            self.player.state = "ATTACK"
            self.player.hit_connected = False
            self.player.swing_done = False
            self.player.state_timer = 25
            for e in self.enemies:
                if e.state == "DOWN": continue
                dist = (e.world_pos - self.player.world_pos).length()
                if dist < 130:
                    knk_dir = e.world_pos - self.player.world_pos
                    if knk_dir.length() > 0: knk_dir = knk_dir.normalize()
                    else: knk_dir = pygame.Vector2(1, 0)
                    e.apply_damage(30, knockback=True, knk_dir=knk_dir)

    def restart_game(self):
        """Reinicia el estado del juego."""
        self.player = Character(200, 480, BLUE, is_player=True)
        self.enemies = []
        self.camera_x = 0
        self.target_wave_x = 800
        self.wave_active = False
        self.wave_enemies_to_spawn = 0
        self.paused = False
        # Reiniciar música por si acaso
        if "music" in self.sounds:
            self.sounds["music"].stop()
            self.sounds["music"].play(-1)

    def update(self):
        if self.game_state == "CINEMATIC":
            self.cinematic.update()
            if self.cinematic.finished:
                self.game_state = "PLAYING"
            return

        if self.paused:
            return
            
        if not self.wave_active:
            # No permitir salir por la izquierda de la vista actual
            if self.player.world_pos.x < self.camera_x + 50: 
                self.player.world_pos.x = self.camera_x + 50
                
            if self.player.world_pos.x > self.camera_x + WIDTH * 0.5:
                self.camera_x += (self.player.world_pos.x - (self.camera_x + WIDTH * 0.5)) * 0.1
            if self.player.world_pos.x > self.target_wave_x:
                self.trigger_wave()
        if self.wave_active:
            if self.player.world_pos.x < self.camera_x + 30: self.player.world_pos.x = self.camera_x + 30
            if self.player.world_pos.x > self.camera_x + WIDTH - 30: self.player.world_pos.x = self.camera_x + WIDTH - 30
            if self.wave_enemies_to_spawn > 0:
                self.wave_spawn_timer += 1
                if self.wave_spawn_timer >= WAVE_SPAWN_INTERVAL or len(self.enemies) == 0:
                    self.spawn_enemy()
                    self.wave_spawn_timer = 0
            if self.wave_enemies_to_spawn <= 0 and len(self.enemies) == 0:
                self.wave_active = False
                self.target_wave_x = self.player.world_pos.x + random.choice(DISTANCE_TO_NEXT_WAVE)

        self.player.update(enemies=self.enemies, camera_x=self.camera_x)
        self.check_player_hit_logic()
        for e in self.enemies: e.update(player_ref=self.player, enemies=self.enemies, camera_x=self.camera_x)
        
        # Mover la luz suavemente siguiendo al jugador o un patrón
        self.light_pos.x = (self.player.world_pos.x - self.camera_x)
        self.light_pos.y = self.player.world_pos.y - self.player.z - 100
        
        if self.combo_vis_timer > 0:
            self.combo_vis_timer -= 1
            
        # Limpiar enemigos solo cuando terminen de parpadear y morir
        self.enemies = [e for e in self.enemies if not e.death_sequence_finished]

    def draw_3d_floor(self):
        if not self.floor_tex:
            draw_gradient_rect(self.screen, (0, FLOOR_START_Y, WIDTH, HEIGHT - FLOOR_START_Y), FLOOR_TOP, FLOOR_BOTTOM)
            return

        floor_h = HEIGHT - FLOOR_START_Y
        tex_w, tex_h = self.floor_tex.get_size()
        center_offset = WIDTH // 2
        
        # Dibujamos línea a línea desde el horizonte hasta el frente
        for sy in range(0, floor_h, 2): # Paso de 2 para optimizar
            v = sy / floor_h
            h_scale = 0.4 + v * 2.2 # El mismo factor que los props
            
            line_w = int(WIDTH * h_scale)
            if line_w <= 0: continue
            
            # Textura v-mapping (v^1.8 genera sensación de mayor velocidad al frente)
            # Clampeamos ty para evitar errores de subsurface
            ty = int((v**1.8 % 1.0) * tex_h)
            ty = max(0, min(ty, tex_h - 1))
            
            try:
                line_slice = self.floor_tex.subsurface((0, ty, tex_w, 1))
                # Usamos scale en lugar de smoothscale para mayor estabilidad y rendimiento
                scaled_line = pygame.transform.scale(line_slice, (line_w, 2))
                
                # Posicionamiento: El mundo se mueve respecto a camera_x
                # Pero la perspectiva "comprime" ese movimiento al fondo
                rel_x = int(self.camera_x * h_scale) % line_w
                
                start_x = (center_offset - rel_x)
                if line_w > 0:
                    while start_x > 0: start_x -= line_w
                
                x = start_x
                while x < WIDTH:
                    self.screen.blit(scaled_line, (x, FLOOR_START_Y + sy))
                    if line_w > 0: x += line_w
                    else: break
            except:
                continue

    def draw_3d_background(self):
        if not self.bg_tex:
            draw_gradient_rect(self.screen, (0, 0, WIDTH, FLOOR_START_Y), SKY_TOP, SKY_BOTTOM)
            return

        # Fondo PARALELO a la pantalla (Vertical/Upright)
        tex_w = self.bg_tex.get_width()
        # Parallax suave
        rel_x = int(self.camera_x * 0.3) % tex_w
        
        self.screen.blit(self.bg_tex, (-rel_x, 0))
        # Tiling: Si el fondo no cubre toda la pantalla por el rel_x, dibujamos otro al lado
        if rel_x > 0:
             self.screen.blit(self.bg_tex, (tex_w - rel_x, 0))
        if tex_w - rel_x < WIDTH:
             self.screen.blit(self.bg_tex, (tex_w - rel_x + tex_w, 0)) # Tercer tile por si acaso

    def draw(self):
        if self.game_state == "MENU":
            self.draw_main_menu()
            return
            
        if self.game_state == "CINEMATIC":
            self.screen.fill((0, 0, 0))
            self.cinematic.draw()
            # Botón de saltar pequeño en una esquina
            skip_text = self.font.render("ENTER PARA SALTAR", True, (150, 150, 150))
            self.screen.blit(skip_text, (WIDTH - 180, HEIGHT - 30))
            pygame.display.flip()
            return

        # 1. Dibujar Planos 3D
        self.draw_3d_background()
        self.draw_3d_floor()

        # 2. Dibujar Sprites (Personajes + Props) ordenados por Y (Profundidad)
        all_sprites = []
        all_sprites.append(self.player)
        for e in self.enemies: all_sprites.append(e)
        for p in self.props: all_sprites.append(p)
        
        # Profundidad dinámica: El atacante se sobrepone al herido solo si están en la misma línea (Y)
        # Esto evita que se sobrepongan a objetos de la escena como postes.
        all_sprites.sort(key=lambda s: (int(s.world_pos.y), getattr(s, 'z_priority', 0)))
        
        for s in all_sprites:
            # Calcular escala según profundidad Y
            y_diff = s.world_pos.y - FLOOR_START_Y
            v_factor = y_diff / (HEIGHT - FLOOR_START_Y) if HEIGHT != FLOOR_START_Y else 0
            sprite_scale = 0.8 + (v_factor * 0.4)
            sprite_scale = max(0.01, sprite_scale) # Seguridad total
            
            s.draw(self.screen, self.camera_x, scale=sprite_scale)

        # 2.1 Dibujar Texto de Combo
        if self.combo_vis_timer > 0:
            self.draw_combo_ui()


        # 3. UI
        self.draw_ui()
        if not self.wave_active:
            current_blink = pygame.time.get_ticks() // 600
            if current_blink % 2 == 0:
                # Play sound only when transitioning to visible
                if self.last_go_blink_tick != current_blink:
                    if "go_bell" in self.sounds: self.sounds["go_bell"].play()
                    self.last_go_blink_tick = current_blink
                
                # Sombra del GO!
                shd_go = self.ui_go_text.copy()
                shd_go.fill((0, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
                shd_rect = shd_go.get_rect(center=(WIDTH - 150 + 4, 150 + 4))
                self.screen.blit(shd_go, shd_rect)

                # Dibujar "GO!" con sombra y escalado suave
                go_rect = self.ui_go_text.get_rect(center=(WIDTH - 150, 150))
                self.screen.blit(self.ui_go_text, go_rect)
            
        if self.paused:
            self.draw_pause_menu()
        
        if self.mobile_mode:
            self.draw_mobile_ui()
            
        pygame.display.flip()

    def draw_mobile_ui(self):
        """Dibuja los botones virtuales translucidos."""
        for name, rect in self.v_btns.items():
            color = (255, 255, 255, 80)
            # Resaltar si está presionado
            if name in self.active_touches.values():
                color = (255, 255, 0, 150)
            
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.ellipse(s, color, (0, 0, rect.width, rect.height))
            
            # Texto descriptivo
            label = name[0].upper() if len(name) > 1 else name.upper()
            txt = self.ui_name_font.render(label, True, (255, 255, 255, 180))
            s.blit(txt, txt.get_rect(center=(rect.width//2, rect.height//2)))
            
            self.screen.blit(s, rect)

    def draw_pause_menu(self):
        # Overlay oscuro
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Titulo PAUSA con fuente Arcade y degradado
        title_surf = render_gradient_text(self.combo_label_font, "PAUSA", (255, 255, 0), (255, 40, 0), outline_width=5)
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 140))
        self.screen.blit(title_surf, title_rect)
        
        # Opciones
        for i, option in enumerate(self.menu_options):
            is_selected = (i == self.menu_index)
            color_t = (255, 255, 0) if is_selected else (255, 255, 255)
            color_b = (255, 150, 0) if is_selected else (180, 180, 180)
            
            text = option
            if i == 2: text += f": {int(self.music_volume * 100)}%"
            if i == 3: text += f": {int(self.sfx_volume * 100)}%"
            
            # Renderizar opción con fuente Arcade y degradado
            opt_surf = render_gradient_text(self.ui_name_font, text, color_t, color_b, outline_width=3)
            
            # Efecto de escala para la opción seleccionada
            if is_selected:
                s_w = int(opt_surf.get_width() * 1.2)
                s_h = int(opt_surf.get_height() * 1.2)
                opt_surf = pygame.transform.smoothscale(opt_surf, (s_w, s_h))
                
            opt_rect = opt_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 20 + i * 50))
            self.screen.blit(opt_surf, opt_rect)
            
            if i == self.menu_index:
                # Dibujar flechitas indicadoras
                pygame.draw.polygon(self.screen, YELLOW, [(opt_rect.left - 20, opt_rect.centery - 5), 
                                                        (opt_rect.left - 20, opt_rect.centery + 5), 
                                                        (opt_rect.left - 10, opt_rect.centery)])

    def draw_combo_ui(self):
        if self.combo_vis_count not in self.combo_num_surfs: return

        # 1. Recuperar superficies pre-renderizadas
        num_surf = self.combo_num_surfs[self.combo_vis_count]
        
        # 2. Aplicar Efecto de Escala (Pop)
        # El timer va de 60 a 0. Queremos un pop rápido al inicio.
        pop_progress = max(0, self.combo_vis_timer - 45) / 15.0 # Pop en los primeros 15 frames
        scale_fact = 1.0 + pop_progress * 0.5
        
        # Fade out al final
        alpha = 255
        if self.combo_vis_timer < 15:
            alpha = int(255 * (self.combo_vis_timer / 15.0))
        
        # Re-escalar para que no sea GIGANTE
        final_scale = 0.7 * scale_fact
        
        try:
            num_w = int(num_surf.get_width() * final_scale)
            num_h = int(num_surf.get_height() * final_scale)
            if num_w > 0 and num_h > 0:
                draw_num = pygame.transform.scale(num_surf, (num_w, num_h))
                
                label_w = int(self.ui_combo_label.get_width() * 0.6)
                label_h = int(self.ui_combo_label.get_height() * 0.6)
                draw_label = pygame.transform.scale(self.ui_combo_label, (label_w, label_h))
                
                if alpha < 255:
                    draw_num.set_alpha(alpha)
                    draw_label.set_alpha(alpha)
                
                # Sombras proyectadas (offset dinámico)
                shd_alpha = int(alpha * 0.5)
                shd_num = draw_num.copy()
                shd_num.fill((0, 0, 0, shd_alpha), special_flags=pygame.BLEND_RGBA_MULT)
                shd_label = draw_label.copy()
                shd_label.fill((0, 0, 0, shd_alpha), special_flags=pygame.BLEND_RGBA_MULT)
                
                screen_pos = pygame.Vector2(self.combo_vis_pos.x - self.camera_x, self.combo_vis_pos.y)
                
                # Dibujar Sombras primero
                self.screen.blit(shd_label, (screen_pos.x - draw_label.get_width()//2 + 5, screen_pos.y + num_h * 0.4 - draw_label.get_height()//2 + 5))
                self.screen.blit(shd_num, (screen_pos.x - draw_num.get_width()//2 + 5, screen_pos.y - draw_num.get_height()//2 + 5))
                
                # Dibujar Originales
                label_rect = draw_label.get_rect(center=(screen_pos.x, screen_pos.y + num_h * 0.4))
                self.screen.blit(draw_label, label_rect)
                
                num_rect = draw_num.get_rect(center=screen_pos)
                self.screen.blit(draw_num, num_rect)
        except:
            pass


    def draw_ui(self):
        # 1. HUD DEL JUGADOR
        p_portrait = self.player.sprites.get("portrait")
        hud_pos = (20, 20)
        hud_scale = 0.8 # Reducir 20%
        
        # Primero Dibujar el Marco
        if self.ui_frame:
            frame_img = pygame.transform.smoothscale(self.ui_frame, (int(450 * hud_scale), int(120 * hud_scale)))
            self.screen.blit(frame_img, hud_pos)
            
            # Dibujar la vida (Relleno) - Ajustado para que quepa bien en el hueco
            if self.ui_fill_p:
                hp_w = int(2.8 * self.player.hp * hud_scale)
                if hp_w > 0:
                    hp_fill = pygame.transform.scale(self.ui_fill_p, (hp_w, int(25 * hud_scale)))
                    # El hueco de vida en el frame está un poco más arriba
                    self.screen.blit(hp_fill, (hud_pos[0] + int(110 * hud_scale), hud_pos[1] + int(37 * hud_scale)))
        else:
            # Fallback
            pygame.draw.rect(self.screen, BLACK, (hud_pos[0] + 85, hud_pos[1] + 30, 204, 25))
            hp_w = int(2 * self.player.hp)
            pygame.draw.rect(self.screen, BLUE, (hud_pos[0] + 87, hud_pos[1] + 32, hp_w, 21))
        
        # Dibujar el retrato ENCIMA del frame (en el hexágono)
        if p_portrait:
            port_size = int(82 * hud_scale) # Aumentado 20% adicional
            port_img = pygame.transform.smoothscale(p_portrait, (port_size, port_size))
            port_rect = port_img.get_rect(center=(hud_pos[0] + int(60 * hud_scale), hud_pos[1] + int(60 * hud_scale)))
            self.screen.blit(port_img, port_rect)
                
        # Nombre del Jugador MAS ARRIBA
        self.screen.blit(self.ui_name_player, (hud_pos[0] + int(115 * hud_scale), hud_pos[1] + int(2 * hud_scale)))

        if self.enemies:
            # HUD DEL ENEMIGO (Espejado al lado derecho)
            alive_enemies = [e for e in self.enemies if not e.is_dead or e.state != "DOWN"]
            if not alive_enemies: alive_enemies = self.enemies
            
            closest = min(alive_enemies, key=lambda e: (e.world_pos - self.player.world_pos).length())
            dist_to_p = (closest.world_pos - self.player.world_pos).length()
            
            if dist_to_p < 450:
                e_portrait = closest.sprites.get("portrait")
                e_hud_w = int(450 * hud_scale)
                e_hud_pos = (WIDTH - e_hud_w - 20, 20)

                if self.ui_frame:
                    e_frame = pygame.transform.smoothscale(self.ui_frame, (e_hud_w, int(120 * hud_scale)))
                    e_frame = pygame.transform.flip(e_frame, True, False)
                    self.screen.blit(e_frame, e_hud_pos)
                    
                    if self.ui_fill_e:
                        hp_w_e = int(2.8 * max(0, closest.hp) * hud_scale)
                        if hp_w_e > 0:
                            hp_fill_e = pygame.transform.scale(self.ui_fill_e, (hp_w_e, int(25 * hud_scale)))
                            hp_fill_e = pygame.transform.flip(hp_fill_e, True, False)
                            self.screen.blit(hp_fill_e, (e_hud_pos[0] + e_hud_w - int(110 * hud_scale) - hp_w_e, e_hud_pos[1] + int(37 * hud_scale)))
                else:
                    # Fallback
                    pygame.draw.rect(self.screen, BLACK, (WIDTH - 289, 30, 204, 25))
                    hp_w_e = int(2 * max(0, closest.hp))
                    pygame.draw.rect(self.screen, RED, (WIDTH - 287, 32, hp_w_e, 21))

                # Retrato Enemigo ENCIMA del frame
                if e_portrait:
                    port_size = int(82 * hud_scale) # Aumentado 20% adicional
                    port_img = pygame.transform.smoothscale(e_portrait, (port_size, port_size))
                    port_img = pygame.transform.flip(port_img, True, False)
                    port_rect = port_img.get_rect(center=(e_hud_pos[0] + e_hud_w - int(60 * hud_scale), e_hud_pos[1] + int(60 * hud_scale)))
                    self.screen.blit(port_img, port_rect)
                        
                # Nombre Enemigo MAS ARRIBA
                self.screen.blit(self.ui_name_enemy, (e_hud_pos[0] + e_hud_w - int(230 * hud_scale), e_hud_pos[1] + int(2 * hud_scale)))

    def draw_main_menu(self):
        # 1. Dibujar fondo (desenfocado)
        menu_bg = pygame.Surface((WIDTH, HEIGHT))
        self.draw_3d_background_to(menu_bg)
        self.draw_3d_floor_to(menu_bg)
        
        blurred_bg = blur_surface(menu_bg, amount=6)
        # Añadir un overlay oscuro para contraste
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        blurred_bg.blit(overlay, (0, 0))
        
        self.screen.blit(blurred_bg, (0, 0))
        
        # 2. Logo
        if self.menu_logo:
            logo_rect = self.menu_logo.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
            self.screen.blit(self.menu_logo, logo_rect)
            
        # 3. Botón "A Jugar!"
        self.menu_button_hover = self.menu_button_rect.collidepoint(pygame.mouse.get_pos())
        
        # Glow intermitente
        glow_val = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5 # 0 a 1
        btn_color = list(YELLOW)
        if self.menu_button_hover:
            btn_color = [min(255, c + 40) for c in btn_color]
        
        # Dibujar Botón con desplazamiento si se presiona
        draw_rect = self.menu_button_rect.copy()
        if self.menu_button_pressed:
            draw_rect.y += 4
            
        # Sombra del botón
        pygame.draw.rect(self.screen, (0,0,0,100), draw_rect.move(4, 4), border_radius=15)
        
        # Efecto de Glow (Borde brillante exterior)
        glow_size = int(5 + glow_val * 10)
        glow_surf = pygame.Surface((draw_rect.width + glow_size*2, draw_rect.height + glow_size*2), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 255, 0, int(glow_val * 100)), (0, 0, glow_surf.get_width(), glow_surf.get_height()), border_radius=20)
        self.screen.blit(glow_surf, (draw_rect.x - glow_size, draw_rect.y - glow_size))

        pygame.draw.rect(self.screen, btn_color, draw_rect, border_radius=15)
        
        # Texto con degradado rojo
        btn_text = render_gradient_text(self.combo_label_font, "A JUGAR!", (255, 0, 0), (150, 0, 0), outline_width=3)
        btn_rect = btn_text.get_rect(center=draw_rect.center)
        self.screen.blit(btn_text, btn_rect)
        
        # 4. Disclaimer
        disc_surf = self.disclaimer_font.render(self.disclaimer_text, True, WHITE)
        disc_rect = disc_surf.get_rect(center=(WIDTH//2, HEIGHT - 30))
        self.screen.blit(disc_surf, disc_rect)
        pygame.display.flip()

    def draw_3d_background_to(self, surface):
        if not self.bg_tex:
            draw_gradient_rect(surface, (0, 0, WIDTH, FLOOR_START_Y), SKY_TOP, SKY_BOTTOM)
            return
        tex_w = self.bg_tex.get_width()
        rel_x = int(self.camera_x * 0.3) % tex_w
        surface.blit(self.bg_tex, (-rel_x, 0))
        if rel_x > 0: surface.blit(self.bg_tex, (tex_w - rel_x, 0))

    def draw_3d_floor_to(self, surface):
        if not self.floor_tex:
            draw_gradient_rect(surface, (0, FLOOR_START_Y, WIDTH, HEIGHT - FLOOR_START_Y), FLOOR_TOP, FLOOR_BOTTOM)
            return
        floor_h = HEIGHT - FLOOR_START_Y
        tex_w, tex_h = self.floor_tex.get_size()
        center_offset = WIDTH // 2
        for sy in range(0, floor_h, 4): # Más rápido para el menú
            v = sy / floor_h
            h_scale = 0.4 + v * 2.2 
            line_w = int(WIDTH * h_scale)
            if line_w <= 0: continue
            ty = int((v**1.8 % 1.0) * tex_h)
            ty = max(0, min(ty, tex_h - 1))
            try:
                line_slice = self.floor_tex.subsurface((0, ty, tex_w, 1))
                scaled_line = pygame.transform.scale(line_slice, (line_w, 4))
                rel_x = int(self.camera_x * h_scale) % line_w
                start_x = (center_offset - rel_x)
                if line_w > 0:
                    while start_x > 0: start_x -= line_w
                x = start_x
                while x < WIDTH:
                    surface.blit(scaled_line, (x, FLOOR_START_Y + sy))
                    if line_w > 0: x += line_w
                    else: break
            except: continue

    def run(self):
        while True:
            try:
                self.handle_events()
                if self.game_state == "PLAYING":
                    self.update()
                self.draw()
                self.clock.tick(FPS)
            except Exception as e:
                print(f"ERROR EN EL LOOP PRINCIPAL: {e}")
                import traceback
                traceback.print_exc()
                pygame.quit()
                sys.exit()
