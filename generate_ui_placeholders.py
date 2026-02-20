import pygame
import os
import math

# Initialize Pygame for drawing
pygame.init()

def draw_hexagon(surface, color, center, radius, width=0):
    points = []
    for i in range(6):
        angle_deg = 60 * i - 30 # Rotate slightly to match reference
        angle_rad = math.radians(angle_deg)
        points.append((
            center[0] + radius * math.cos(angle_rad),
            center[1] + radius * math.sin(angle_rad)
        ))
    pygame.draw.polygon(surface, color, points, width)
    return points

def draw_slanted_rect(surface, color, rect, slant=20, width=0):
    x, y, w, h = rect
    points = [
        (x + slant, y),
        (x + w, y),
        (x + w - slant, y + h),
        (x, y + h)
    ]
    pygame.draw.polygon(surface, color, points, width)
    return points

def create_ui_assets():
    ui_dir = r"c:\Users\user\Desktop\Melon\New folder\Beatemup\textures\ui"
    if not os.path.exists(ui_dir):
        os.makedirs(ui_dir)

    # Frame Dimensions
    W, H = 450, 120
    
    # 1. health_frame.png
    frame = pygame.Surface((W, H), pygame.SRCALPHA)
    
    # Colors
    C_BORDER = (90, 40, 20) # Metallic brown/orange
    C_BORDER_LIGHT = (180, 80, 40)
    C_BG = (20, 25, 30, 230) # Dark glassy background
    
    # Draw Background for bar area first
    draw_slanted_rect(frame, C_BG, (100, 30, 320, 45), slant=15)
    
    # Draw Hexagon Border
    draw_hexagon(frame, C_BORDER, (60, 60), 55) # Outer
    draw_hexagon(frame, C_BORDER_LIGHT, (60, 60), 55, width=3) # Highlight
    draw_hexagon(frame, (30, 40, 45, 200), (60, 60), 48) # Glassy center
    
    # Draw Main Bar Border (Slanted)
    draw_slanted_rect(frame, C_BORDER, (110, 35, 280, 25), slant=10, width=4)
    draw_slanted_rect(frame, C_BORDER_LIGHT, (110, 35, 280, 25), slant=10, width=1)
    
    # Draw Smaller Sub-Bar below (for energy/special)
    draw_slanted_rect(frame, C_BG, (110, 65, 180, 20), slant=8)
    draw_slanted_rect(frame, C_BORDER, (110, 65, 180, 20), slant=8, width=3)

    pygame.image.save(frame, os.path.join(ui_dir, "health_frame.png"))
    print("Created health_frame.png")

    # 2. health_fill_player.png (Main HP gradient)
    # We create a 200px wide fill (standard size)
    fill_w, fill_h = 280, 25
    fill_p = pygame.Surface((fill_w, fill_h), pygame.SRCALPHA)
    
    # Draw gradient slanted
    for x in range(fill_w):
        # Red to Orange to Yellow
        if x < fill_w // 2:
            # Red to Orange
            t = x / (fill_w // 2)
            color = (255, int(100 * t), 0)
        else:
            # Orange to Yellow
            t = (x - (fill_w // 2)) / (fill_w // 2)
            color = (255, 100 + int(155 * t), 0)
            
        # Draw vertical line on slanted rect logic
        # For simplicity, we draw it on a rect and we'll slant it in the engine or here
        pygame.draw.line(fill_p, color, (x, 0), (x, fill_h))
    
    # Add glossy top
    glow = pygame.Surface((fill_w, fill_h // 2), pygame.SRCALPHA)
    glow.fill((255, 255, 255, 80))
    fill_p.blit(glow, (0, 0))

    pygame.image.save(fill_p, os.path.join(ui_dir, "health_fill_player.png"))
    print("Created health_fill_player.png")

    # 3. health_fill_enemy.png (Pink/Red to Purple gradient)
    fill_e = pygame.Surface((fill_w, fill_h), pygame.SRCALPHA)
    for x in range(fill_w):
        t = x / fill_w
        color = (200, 20, 100 + int(100 * t)) # Pinkish to Purple
        pygame.draw.line(fill_e, color, (x, 0), (x, fill_h))
    
    fill_e.blit(glow, (0, 0))
    pygame.image.save(fill_e, os.path.join(ui_dir, "health_fill_enemy.png"))
    print("Created health_fill_enemy.png")

if __name__ == "__main__":
    create_ui_assets()
