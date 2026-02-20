from PIL import Image, ImageDraw
import os

def create_hit_gif(output_path, color):
    # Regresamos a 3 frames para que coincida con el ritmo original pero con mejor tiempo
    frames = []
    width, height = 230, 230
    
    # Frame 1: Preparación
    f1 = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d1 = ImageDraw.Draw(f1)
    d1.rectangle([30, 50, 160, 180], fill=color, outline="black", width=4)
    d1.rectangle([140, 80, 170, 110], fill="white", outline="black")
    
    # Frame 2: Impacto
    f2 = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(f2)
    d2.rectangle([70, 50, 200, 180], fill=color, outline="black", width=4)
    d2.rectangle([180, 90, 225, 120], fill="white", outline="black")
    d2.line([210, 70, 230, 50], fill="yellow", width=3)
    d2.line([210, 130, 230, 150], fill="yellow", width=3)
    
    # Frame 3: Recuperación / Pose final
    f3 = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(f3)
    d3.rectangle([50, 50, 180, 180], fill=color, outline="black", width=4)
    
    frames = [f1, f2, f3]
    
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0,
        disposal=2
    )

if __name__ == "__main__":
    folder = "textures/sprites"
    create_hit_gif(os.path.join(folder, "player_hit.gif"), (50, 100, 255))
    print("GIF de 3 frames regenerado.")
