"# pawstar" 

To github.com:kimchidong/pawstar.git
 ! [remote rejected] dev -> dev (push declined due to repository rule violations)
error: failed to push some refs to 'github.com:kimchidong/pawstar.git'


# 1. 과거 보안키 커밋 기록을 지우고 현재 깨끗한 코드로 새 커밋 작성
git checkout --orphan clean_branch
git add .
git commit -m "Fix: Security update and PawStar enhancements"

# 2. 기존 브랜치를 정리하고 main으로 지정
git branch -D main
git branch -m main

# 3. GitHub로 강제 푸시 (Secret이 완전히 제거된 깨끗한 커밋 푸시)
git push -f origin main

--

