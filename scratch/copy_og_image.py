import shutil
import os

src = r"C:\Users\cellh\.gemini\antigravity\brain\0e8d657c-a41c-437f-a7ea-babdaff93ca8\pawstar_og_banner_1787824284042.jpg"
dst_dir = r"d:\dev\workspace1\pawstar\static\image\app"
os.makedirs(dst_dir, exist_ok=True)
dst = os.path.join(dst_dir, "og_image.png")

shutil.copy2(src, dst)
print(f"Successfully copied OG image from {src} to {dst}")
