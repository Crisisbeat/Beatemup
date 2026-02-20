import pygame
import random
import os
from constants import *
from utils import get_bottom_pixel, load_gif

# --- CACHE GLOBAL DE RECURSOS ---
# Esto evita que el juego lea el disco cada vez que aparece un enemigo, eliminando el "lag" de spawn.
GLOBAL_ASSET_CACHE = {
    "sprites": {},
    "animations": {},
    "bottoms": {}
}

class Character:
    def __init__(self, x, y, color, is_player=False):
        self.world_pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.z = 0  
        self.velocity_z = 0
        
        self.is_running = False
        self.color = color
        self.is_player = is_player
        self.facing_right = True
        
        self.hp = 100
        self.max_hp = 100
        self.state = "IDLE"  
        self.state_timer = 0
        
        # Animación
        self.animations = {}
        self.anim_frame = 0
        self.anim_timer = 0
        
        self.combo_index = 0
        self.last_attack_time = 0
        self.attack_duration = ATTACK_DURATION
        self.hit_connected = False # Nueva bandera para detección por frame
        self.recovery_timer = 0    # Evita transiciones instantáneas que se sienten mal
        self.z_priority = 0        # Prioridad dinámica para el orden de dibujado (depth sorting)
        self.swing_done = False    # Control para disparar el sonido de swing en el frame correcto
        self.flash_timer = 0       # Efecto visual de flash al recibir daño
        self.jump_anim_timer = 0   # Para sincronizar el GIF de salto
        
        self.target_offset = pygame.Vector2(0, 0)
        self.attack_prep_timer = 0 
        self.attack_cooldown = 0
        
        self.knk_vector = pygame.Vector2(0, 0)
        
        # Estado de Muerte
        self.is_dead = False
        self.death_sequence_finished = False
        self.blink_state = True
        self.blink_timer = 0
        
        # Saltos
        self.jumps_done = 0
        
        self.sprites = {}
        self.sprite_bottoms = {}
        self.load_placeholders()

    def load_placeholders(self):
        folder = "textures/sprites"
        if not os.path.exists(folder):
            os.makedirs(folder)

        # 0. Intentar cargar desde hoja de sprites si es el jugador
        sheet_path = os.path.join(folder, "player_sprite_sheet.png")
        if self.is_player and os.path.exists(sheet_path):
            self.load_from_sprite_sheet(sheet_path)
            return

        prefix = "player" if self.is_player else "enemy"
        names = ["idle", "hit", "damage", "ground", "portrait"]
        for name in names:
            cache_key = f"{prefix}_{name}"
            display_size = (CHAR_WIDTH, CHAR_HEIGHT) if name != "portrait" else (PORTRAIT_SIZE, PORTRAIT_SIZE)

            if cache_key in GLOBAL_ASSET_CACHE["sprites"]:
                self.sprites[name] = GLOBAL_ASSET_CACHE["sprites"][cache_key]
                self.sprite_bottoms[name] = GLOBAL_ASSET_CACHE["bottoms"][cache_key]
                continue

            filename = f"{prefix}_{name}.png"
            path = os.path.join(folder, filename)
            
            if os.path.exists(path):
                raw_img = pygame.image.load(path).convert_alpha()
                surf = pygame.transform.smoothscale(raw_img, display_size)
            else:
                surf = pygame.Surface(display_size, pygame.SRCALPHA)
                c = self.color
                if name == "hit": c = WHITE
                if name == "damage": c = YELLOW
                if name == "portrait": c = (c[0]//2, c[1]//2, c[2]//2)
                pygame.draw.rect(surf, c, (0, 0, display_size[0], display_size[1]))
                pygame.draw.rect(surf, BLACK, (0, 0, display_size[0], display_size[1]), 2)
                
                if name == "portrait":
                    font = pygame.font.SysFont("Arial", 10, bold=True)
                    txt = font.render("PORTRAIT", True, WHITE)
                    surf.blit(txt, (2, 20))

                pygame.image.save(surf, path)

            self.sprites[name] = surf
            self.sprite_bottoms[name] = get_bottom_pixel(surf)
            GLOBAL_ASSET_CACHE["sprites"][cache_key] = surf
            GLOBAL_ASSET_CACHE["bottoms"][cache_key] = self.sprite_bottoms[name]

        # --- CARGAR ANIMACIONES (GIFs) ---
        if self.is_player:
            self._cache_and_load_gif("WALK", os.path.join(folder, "player_run.gif"))
            for i in range(3):
                suffix = str(i+1)
                h_path = os.path.join(folder, f"player_hit{suffix}.gif")
                if i == 0 and not os.path.exists(h_path): h_path = os.path.join(folder, "player_hit.gif")
                self._cache_and_load_gif(f"ATTACK_{i}", h_path)
            self._cache_and_load_gif("IDLE", os.path.join(folder, "player_idle.gif"))
            self._cache_and_load_gif("JUMP", os.path.join(folder, "player_Jump.gif"))
        else:
            self._cache_and_load_gif("WALK", os.path.join(folder, "enemy-walk.gif"))

    def load_from_sprite_sheet(self, path):
        """Slices the player sprite sheet generated by generate_player_sheet.py"""
        sheet = pygame.image.load(path).convert_alpha()
        fw, fh = CHAR_WIDTH, CHAR_HEIGHT # 230, 230
        label_w = 250
        
        # Estructura del sheet (Etiqueta, FrameCount, AnimKey, SpriteKey)
        rows = [
            (9, "IDLE", "idle"),
            (11, "WALK", None),
            (9, "JUMP", None),
            (4, "ATTACK_0", "hit"),
            (3, "ATTACK_1", None),
            (5, "ATTACK_2", None),
            (1, None, "damage"),
            (1, None, "ground")
        ]
        
        folder = "textures/sprites"
        
        for i, (count, anim_key, sprite_key) in enumerate(rows):
            frames = []
            y = i * fh
            for j in range(count):
                x = label_w + (j * fw) + 1 # Offset 1px para evitar bordes
                sub_y = y + 1             # Offset 1px para evitar bordes
                # Slicing del frame (2 píxeles más pequeño para ignorar el marco de la sheet)
                frame = sheet.subsurface((x, sub_y, fw - 2, fh - 2)).copy()
                frames.append(frame)
            
            # Asignar a Animaciones
            if anim_key:
                self.animations[anim_key] = frames
                self.sprite_bottoms[anim_key] = get_bottom_pixel(frames[0])
                GLOBAL_ASSET_CACHE["animations"][f"player_{anim_key}"] = frames
                GLOBAL_ASSET_CACHE["bottoms"][f"player_{anim_key}"] = self.sprite_bottoms[anim_key]
            
            # Asignar a Sprites Estáticos (usando el primer frame de la fila)
            if sprite_key:
                self.sprites[sprite_key] = frames[0]
                self.sprite_bottoms[sprite_key] = get_bottom_pixel(frames[0])
                GLOBAL_ASSET_CACHE["sprites"][f"player_{sprite_key}"] = frames[0]
                GLOBAL_ASSET_CACHE["bottoms"][f"player_{sprite_key}"] = self.sprite_bottoms[sprite_key]

        # El portrait siempre lo cargamos aparte para no meterlo en el loop de la hoja si no está ahí
        port_path = os.path.join(folder, "player_portrait.png")
        if os.path.exists(port_path):
            img = pygame.image.load(port_path).convert_alpha()
            self.sprites["portrait"] = pygame.transform.smoothscale(img, (PORTRAIT_SIZE, PORTRAIT_SIZE))
            self.sprite_bottoms["portrait"] = get_bottom_pixel(self.sprites["portrait"])
            GLOBAL_ASSET_CACHE["sprites"]["player_portrait"] = self.sprites["portrait"]

    def _cache_and_load_gif(self, anim_key, path):
        """Helper para cargar GIFs usando el cache global."""
        prefix = "player" if self.is_player else "enemy"
        full_cache_key = f"{prefix}_{anim_key}"

        if full_cache_key in GLOBAL_ASSET_CACHE["animations"]:
            self.animations[anim_key] = GLOBAL_ASSET_CACHE["animations"][full_cache_key]
            self.sprite_bottoms[anim_key] = GLOBAL_ASSET_CACHE["bottoms"][full_cache_key]
            return

        if os.path.exists(path):
            frames = load_gif(path, (CHAR_WIDTH, CHAR_HEIGHT))
            if frames:
                self.animations[anim_key] = frames
                self.sprite_bottoms[anim_key] = get_bottom_pixel(frames[0])
                # Guardar en Cache
                GLOBAL_ASSET_CACHE["animations"][full_cache_key] = frames
                GLOBAL_ASSET_CACHE["bottoms"][full_cache_key] = self.sprite_bottoms[anim_key]
        else:
            print(f"ADVERTENCIA: No se encontró animación para {anim_key} en {path}")

    def update(self, player_ref=None, enemies=None, camera_x=0):
        # 1. Temporizador de Estados
        # Reset de prioridad cada frame
        self.z_priority = 0
        
        # Ajustar prioridad según estado para que el atacante siempre esté al frente
        if self.state == "ATTACK":
            self.z_priority = 50 
        elif self.state in ["STUN", "KNOCKBACK", "DOWN"]:
            self.z_priority = -50
            
        if self.state_timer > 0:
            self.state_timer -= 1
            if self.state_timer <= 0:
                # Si terminamos un Knockback pero seguimos en el aire, mantenemos el estado
                if self.state == "KNOCKBACK" and self.z > 0:
                    self.state_timer = 1 
                elif self.state == "DOWN" and not self.is_dead:
                    self.state = "IDLE"
                elif self.state != "DOWN":
                    self.state = "IDLE" if self.z <= 0 else "JUMP"

        # 1.1 Secuencia de Muerte (Blink) - Debe ejecutarse continuamente cuando está muerto en el suelo
        if self.is_dead and self.state == "DOWN" and self.state_timer <= 0:
            self.blink_timer += 1
            if self.blink_timer % 5 == 0:
                self.blink_state = not self.blink_state
            if self.blink_timer > 60: # 1 segundo parpadeando antes de desaparecer
                self.death_sequence_finished = True

        # 1.2 Temporizador de Recuperación (Bloquea nuevas acciones por unos frames)
        if self.recovery_timer > 0:
            self.recovery_timer -= 1
            
        if self.flash_timer > 0:
            self.flash_timer -= 1

        # 1.3 Actualizar Animación
        self.anim_timer += 1
        if self.anim_timer >= 5: # Cambiar frame cada 5 tics
            self.anim_timer = 0
            self.anim_frame += 1

        # 2. Gravedad (Independiente del estado)
        if self.z > 0 or self.velocity_z != 0:
            self.z += self.velocity_z
            self.velocity_z -= GRAVITY
            
            # Aterrizaje
            if self.z <= 0:
                self.z = 0
                self.velocity_z = 0
                self.jumps_done = 0
                if self.state == "DIVE":
                    self.land_dive(enemies if self.is_player else [player_ref])
                
                # Si estábamos en JUMP, volver a IDLE inmediatamente
                if self.state == "JUMP":
                    self.state = "IDLE"
                    self.jump_anim_timer = 0
                
                # Si estábamos volando por knockback, al caer entramos en DOWN
                if self.state == "KNOCKBACK":
                    self.state = "DOWN"
                    self.state_timer = DOWN_TIME
                    self.knk_vector *= 0 
                elif self.state == "STUN":
                    self.state = "IDLE"

        # 3. Aplicar Movimiento (X, Y)
        # Solo aplicamos fricción si no estamos en ataque aéreo o recibiendo knockback
        if self.state == "KNOCKBACK":
            self.world_pos += self.knk_vector
            self.knk_vector *= 0.95
        elif self.state == "DOWN":
            self.knk_vector *= 0 # No se mueve en el suelo
        else:
            # Fricción normal para caminar/idle
            is_aerial_attack = (self.state == "ATTACK" and self.z > 0)
            if not is_aerial_attack:
                self.vel *= FRICTION
            
            if self.vel.length() < 0.1: self.vel *= 0
            self.world_pos += self.vel
        
        # 3.1 Resolver Colisiones entre personajes (no se montan)
        if enemies:
            self.resolve_collisions(enemies)
        if player_ref: 
             self.resolve_collisions([player_ref])

        # 4. Límites de Pantalla (Eje Y / Profundidad)
        if self.world_pos.y < FLOOR_START_Y + 20: self.world_pos.y = FLOOR_START_Y + 20
        if self.world_pos.y > HEIGHT - 20: self.world_pos.y = HEIGHT - 20

        # 5. Lógica de Acción (Solo si no está derribado o volando)
        if self.state not in ["KNOCKBACK", "DOWN", "STUN"]:
            if self.state == "JUMP":
                self.jump_anim_timer += 1
            
            if self.is_player:
                self.handle_input()
            else:
                self.handle_ai(player_ref)
                if self.attack_cooldown > 0:
                    self.attack_cooldown -= 1


    def handle_input(self):
        if self.state == "ATTACK" and self.state_timer > 0 and self.z == 0: return

        keys = pygame.key.get_pressed()
        move_input = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: move_input.x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_input.x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: move_input.y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: move_input.y = 1

        if move_input.length() > 0:
            move_input = move_input.normalize()
            if move_input.x > 0: self.facing_right = True
            elif move_input.x < 0: self.facing_right = False
            
            target_speed = BASE_SPEED * (RUN_MULTIPLIER if self.is_running else 1)
            # Aumentamos la aceleración al correr para superar el límite de fricción
            accel_to_use = ACCEL * (1.8 if self.is_running else 1.0)
            self.vel += move_input * accel_to_use
            
            if self.vel.length() > target_speed:
                self.vel = self.vel.normalize() * target_speed
            
            if self.z == 0 and self.state != "ATTACK": self.state = "WALK"
        else:
            if self.state == "WALK": self.state = "IDLE"

    def handle_ai(self, player_ref):
        if not player_ref: return
        
        # Cambiar el offset de forma aleatoria periódicamente para un movimiento errático
        if random.random() < 0.01: # 1% cada frame
            self.target_offset = pygame.Vector2(
                random.randint(-150, 150),
                random.randint(-40, 40)
            )

        target_pos = player_ref.world_pos + self.target_offset
        dist_vec = target_pos - self.world_pos
        
        if dist_vec.length() > 20:
            move_input = dist_vec.normalize()
            if move_input.x > 0: self.facing_right = True
            elif move_input.x < 0: self.facing_right = False
            
            # Movimiento con un poco de "ruido" lateral
            noise = pygame.Vector2(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2))
            move_input = (move_input + noise).normalize()
            
            self.vel += move_input * (ACCEL * 0.4)
            max_ai_speed = BASE_SPEED * 0.75
            if self.vel.length() > max_ai_speed:
                self.vel = self.vel.normalize() * max_ai_speed
            if self.state != "ATTACK": self.state = "WALK"
        else:
            if self.state != "ATTACK": self.state = "IDLE"

        # Lógica de ataque: Más agresiva
        vec_to_player = player_ref.world_pos - self.world_pos
        # Rango de ataque un poco más amplio
        if vec_to_player.length() < 90 and abs(vec_to_player.y) < 30 and self.attack_cooldown <= 0:
            if player_ref.state != "DOWN":
                self.attack_prep_timer += 1
                if self.attack_prep_timer >= ENEMY_ATTACK_PREP:
                    self.execute_enemy_punch(player_ref)
                    self.attack_prep_timer = 0
                    self.attack_cooldown = ENEMY_COOLDOWN
        else:
            self.attack_prep_timer = 0

    def execute_enemy_punch(self, player_ref):
        if self.state != "ATTACK":
            self.anim_frame = 0
            self.anim_timer = 0
        self.state = "ATTACK"
        self.state_timer = self.attack_duration
        self.facing_right = (player_ref.world_pos.x > self.world_pos.x)
        vec = player_ref.world_pos - self.world_pos
        if vec.length() < 80 and abs(vec.y) < (HIT_RANGE_Y * HIT_RANGE_Y_MULT):
            player_ref.apply_damage(5)

    def apply_damage(self, dmg, knockback=False, knk_dir=None):
        if self.state == "DOWN" or self.is_dead: return 
        
        self.hp -= dmg
        self.flash_timer = 2 # 2 frames de flash blanco
        
        # Aseguramos que knk_dir no tenga componente Y (profundidad)
        if knk_dir:
            knk_dir = pygame.Vector2(knk_dir.x, 0)

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            # Forzar Knockback de muerte
            self.state = "KNOCKBACK"
            self.state_timer = 30
            self.velocity_z = 10
            if knk_dir:
                self.knk_vector = knk_dir * 12
            else:
                self.knk_vector = pygame.Vector2(random.choice([-1, 1]) * 6, 0)
            return

        if knockback:
            # Finisher del combo: Salto hacia atrás en el mismo plano Y
            self.state = "KNOCKBACK"
            self.state_timer = 30
            self.velocity_z = 12 # Salto hacia arriba
            if knk_dir: 
                self.knk_vector = knk_dir * 10
        else:
            # Golpe normal: desplazamiento pequeño lateral (5% de un valor de referencia o ~15px)
            self.state = "STUN"
            self.state_timer = 25
            if knk_dir:
                # Nos movemos un poco en la dirección del golpe (X)
                self.world_pos.x += knk_dir.x * 15

    def resolve_collisions(self, teammates):
        """Evita que los personajes se solapen demasiado de forma eficiente."""
        collision_dist = 40 # Radio un poco más pequeño para fluidez
        for other in teammates:
            if other is self or other.state == "DOWN": continue
            
            diff = self.world_pos - other.world_pos
            dist = diff.length()
            
            if 0.1 < dist < collision_dist:
                # Solo empujamos a 'self' para evitar procesar el par dos veces (oscilaciones)
                # El otro personaje será empujado cuando el bucle le toque a él
                push_strength = (collision_dist - dist) * 0.05
                self.world_pos += diff.normalize() * push_strength

    def land_dive(self, targets):
        self.state = "IDLE"
        if not targets: return
        for t in targets:
            if not t or t.state == "DOWN": continue
            d = (t.world_pos - self.world_pos).length()
            if d < 100:
                knk_dir = t.world_pos - self.world_pos
                if knk_dir.length() > 0: knk_dir = knk_dir.normalize()
                else: knk_dir = pygame.Vector2(1, 0)
                t.apply_damage(15, knockback=True, knk_dir=knk_dir)

    def draw(self, screen, camera_x, scale=1.0):
        # 1. Ajustar posición local
        local_x = (self.world_pos.x - camera_x)
        
        # 2. Determinar el sprite a usar
        sprite_key = "idle"
        if self.state == "ATTACK": sprite_key = "ATTACK"
        if self.state == "JUMP" and "JUMP" in self.animations: sprite_key = "JUMP"
        if self.state in ["STUN", "KNOCKBACK"]: sprite_key = "damage"
        if self.state == "DOWN": sprite_key = "ground"
        if self.state == "WALK" and "WALK" in self.animations: sprite_key = "WALK"
        
        img = None
        if sprite_key == "WALK" and "WALK" in self.animations:
            frames = self.animations["WALK"]
            img = frames[self.anim_frame % len(frames)]
        elif sprite_key == "ATTACK":
            anim_key = f"ATTACK_{self.combo_index}"
            if anim_key in self.animations:
                frames = self.animations[anim_key]
                idx = min(self.anim_frame, len(frames) - 1)
                img = frames[idx]
            else:
                img = self.sprites.get("hit", self.sprites["idle"])
        elif sprite_key == "idle" and "IDLE" in self.animations:
            frames = self.animations["IDLE"]
            img = frames[self.anim_frame % len(frames)]
        elif sprite_key == "JUMP" and "JUMP" in self.animations:
            frames = self.animations["JUMP"]
            # Sincronización ajustada: 9 frames * 5.5 tics = 49.5 tics (salto total ~52)
            # Esto asegura que llegamos al último frame justo antes de tocar suelo
            idx = min(int(self.jump_anim_timer / 5.5), len(frames) - 1)
            img = frames[idx]
        else:
            img = self.sprites.get(sprite_key, self.sprites["idle"])
            
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
            
        # 3. Aplicar Escalado de Perspectiva
        original_w, original_h = img.get_size()
        
        # ENEMIGOS UN 5% MÁS PEQUEÑOS (Ajustado: +10% desde el 0.85 anterior)
        final_scale = scale
        if not self.is_player:
            final_scale *= 0.95
            
        new_w = int(original_w * final_scale)
        new_h = int(original_h * final_scale)
        if new_w <= 0 or new_h <= 0: return
        
        img = pygame.transform.smoothscale(img, (new_w, new_h))
            
        # 3.1 Efecto de Flash Blanco (Silhouette)
        if self.flash_timer > 0:
            fill_surf = img.copy()
            fill_surf.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
            img.blit(fill_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # 4. Dibujar Personaje
        char_x = local_x - new_w // 2
        
        # Buscamos el punto más bajo del sprite para que coincida con world_pos.y
        # Como el sprite está escalado, el bottom_y también debe escalarse
        bottom_y_original = self.sprite_bottoms.get(sprite_key, original_h)
        bottom_y = int(bottom_y_original * final_scale)

        if self.state == "DOWN":
            if not self.blink_state: return
            # En el suelo usamos el sprite "ground" sin rotar
            char_y = self.world_pos.y - new_h
            screen.blit(img, (char_x, char_y))
        else:
            # Los pies (bottom_y) deben estar en world_pos.y - (z * scale)
            char_y = self.world_pos.y - (self.z * scale) - bottom_y
            screen.blit(img, (char_x, char_y))
            
            # La sombra se queda en el suelo (world_pos.y) alineada con los pies
            # Si queremos que la sombra se mueva con el sprite en el aire, ya está en world_pos.y
