/* 
 * Paw Star - Mobile Exclusive JavaScript (m_main.js)
 * 모든 모바일 관련 작업 파일은 'm'으로 시작하는 규칙 준수
 */

document.addEventListener('DOMContentLoaded', function() {
    // 1. 모바일 자랑하기 (/m/upload 전용 페이지 전환 적용)
    const mBtnUploadNav = document.getElementById('mBtnUploadNav');
    const mUploadModal = document.getElementById('mUploadModal');
    const mBtnCloseUpload = document.getElementById('mBtnCloseUpload');

    if (mBtnUploadNav) {
        mBtnUploadNav.addEventListener('click', function(e) {
            if (!mUploadModal) {
                window.location.href = '/m/upload';
            } else {
                e.preventDefault();
                mUploadModal.classList.add('active');
            }
        });
    }

    // 2. 모바일 신규 자랑 게시물 등록
    const mUploadForm = document.getElementById('mUploadForm');
    if (mUploadForm) {
        mUploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const contest_id = document.getElementById('mPostContestId').value;
            const pet_name = document.getElementById('mPetName').value.trim();
            const pet_type = document.getElementById('mPetType').value;
            const title = document.getElementById('mPostTitle').value.trim();
            const media_url = document.getElementById('mMediaUrl').value.trim();
            const content = document.getElementById('mPostContent').value.trim();

            if (!title) {
                alert('자랑 제목을 입력해 주세요.');
                return;
            }

            fetch('/api/post/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contest_id: contest_id,
                    user_id: 'user1',
                    pet_name: pet_name,
                    pet_type: pet_type,
                    title: title,
                    media_url: media_url,
                    content: content
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert('🎉 펫 자랑 게시물이 정상 출전되었습니다!');
                    location.reload();
                } else {
                    alert('출전 실패: ' + (data.message || '오류 발생'));
                }
            })
            .catch(err => {
                console.error(err);
                alert('등록 중 오류가 발생했습니다.');
            });
        });
    }
});

// 3. 모바일 전용 게시물 상세보기 모달 open
function openMobileDetailModal(postData) {
    const detailModal = document.getElementById('mDetailModal');
    if (!detailModal) return;

    document.getElementById('mDetailImg').src = postData.media_url || '';
    document.getElementById('mDetailAuthorImg').src = postData.user_profile || '';
    document.getElementById('mDetailAuthorNickname').textContent = postData.user_nickname || '집사';
    document.getElementById('mDetailPetTag').textContent = `${postData.pet_type || ''} ${postData.pet_name || ''}`;
    document.getElementById('mDetailScoreNum').textContent = (postData.score || 0).toLocaleString();
    document.getElementById('mDetailTitle').textContent = postData.title || '';
    document.getElementById('mDetailContent').textContent = postData.content || '';

    detailModal.classList.add('active');
}

function closeMobileDetailModal() {
    const detailModal = document.getElementById('mDetailModal');
    if (detailModal) {
        detailModal.classList.remove('active');
    }
}
