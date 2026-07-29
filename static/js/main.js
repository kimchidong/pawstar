/**
 * Paw Star - Interactive Main JS
 * "반려동물도 스타가 될 수 있다."
 */

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

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

    // 동물 종류 선택 변경 이벤트
    const petTypeSelect = document.getElementById('petTypeSelect');
    if (petTypeSelect) {
        petTypeSelect.addEventListener('change', (e) => {
            const petType = e.target.value;
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('pet_type', petType);
            window.location.href = currentUrl.toString();
        });
    }

    // 모달 제어 (/upload 전용 페이지 전환 적용)
    const modalBackdrop = document.getElementById('uploadModal');
    const openBtn = document.getElementById('btnOpenModal');
    const closeBtn = document.getElementById('btnCloseModal');

    if (openBtn) {
        openBtn.addEventListener('click', (e) => {
            if (!modalBackdrop) {
                window.location.href = '/upload';
            } else {
                modalBackdrop.classList.add('show');
            }
        });
    }
    if (closeBtn && modalBackdrop) {
        closeBtn.addEventListener('click', () => modalBackdrop.classList.remove('show'));
    }

    // 상세 모달 닫기 제어
    const detailModal = document.getElementById('postDetailModal');
    const closeDetailBtn = document.getElementById('btnCloseDetailModal');
    if (closeDetailBtn && detailModal) {
        closeDetailBtn.addEventListener('click', () => detailModal.classList.remove('show'));
    }
    if (detailModal) {
        detailModal.addEventListener('click', (e) => {
            if (e.target === detailModal) detailModal.classList.remove('show');
        });
    }

    // 프로필 수정 모달 제어 (plamodelshop 회원관리 로직과 동일)
    const profileModal = document.getElementById('profileEditModal');
    const btnOpenProfile = document.getElementById('btnOpenProfileModal');
    const btnCloseProfile = document.getElementById('btnCloseProfileModal');
    if (btnOpenProfile && profileModal) {
        btnOpenProfile.addEventListener('click', () => profileModal.classList.add('show'));
    }
    if (btnCloseProfile && profileModal) {
        btnCloseProfile.addEventListener('click', () => profileModal.classList.remove('show'));
    }

    // 프로필 정보 수정 AJAX 폼 제출
    const profileEditForm = document.getElementById('profileEditForm');
    if (profileEditForm) {
        profileEditForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const updateData = {
                user_id: 'user1',
                nickname: document.getElementById('editNickname').value,
                profile_img: document.getElementById('editProfileImg').value,
                bio: document.getElementById('editBio').value
            };

            try {
                const response = await fetch('/api/profile/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updateData)
                });
                const res = await response.json();
                if (res.success) {
                    showToast('✨ 프로필 정보가 성공적으로 수정되었습니다!');
                    profileModal.classList.remove('show');
                    
                    // DOM 실시간 갱신
                    const currentNickname = document.getElementById('currentNickname');
                    if (currentNickname) currentNickname.textContent = res.data.nickname;
                    const currentBio = document.getElementById('currentBio');
                    if (currentBio) currentBio.textContent = res.data.bio;
                    const currentProfileImg = document.getElementById('currentProfileImg');
                    if (currentProfileImg) currentProfileImg.src = res.data.profile_img;
                } else {
                    alert(res.message);
                }
            } catch (err) {
                console.error(err);
                alert('프로필 수정 중 오류가 발생했습니다.');
            }
        });
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

            // 모달 내부 수치 동기화 갱신
            const detailScore = document.getElementById('detailScoreNum');
            if (detailScore) detailScore.textContent = data.new_score.toLocaleString();
            const dView = document.getElementById('detailViewCount');
            if (dView) dView.textContent = data.view_count;
            const dLike = document.getElementById('detailLikeCount');
            if (dLike) dLike.textContent = data.like_count;
            const dComment = document.getElementById('detailCommentCount');
            if (dComment) dComment.textContent = data.comment_count;
            const dShare = document.getElementById('detailShareCount');
            if (dShare) dShare.textContent = data.share_count;

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

/**
 * 게시물 상세 레이어 팝업 모달 띄우기
 */
