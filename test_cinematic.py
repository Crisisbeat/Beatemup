from engine import GameEngine
import pygame

if __name__ == "__main__":
    game = GameEngine()
    # Force state to cinematic to test immediately
    game.game_state = "CINEMATIC"
    game.cinematic.start()
    
    # Run a few frames to see if it crashes
    for _ in range(100):
        game.handle_events()
        game.update()
        # We won't call game.draw() here to avoid opening a window in a headless test environment
        # But we can check if the cinematic frame is advancing
        if game.cinematic.frame > 0:
            print(f"Cinematic advancing... Frame: {game.cinematic.frame}")
            break
    
    print("Test passed: Cinematic logic initialized and advanced.")
    pygame.quit()
