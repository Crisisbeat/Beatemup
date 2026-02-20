from PIL import Image
import os

folder = r"c:\Users\user\Desktop\Melon\New folder\Beatemup\textures\sprites"
files = ["player_idle.gif", "player_run.gif", "player_Jump.gif", "player_hit.gif", "player_hit2.gif", "player_hit3.gif"]

for f in files:
    path = os.path.join(folder, f)
    if os.path.exists(path):
        img = Image.open(path)
        frames = 0
        try:
            while True:
                frames += 1
                img.seek(img.tell() + 1)
        except EOFError:
            pass
        print(f"{f}: {frames}")
    else:
        print(f"{f}: Not found")