function openDetailModal(post) {
    const modal = document.getElementById('postDetailModal');
    if (!modal || !post) return;

    // 데이터 채우기
    const imgEl = document.getElementById('detailImg');
    if (imgEl) imgEl.src = post.media_url || '';

    const authorImgEl = document.getElementById('detailAuthorImg');
    if (authorImgEl) authorImgEl.src = post.user_profile || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80';

    const nicknameEl = document.getElementById('detailAuthorNickname');
    if (nicknameEl) nicknameEl.textContent = post.user_nickname || '집사';

    const petTagEl = document.getElementById('detailPetTag');
    const nameStr = (post.pet_name && post.pet_name !== '강아지' && post.pet_name !== '우리 강아지' && post.pet_name !== '아이 이름') ? ` ${post.pet_name}` : '';
    if (petTagEl) petTagEl.textContent = `${post.pet_type || '🐕 강아지'}${nameStr}`;

    const scoreNumEl = document.getElementById('detailScoreNum');
    if (scoreNumEl) scoreNumEl.textContent = Number(post.score || 0).toLocaleString();

    const titleEl = document.getElementById('detailTitle');
    if (titleEl) titleEl.textContent = post.title || '';

    const contentEl = document.getElementById('detailContent');
    if (contentEl) contentEl.textContent = post.content || '';

    const createdAtEl = document.getElementById('detailCreatedAt');
    if (createdAtEl) createdAtEl.textContent = `등록일: ${post.created_at || '2026-07-28'}`;

    const viewCountEl = document.getElementById('detailViewCount');
    if (viewCountEl) viewCountEl.textContent = post.view_count || 0;

    const likeCountEl = document.getElementById('detailLikeCount');
    if (likeCountEl) likeCountEl.textContent = post.like_count || 0;

    const commentCountEl = document.getElementById('detailCommentCount');
    if (commentCountEl) commentCountEl.textContent = post.comment_count || 0;

    const shareCountEl = document.getElementById('detailShareCount');
    if (shareCountEl) shareCountEl.textContent = post.share_count || 0;

    // 현재 열린 게시물 ID 저장 및 댓글 로드
    window.currentDetailPostId = post.post_id;
    loadComments(post.post_id);

    // 랭킹 배지 채우기
    const badgeEl = document.getElementById('detailRankBadge');
    if (badgeEl) {
        if (post.rank_candidate === 1) {
            badgeEl.innerHTML = '<div class="rank-ribbon rank-1"><i class="fa-solid fa-medal"></i> 1위 후보</div>';
        } else if (post.rank_candidate === 2) {
            badgeEl.innerHTML = '<div class="rank-ribbon rank-2"><i class="fa-solid fa-medal"></i> 2위 후보</div>';
        } else if (post.rank_candidate === 3) {
            badgeEl.innerHTML = '<div class="rank-ribbon rank-3"><i class="fa-solid fa-medal"></i> 3위 후보</div>';
        } else {
            badgeEl.innerHTML = '';
        }
    }

    // 모달 내부 버튼 이벤트 바인딩
    const btnView = document.getElementById('detailBtnView');
    const btnLike = document.getElementById('detailBtnLike');
    const btnComment = document.getElementById('detailBtnComment');
    const btnShare = document.getElementById('detailBtnShare');

    if (btnView) btnView.onclick = () => triggerEvent(post.post_id, 'view');
    if (btnLike) btnLike.onclick = () => triggerEvent(post.post_id, 'like');
    if (btnComment) btnComment.onclick = () => triggerEvent(post.post_id, 'comment');
    if (btnShare) btnShare.onclick = () => triggerEvent(post.post_id, 'share');

    modal.classList.add('show');
}

function closeDetailModal() {
    const modal = document.getElementById('postDetailModal');
    if (modal) modal.classList.remove('show');
}

/**
 * 댓글 목록 로드 및 렌더링
 */
function loadComments(postId) {
    fetch(`/api/comments/${postId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderDetailComments(data.comments);
            }
        })
        .catch(err => console.error('댓글 로드 실패:', err));
}

function renderDetailComments(comments) {
    const listEl = document.getElementById('detailCommentList');
    const headerCountEl = document.getElementById('detailCommentHeaderCount');
    if (headerCountEl) headerCountEl.textContent = `(${comments ? comments.length : 0})`;
    
    if (!listEl) return;
    if (!comments || comments.length === 0) {
        listEl.innerHTML = '<div style="text-align: center; color: var(--text-muted); font-size: 0.8rem; padding: 0.75rem 0;">첫 한줄 댓글의 주인공이 되어보세요! 💬</div>';
        return;
    }
    
    listEl.innerHTML = comments.map(c => `
        <div style="background: #f8fafc; border: 1px solid var(--border-light); border-radius: 12px; padding: 0.5rem 0.75rem; font-size: 0.82rem; display: flex; flex-direction: column; gap: 0.2rem;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 0.35rem; font-weight: 800; color: var(--text-primary);">
                    <img src="${c.user_profile || '/static/image/profile/default_profile.png'}" style="width: 18px; height: 18px; border-radius: 50%; object-fit: cover;">
                    <span>${escapeHtml(c.user_nickname || '집사')}</span>
                </div>
                <span style="font-size: 0.72rem; color: var(--text-muted);">${c.created_at || ''}</span>
            </div>
            <div style="color: var(--text-secondary); font-weight: 500; word-break: break-all; padding-left: 1.4rem;">
                ${escapeHtml(c.content)}
            </div>
        </div>
    `).join('');
}

function submitDetailComment() {
    const inputEl = document.getElementById('detailCommentInput');
    if (!inputEl || !window.currentDetailPostId) return;
    const content = inputEl.value.trim();
    if (!content) {
        showToast('댓글 내용을 입력해주세요.', 'warning');
        return;
    }
    
    fetch(`/api/comments/${window.currentDetailPostId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            inputEl.value = '';
            showToast('한줄 댓글 작성 완료! (+10점 반영)', 'success');
            loadComments(window.currentDetailPostId);
            
            if (data.event_res) {
                const scoreEl = document.getElementById('detailScoreNum');
                const commentEl = document.getElementById('detailCommentCount');
                if (scoreEl) scoreEl.textContent = Number(data.event_res.new_score || 0).toLocaleString();
                if (commentEl) commentEl.textContent = data.event_res.comment_count || 0;
                
                const card = document.getElementById(`post-card-${window.currentDetailPostId}`);
                if (card) {
                    const cardScore = card.querySelector('.score-num');
                    const cardComment = card.querySelector('.comment-count');
                    if (cardScore) cardScore.textContent = Number(data.event_res.new_score || 0).toLocaleString();
                    if (cardComment) cardComment.textContent = data.event_res.comment_count || 0;
                }
            }
        } else {
            showToast(data.message || '댓글 작성 실패', 'error');
        }
    })
    .catch(err => {
        console.error('댓글 작성 오류:', err);
        showToast('댓글 등록 중 오류가 발생했습니다.', 'error');
    });
}
