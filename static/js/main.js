/**
 * Paw Star - Interactive Main JS
 * "반려동물도 스타가 될 수 있다."
 */

document.addEventListener('DOMContentLoaded', () => {
    initEventHandlers();
});

function initEventHandlers() {
    // 회차 선택 변경 이벤트
    const contestSelect = document.getElementById('contestSelect');
    if (contestSelect) {
        contestSelect.addEventListener('change', (e) => {
            const contestId = e.target.value;
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('contest_id', contestId);
            window.location.href = currentUrl.toString();
        });
    }

    // 모달 제어
    const modalBackdrop = document.getElementById('uploadModal');
    const openBtn = document.getElementById('btnOpenModal');
    const closeBtn = document.getElementById('btnCloseModal');

    if (openBtn && modalBackdrop) {
        openBtn.addEventListener('click', () => modalBackdrop.classList.add('show'));
    }
    if (closeBtn && modalBackdrop) {
        closeBtn.addEventListener('click', () => modalBackdrop.classList.remove('show'));
    }

    // 신규 등록 폼 제출
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = {
                contest_id: document.getElementById('postContestId').value,
                pet_name: document.getElementById('petName').value,
                pet_type: document.getElementById('petType').value,
                title: document.getElementById('postTitle').value,
                content: document.getElementById('postContent').value,
                media_url: document.getElementById('mediaUrl').value
            };

            try {
                const response = await fetch('/api/post/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                const res = await response.json();
                if (res.success) {
                    showToast('🎉 자랑 게시물이 성공적으로 등록되었습니다!');
                    modalBackdrop.classList.remove('show');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    alert(res.message);
                }
            } catch (err) {
                console.error(err);
                alert('게시물 등록 중 오류가 발생했습니다.');
            }
        });
    }
}

/**
 * 실시간 게시물 점수 증감 이벤트 처리
 * @param {number} postId 
 * @param {string} eventType ('view', 'like', 'comment', 'share')
 */
async function triggerEvent(postId, eventType) {
    try {
        const response = await fetch('/api/post/event', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ post_id: postId, event_type: eventType })
        });
        const res = await response.json();

        if (res.success) {
            const data = res.data;
            
            // UI Score 수치 갱신 & 카운터 갱신
            const card = document.getElementById(`post-card-${postId}`);
            if (card) {
                const scoreDisplay = card.querySelector('.score-num');
                if (scoreDisplay) {
                    scoreDisplay.textContent = data.new_score.toLocaleString();
                    
                    // 애니메이션 효과
                    scoreDisplay.style.color = '#f43f5e';
                    scoreDisplay.style.transform = 'scale(1.2)';
                    setTimeout(() => {
                        scoreDisplay.style.color = '';
                        scoreDisplay.style.transform = 'scale(1)';
                    }, 400);
                }

                // 각 이벤트별 수치 갱신
                const viewNum = card.querySelector('.view-count');
                const likeNum = card.querySelector('.like-count');
                const commentNum = card.querySelector('.comment-count');
                const shareNum = card.querySelector('.share-count');

                if (viewNum) viewNum.textContent = data.view_count;
                if (likeNum) likeNum.textContent = data.like_count;
                if (commentNum) commentNum.textContent = data.comment_count;
                if (shareNum) shareNum.textContent = data.share_count;
            }

            const messages = {
                'view': '조회수 +1 (Score +1)',
                'like': '❤️ 좋아요! (Score +5)',
                'comment': '💬 댓글 작성 (Score +10)',
                'share': '🚀 공유 유입 (Score +20)'
            };
            showToast(`✨ ${messages[eventType]} 점수가 반영되었습니다!`);
        }
    } catch (err) {
        console.error(err);
    }
}

/**
 * 회차 종료 & 수상자 자동 선정 배치 실행
 * @param {number} contestId 
 */
async function runAwardBatch(contestId) {
    if (!confirm(`제${contestId}회 콘테스트를 종료하고 1~3위 및 급상승 루키스타 수상자를 선정하시겠습니까?`)) {
        return;
    }

    try {
        const response = await fetch('/api/admin/close-contest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contest_id: contestId })
        });
        const res = await response.json();
        if (res.success) {
            showToast('🏆 콘테스트 회차 종료 및 수상자 선정 배치가 완료되었습니다!');
            setTimeout(() => {
                window.location.href = `/hall-of-fame?contest_id=${contestId}`;
            }, 1200);
        } else {
            alert(res.message);
        }
    } catch (err) {
        console.error(err);
        alert('배치 실행 중 오류가 발생했습니다.');
    }
}

/** 토스트 메시지 팝업 */
function showToast(message) {
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `<i class="fa-solid fa-sparkles"></i> <span>${message}</span>`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        toast.style.transition = 'all 0.4s ease';
        setTimeout(() => toast.remove(), 400);
    }, 2500);
}
