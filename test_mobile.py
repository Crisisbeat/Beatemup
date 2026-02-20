from engine import GameEngine

if __name__ == "__main__":
    game = GameEngine()
    # Forzamos el modo móvil para ver los botones en PC
    game.mobile_mode = True
    game.run()
