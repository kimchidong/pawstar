/* 
 * Paw Star - Mobile Exclusive JavaScript (m_main.js)
 * 모든 모바일 관련 작업 파일은 'm'으로 시작하는 규칙 준수
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

    const mPopupSrc = postData.IMAGE_PATH || postData.image_path || postData.media_url || 
        ((postData.file_path && postData.list_file_name) ? (postData.file_path.endsWith('/') ? postData.file_path : postData.file_path + '/') + postData.list_file_name : '');
    document.getElementById('mDetailImg').src = mPopupSrc;
    document.getElementById('mDetailAuthorImg').src = postData.PROFILE_URL || postData.user_profile || '/static/image/profile/default_profile.png';
    document.getElementById('mDetailAuthorNickname').textContent = postData.NK_NM || postData.user_nickname || '집사';
    
    const mPetTagEl = document.getElementById('mDetailPetTag');
    if (mPetTagEl) {
        const mKindNm = postData.KIND_NM || postData.pet_type || '🐕 강아지';
        const mPetNm = postData.PET_NM || postData.pet_name || '';
        if (mPetNm) {
            mPetTagEl.innerHTML = `<span style="color: #e11d48; font-weight: 800; white-space: nowrap;">${mKindNm}</span> <span style="color: #6d28d9; font-weight: 700; white-space: nowrap;">${mPetNm}</span>`;
        } else {
            mPetTagEl.innerHTML = `<span style="color: #e11d48; font-weight: 800; white-space: nowrap;">${mKindNm}</span>`;
        }
    }
    document.getElementById('mDetailScoreNum').textContent = (postData.score || 0).toLocaleString();
    document.getElementById('mDetailTitle').textContent = postData.title || '';
    document.getElementById('mDetailContent').textContent = postData.content || '';

    const isCommented = (postData.actions && postData.actions.is_commented) || postData.is_commented || false;
    window.currentMobileDetailPost = postData;
    window.currentMobileDetailPostIsCommented = isCommented;

    const btnCommentPopup = document.getElementById('mDetailBtnComment');
    if (btnCommentPopup) {
        if (isCommented) {
            btnCommentPopup.classList.add('active');
            const icon = btnCommentPopup.querySelector('i');
            if (icon) icon.className = 'fa-solid fa-comment';
        } else {
            btnCommentPopup.classList.remove('active');
            const icon = btnCommentPopup.querySelector('i');
            if (icon) icon.className = 'fa-regular fa-comment';
        }
    }

    window.currentMobileDetailPostId = postData.post_id;
    loadMobileComments(postData.post_id);

    if (typeof triggerEvent === 'function') {
        triggerEvent(postData.post_id, 'view');
    }

    detailModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeMobileDetailModal() {
    const detailModal = document.getElementById('mDetailModal');
    if (detailModal) {
        detailModal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function loadMobileComments(postId) {
    fetch(`/api/comments/${postId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderMobileDetailComments(data.comments);
            }
        })
        .catch(err => console.error('모바일 댓글 로드 실패:', err));
}

function renderMobileDetailComments(comments) {
    const listEl = document.getElementById('mDetailCommentList');
    const headerCountEl = document.getElementById('mDetailCommentHeaderCount');
    if (headerCountEl) headerCountEl.textContent = `(${comments ? comments.length : 0})`;
    
    // 댓글 목록에서 현재 접속 유저가 쓴 댓글이 포함되어 있는지 점검 (초기 isCommented 상태 유지)
    const isInitiallyCommented = window.currentMobileDetailPostIsCommented === true || (window.currentMobileDetailPost && window.currentMobileDetailPost.actions && window.currentMobileDetailPost.actions.is_commented);
    let hasMyComment = !!isInitiallyCommented;

    if (!hasMyComment && comments && comments.length > 0) {
        const rawCurrentId = String(window.CURRENT_USER_ID || '');
        const currentUserId = rawCurrentId.split('_post_')[0];
        const currentNickname = window.CURRENT_USER_NICKNAME;

        hasMyComment = comments.some(c => {
            const rawCUserId = String(c.user_id || c.USER_ID || c.CMT_USER_ID || '');
            const cUserId = rawCUserId.split('_post_')[0];
            const cNickname = c.user_nickname || c.NK_NM;

            return (currentUserId && cUserId && cUserId === currentUserId) ||
                   (currentNickname && cNickname && cNickname === currentNickname);
        });
    }

    const btnCommentPopup = document.getElementById('mDetailBtnComment');
    if (btnCommentPopup) {
        if (hasMyComment) {
            btnCommentPopup.classList.add('active');
            const icon = btnCommentPopup.querySelector('i');
            if (icon) icon.className = 'fa-solid fa-comment';
        } else {
            btnCommentPopup.classList.remove('active');
            const icon = btnCommentPopup.querySelector('i');
            if (icon) icon.className = 'fa-regular fa-comment';
        }
    }

    if (!listEl) return;
    if (!comments || comments.length === 0) {
        listEl.innerHTML = '<div style="text-align: center; color: var(--text-muted); font-size: 0.75rem; padding: 0.5rem 0;">첫 한줄 댓글의 주인공이 되어보세요! 💬</div>';
        return;
    }
    
    listEl.innerHTML = comments.map(c => `
        <div style="background: #f8fafc; border: 1px solid var(--border-light); border-radius: 10px; padding: 0.4rem 0.6rem; font-size: 0.78rem; display: flex; flex-direction: column; gap: 0.15rem;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 0.3rem; font-weight: 800; color: var(--text-primary);">
                    <img src="${c.user_profile || '/static/image/profile/default_profile.png'}" style="width: 16px; height: 16px; border-radius: 50%; object-fit: cover;">
                    <span>${escapeHtml(c.user_nickname || '집사')}</span>
                </div>
                <span style="font-size: 0.68rem; color: var(--text-muted);">${c.created_at || ''}</span>
            </div>
            <div style="color: var(--text-secondary); font-weight: 500; word-break: break-all; padding-left: 1.2rem;">
                ${escapeHtml(c.content)}
            </div>
        </div>
    `).join('');
}

function submitMobileDetailComment() {
    const inputEl = document.getElementById('mDetailCommentInput');
    if (!inputEl || !window.currentMobileDetailPostId) return;
    const content = inputEl.value.trim();
    if (!content) {
        alert('댓글 내용을 입력해주세요.');
        return;
    }
    
    fetch(`/api/comments/${window.currentMobileDetailPostId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            alert(data.message || '댓글 작성 실패');
            if (data.require_login) {
                const mAuthModal = document.getElementById('mAuthModal');
                if (mAuthModal) mAuthModal.classList.add('active');
            }
            return;
        }
        
        inputEl.value = '';
        
        window.currentMobileDetailPostIsCommented = true;
        if (window.currentMobileDetailPost) {
            window.currentMobileDetailPost.is_commented = true;
            window.currentMobileDetailPost.actions = window.currentMobileDetailPost.actions || {};
            window.currentMobileDetailPost.actions.is_commented = true;
        }

        const mBtnCommentPopup = document.getElementById('mDetailBtnComment');
        if (mBtnCommentPopup) {
            mBtnCommentPopup.classList.add('active');
            const icon = mBtnCommentPopup.querySelector('i');
            if (icon) icon.className = 'fa-solid fa-comment';
        }
        
        // 메인 피드 카드 및 모바일 모달 수치 실시간 갱신 (+1 댓글, +10 점수)
        const mPostId = window.currentMobileDetailPostId;
        if (mPostId) {
            const mScoreEl = document.getElementById('mDetailScoreNum');
            if (mScoreEl) {
                const currentScore = parseInt(mScoreEl.textContent.replace(/,/g, ''), 10) || 0;
                mScoreEl.textContent = (currentScore + 10).toLocaleString();
            }

            const card = document.getElementById(`m-post-card-${mPostId}`);
            if (card) {
                const btnCardComment = card.querySelector('.btn-comment');
                if (btnCardComment) {
                    btnCardComment.classList.add('active');
                    const icon = btnCardComment.querySelector('i');
                    if (icon) icon.className = 'fa-solid fa-comment';
                }

                const cardComment = card.querySelector('.comment-count');
                if (cardComment) {
                    const currentCardCnt = parseInt(cardComment.textContent, 10) || 0;
                    cardComment.textContent = currentCardCnt + 1;
                }
                const cardScore = card.querySelector('.m-card-score, .score-num');
                if (cardScore) {
                    const currentScore = parseInt(cardScore.textContent.replace(/,/g, '').replace('⭐', '').trim(), 10) || 0;
                    cardScore.textContent = `⭐ ${(currentScore + 10).toLocaleString()}`;
                }
            }
        }

        loadMobileComments(window.currentMobileDetailPostId);
        if (data.event_res) {
            const scoreEl = document.getElementById('mDetailScoreNum');
            if (scoreEl) scoreEl.textContent = Number(data.event_res.new_score || 0).toLocaleString();
        }
    })
    .catch(err => {
        console.error('모바일 댓글 작성 오류:', err);
    });
}
