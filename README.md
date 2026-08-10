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

# 수상 당선 배치
0 0 1 * * /usr/bin/python3 /d/dev/workspace1/pawstar/monthly_award_batch.py >> /d/dev/workspace1/pawstar/batch.log 2>&1


# 데이터 초기화
-- 1. 외래키 제약조건 잠시 해제
SET FOREIGN_KEY_CHECKS = 0;
-- 2. 해당 테이블 데이터 전체 삭제 및 AUTO_INCREMENT 초기화
TRUNCATE TABLE pst_contest_cmt;
TRUNCATE TABLE pst_contest_like;
TRUNCATE TABLE pst_contest_vw;
TRUNCATE TABLE pst_contest_share;
TRUNCATE TABLE pst_contest_award; -- (선택) 수상 기록 테이블도 초기화가 필요한 경우 포함
TRUNCATE TABLE pst_contest_round;
TRUNCATE TABLE pst_user;
-- 3. 외래키 제약조건 재설정
SET FOREIGN_KEY_CHECKS = 1;

