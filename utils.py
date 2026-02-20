import pygame

def draw_gradient_rect(screen, rect, color1, color2, horizontal=False):
    """Dibuja un degradado dentro de un rect especificado."""
    target_rect = pygame.Rect(rect)
    if not horizontal:
        column = pygame.Surface((1, target_rect.height))
        for y in range(target_rect.height):
            r = color1[0] + (color2[0] - color1[0]) * y / target_rect.height
            g = color1[1] + (color2[1] - color1[1]) * y / target_rect.height
            b = color1[2] + (color2[2] - color1[2]) * y / target_rect.height
            pygame.draw.line(column, (int(r), int(g), int(b)), (0, y), (0, y))
        screen.blit(pygame.transform.scale(column, (target_rect.width, target_rect.height)), target_rect)
    else:
        row = pygame.Surface((target_rect.width, 1))
        for x in range(target_rect.width):
            r = color1[0] + (color2[0] - color1[0]) * x / target_rect.width
            g = color1[1] + (color2[1] - color1[1]) * x / target_rect.width
            b = color1[2] + (color2[2] - color1[2]) * x / target_rect.width
            pygame.draw.line(row, (int(r), int(g), int(b)), (x, 0), (x, 0))
        screen.blit(pygame.transform.scale(row, (target_rect.width, target_rect.height)), target_rect)

def get_bottom_pixel(surface):
    """Retorna la coordenada Y del píxel no transparente más bajo."""
    if not surface:
        return 0
    width, height = surface.get_size()
    mask = pygame.mask.from_surface(surface)
    for y in range(height - 1, -1, -1):
        for x in range(width):
            if mask.get_at((x, y)):
                return y + 1 
    return height

def load_gif(filename, scale=None):
    """Carga un GIF y devuelve una lista de cuadros (surfaces) y duraciones."""
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: El modulo 'Pillow' no esta instalado. Ejecuta 'pip install pillow'.")
        # Retornar una superficie vacía para evitar crash total si falla en tiempo de ejecucion
        surf = pygame.Surface((10, 10))
        surf.fill((255, 0, 255))
        return [surf]

    import pygame

    try:
        pil_img = Image.open(filename)
    except Exception as e:
        print(f"Error al abrir GIF {filename}: {e}")
        surf = pygame.Surface((10, 10))
        surf.fill((255, 0, 255))
        return [surf]

    frames = []
    
    try:
        while True:
            # Convertir frame de PIL a Pygame
            frame = pil_img.convert("RGBA")
            data = frame.tobytes("raw", "RGBA")
            pygame_surface = pygame.image.fromstring(data, frame.size, "RGBA")
            
            if scale:
                pygame_surface = pygame.transform.smoothscale(pygame_surface, scale)
            
            frames.append(pygame_surface)
            pil_img.seek(pil_img.tell() + 1)
    except EOFError:
        pass
        
    return frames

def render_gradient_text(font, text, color_top, color_bottom, outline_color=(0, 0, 0), outline_width=3):
    """Renderiza texto con un degradado vertical y un borde."""
    # Renderizar el texto base en blanco para usarlo como máscara
    text_surf = font.render(text, True, (255, 255, 255)).convert_alpha()
    w, h = text_surf.get_size()
    
    # Crear superficie de degradado
    grad_surf = pygame.Surface((w, h)).convert_alpha()
    for y in range(h):
        r = color_top[0] + (color_bottom[0] - color_top[0]) * y / h
        g = color_top[1] + (color_bottom[1] - color_top[1]) * y / h
        b = color_top[2] + (color_bottom[2] - color_top[2]) * y / h
        pygame.draw.line(grad_surf, (int(r), int(g), int(b), 255), (0, y), (w, y))
        
    # Multiplicar el degradado por el texto blanco (conserva el alpha del texto)
    text_surf.blit(grad_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    # Crear superficie final para el borde + texto
    final_surf = pygame.Surface((w + outline_width * 2, h + outline_width*2), pygame.SRCALPHA)
    
    # Renderizar borde (múltiples blits del texto en color borde)
    outline_text = font.render(text, True, outline_color).convert_alpha()
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx*dx + dy*dy <= outline_width*outline_width:
                final_surf.blit(outline_text, (dx + outline_width, dy + outline_width))
                
    # Blitear el texto degradado encima
    final_surf.blit(text_surf, (outline_width, outline_width))
    return final_surf

def blur_surface(surface, amount=4):
    """Simula un desenfoque escalando la superficie hacia abajo y hacia arriba."""
    if amount <= 1: return surface
    w, h = surface.get_size()
    small_surf = pygame.transform.smoothscale(surface, (w // amount, h // amount))
    return pygame.transform.smoothscale(small_surf, (w, h))
