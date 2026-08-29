import os
import shutil

src = r"C:\Users\cellh\.gemini\antigravity\brain\492b93fa-08ef-4ecf-94c8-14f1a4d9b30d\notice_open_poster_kr_1787971065132.jpg"
dest_dir = r"d:\dev\workspace1\pawstar\static\image\poster"
dest = os.path.join(dest_dir, "notice_open_poster.jpg")

os.makedirs(dest_dir, exist_ok=True)
shutil.copy2(src, dest)

print(f"[SUCCESS] 한글 포스터 이미지를 {dest} 에 성공적으로 저장했습니다!")
