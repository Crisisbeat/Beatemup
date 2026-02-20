from PIL import Image
import os

path = r"c:\Users\user\Desktop\Melon\New folder\Beatemup\textures\sprites\player_Jump.gif"
if os.path.exists(path):
    img = Image.open(path)
    frames = 0
    try:
        while True:
            frames += 1
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    print(f"Frames: {frames}")
else:
    print("File not found")
