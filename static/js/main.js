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
        closeDetailBtn.addEventListener('click', () => closeDetailModal());
    }
    if (detailModal) {
        detailModal.addEventListener('click', (e) => {
            if (e.target === detailModal) closeDetailModal();
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
        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            if (eventType !== 'view') {
                showToast('서버 응답 오류가 발생하였습니다.', 'error');
            }
            return false;
        }
        const res = await response.json();

        if (!res.success) {
            // 조회(view) 이벤트시에는 어떠한 메세지도 일절 띄우지 않음
            if (eventType === 'view') {
                return false;
            }

            if (res.require_login) {
                showToast(res.message || '로그인이 필요한 서비스입니다.', 'warning');
                window.location.href = '/auth/google';
            } else if (res.is_owner) {
                // 본인 게시물일 경우 알림창을 띄우지 않고 조용히 기능만 제어
                return false;
            } else if (res.already_viewed) {
                // 이미 조회한 글인 경우 조용히 무시
                return false;
            } else {
                showToast(res.message || '요청 처리 실패', 'warning');
            }
            return false;
        }

        const data = res.data;
        
        // 전역 메모리 데이터 갱신
        if (!window.postsDataStore) window.postsDataStore = {};
        if (!window.postsDataStore[postId]) {
            window.postsDataStore[postId] = {};
        }
        window.postsDataStore[postId].like_count = data.like_count;
        window.postsDataStore[postId].score = data.new_score;
        window.postsDataStore[postId].view_count = data.view_count;
        window.postsDataStore[postId].comment_count = data.comment_count;
        window.postsDataStore[postId].share_count = data.share_count;
        if (data.is_liked !== undefined) {
            window.postsDataStore[postId].is_liked = data.is_liked;
            window.postsDataStore[postId].actions = window.postsDataStore[postId].actions || {};
            window.postsDataStore[postId].actions.is_liked = data.is_liked;
        }

        // UI Score 수치 갱신 & 카운터 갱신 (다중 식별자 호환)
        const cleanId = String(postId);
        const rawEntId = cleanId.replace(/^\d+_/, '');
        const card = document.getElementById(`post-card-${cleanId}`) || 
                     document.getElementById(`post-card-${rawEntId}`) ||
                     document.querySelector(`[data-post-id="${cleanId}"]`) ||
                     document.querySelector(`[data-ent-user-id="${rawEntId}"]`) ||
                     document.querySelector(`[data-ent-user-id="${cleanId}"]`);

        if (card) {
            const btnLike = card.querySelector('.btn-like');
            if (btnLike && data.is_liked !== undefined) {
                const icon = btnLike.querySelector('i');
                if (data.is_liked) {
                    btnLike.classList.add('active');
                    if (icon) {
                        icon.className = 'fa-solid fa-heart';
                        icon.style.color = '#e11d48';
                    }
                } else {
                    btnLike.classList.remove('active');
                    if (icon) {
                        icon.className = 'fa-regular fa-heart';
                        icon.style.color = '';
                    }
                }
            }

            const scoreDisplay = card.querySelector('.score-num');
            if (scoreDisplay) {
                const cardScoreVal = Number((data && data.new_score !== undefined) ? data.new_score : ((data && data.score) || 0));
                scoreDisplay.textContent = cardScoreVal.toLocaleString();
                
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

            if (viewNum && data.view_count !== undefined) {
                viewNum.textContent = data.view_count;
            }
            if (likeNum && data.like_count !== undefined) {
                likeNum.textContent = data.like_count;
            }
            if (commentNum && data.comment_count !== undefined) {
                commentNum.textContent = data.comment_count;
            }
            if (shareNum && data.share_count !== undefined) {
                shareNum.textContent = data.share_count;
            }
        }

        // 팝업 모달 내부 수치도 동시 실시간 갱신
        const detailViewCountEl = document.getElementById('detailViewCount');
        if (detailViewCountEl && data.view_count !== undefined) {
            detailViewCountEl.textContent = data.view_count;
        }
        const mDetailViewCountEl = document.getElementById('mDetailViewCount');
        if (mDetailViewCountEl && data.view_count !== undefined) {
            mDetailViewCountEl.textContent = data.view_count;
        }

        const detailScoreNumEl = document.getElementById('detailScoreNum');
        if (detailScoreNumEl && (data.new_score !== undefined || data.score !== undefined)) {
            const scoreVal = Number(data.new_score !== undefined ? data.new_score : data.score);
            detailScoreNumEl.textContent = scoreVal.toLocaleString();
        }

        // 모달 내부 수치 동기화 갱신
        const detailScore = document.getElementById('detailScoreNum');
        if (detailScore) {
            const modalScoreVal = Number((data && data.new_score !== undefined) ? data.new_score : ((data && data.score) || 0));
            detailScore.textContent = modalScoreVal.toLocaleString();
        }
        const dView = document.getElementById('detailViewCount');
        if (dView && data && data.view_count !== undefined) dView.textContent = data.view_count;
        const dLike = document.getElementById('detailLikeCount');
        if (dLike && data && data.like_count !== undefined) dLike.textContent = data.like_count;
        if (data && data.is_liked !== undefined) {
            const detailBtnLike = document.getElementById('detailBtnLike');
            const detailHeartIcon = document.getElementById('detailHeartIcon');
            if (detailBtnLike) {
                const icon = detailBtnLike.querySelector('i');
                if (data.is_liked) {
                    detailBtnLike.classList.add('active');
                    if (icon) icon.className = 'fa-solid fa-heart';
                } else {
                    detailBtnLike.classList.remove('active');
                    if (icon) icon.className = 'fa-regular fa-heart';
                }
            }
            if (detailHeartIcon) {
                detailHeartIcon.className = data.is_liked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
                detailHeartIcon.style.color = data.is_liked ? '#e11d48' : '';
            }
        }
        const dComment = document.getElementById('detailCommentCount');
        if (dComment && data && data.comment_count !== undefined) dComment.textContent = data.comment_count;
        const dShare = document.getElementById('detailShareCount');
        if (dShare && data && data.share_count !== undefined) dShare.textContent = data.share_count;

        if (eventType !== 'view') {
            const messages = {
                'like': '❤️ 좋아요! (Score +5)',
                'unlike': '🤍 좋아요 취소 (Score -5)',
                'comment': '💬 댓글 작성 (Score +10)'
            };
            if (messages[eventType]) {
                showToast(`✨ ${messages[eventType]} 점수가 반영되었습니다!`);
            }
        }
        return true;
    } catch (err) {
        console.error(err);
        return false;
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

// 전역 post 데이터 레지스트리
if (!window.postsDataStore) {
    window.postsDataStore = {};
}

/**
 * 게시물 상세 레이어 팝업 모달 띄우기
 */
function openDetailModal(post, isHallOfFame = false) {
    if (!window.isUserLoggedIn) {
        showToast('로그인이 필요한 서비스입니다. 먼저 로그인해주세요! 🐾', 'warning');
        setTimeout(() => {
            window.location.href = '/auth/google';
        }, 400);
        return;
    }

    const modal = document.getElementById('postDetailModal');
    if (!modal || !post) return;

    // 객체 데이터 속성 표준화
    post.post_id = post.post_id || post.POST_ID || ((post.CONTEST_ROUND || post.contest_id) && (post.ROUND_NO || post.round_no) ? `${post.CONTEST_ROUND || post.contest_id}_${post.ROUND_NO || post.round_no}` : (post.ROUND_NO || post.round_no));
    post.title = post.title || post.TITLE || '';
    post.content = post.content || post.CONTS || post.conts || '';
    post.score = post.score !== undefined ? post.score : (post.SCORE !== undefined ? post.SCORE : 0);
    post.created_at = post.created_at || post.ENT_DT || '';

    // 최신 메모리 데이터 객체 동기화
    if (!window.postsDataStore[post.post_id]) {
        window.postsDataStore[post.post_id] = Object.assign({}, post);
    }
    post = window.postsDataStore[post.post_id];

    // 회차 종료/마감 여부 판별
    const isClosedRound = isHallOfFame || 
                          post.contest_stat === 'G001C002' || 
                          post.CONTEST_STAT === 'G001C002' || 
                          post.is_ended === true || 
                          post.IS_ENDED === true;

    // 메인 피드 카드 DOM 수치가 더 최신일 경우 읽어와 보정 (종료 회차는 DB 확정 수치 100% 보존)
    if (!isClosedRound) {
        const feedCard = document.getElementById(`post-card-${post.post_id}`);
        if (feedCard) {
            const cardLike = feedCard.querySelector('.like-count');
            const cardScore = feedCard.querySelector('.score-num');
            if (cardLike && cardLike.textContent !== '') {
                post.like_count = parseInt(cardLike.textContent, 10) || post.like_count;
            }
            if (cardScore && cardScore.textContent !== '') {
                post.score = parseInt(cardScore.textContent.replace(/,/g, ''), 10) || post.score;
            }
        }
    }

    // 마감된 회차 데이터 제어: 점수 변동 이벤트 차단, 하트/댓글입력 영역 숨김, 수치 박스 손모양 제거
    const commentFormContainer = document.getElementById('detailCommentFormContainer');
    const commentScoreNotice = document.getElementById('detailCommentScoreNotice');
    const heartLikeBtn = document.getElementById('detailHeartLikeBtn');
    let btnLike = document.getElementById('detailBtnLike');

    let btnViewPopup = document.getElementById('detailBtnView');
    let btnCommentPopup = document.getElementById('detailBtnComment');

    if (isClosedRound) {
        if (commentFormContainer) commentFormContainer.style.display = 'none';
        if (commentScoreNotice) commentScoreNotice.style.display = 'none';
        if (heartLikeBtn) heartLikeBtn.style.display = 'none';
        [btnViewPopup, btnLike, btnCommentPopup].forEach(el => {
            if (el) {
                el.style.display = 'flex';
                el.style.pointerEvents = 'none';
                el.style.cursor = 'default';
            }
        });
    } else {
        if (commentFormContainer) commentFormContainer.style.display = 'flex';
        if (commentScoreNotice) commentScoreNotice.style.display = '';
        if (heartLikeBtn) heartLikeBtn.style.display = 'flex';
        [btnViewPopup, btnLike, btnCommentPopup].forEach(el => {
            if (el) {
                el.style.display = 'flex';
                el.style.pointerEvents = '';
                el.style.cursor = '';
            }
        });
        
        // 진행 중인 회차 팝업 시만 자동 조회수 증가
        triggerEvent(post.post_id, 'view');
    }

    // 출전 포기(삭제) 버튼 제어 (진행 중인 회차 + 본인 출전물인 경우 노출)
    const deleteBtn = document.getElementById('detailDeleteBtn');
    if (deleteBtn) {
        const currentUserId = String(window.CURRENT_USER_ID || '').trim();
        const postOwnerId = String(post.ENT_USER_ID || post.user_id || '').trim();
        if (!isClosedRound && currentUserId && postOwnerId && (currentUserId === postOwnerId || currentUserId === 'admin')) {
            deleteBtn.style.display = 'inline-flex';
        } else {
            deleteBtn.style.display = 'none';
        }
    }

    const cleanId = String(post.post_id);
    const rawEntId = cleanId.replace(/^\d+_/, '');
    const card = document.getElementById(`post-card-${cleanId}`) || 
                 document.getElementById(`post-card-${rawEntId}`) ||
                 document.querySelector(`[data-post-id="${cleanId}"]`) ||
                 document.querySelector(`[data-ent-user-id="${rawEntId}"]`) ||
                 document.querySelector(`[data-ent-user-id="${cleanId}"]`);
    if (!isClosedRound) {
        if (card) {
            const btnView = card.querySelector('.btn-view');
            if (btnView) {
                btnView.classList.add('active');
                const icon = btnView.querySelector('i');
                if (icon) icon.className = 'fa-solid fa-eye';
            }
        }

        // 팝업 모달 내부의 조회수 버튼 박스도 진행 중 회차에서만 활성화(active) 하이라이트
        const detailBtnViewPopup = document.getElementById('detailBtnView');
        if (detailBtnViewPopup) {
            detailBtnViewPopup.classList.add('active');
            const icon = detailBtnViewPopup.querySelector('i');
            if (icon) icon.className = 'fa-solid fa-eye';
        }
    } else {
        // 종료된 회차인 경우 DB 저장이 진행되지 않으므로 active 클래스를 제거하고 비활성화 상태 유지
        const detailBtnViewPopup = document.getElementById('detailBtnView');
        if (detailBtnViewPopup) {
            detailBtnViewPopup.classList.remove('active');
            const icon = detailBtnViewPopup.querySelector('i');
            if (icon) icon.className = 'fa-regular fa-eye';
        }
        if (card) {
            const btnView = card.querySelector('.btn-view');
            if (btnView) {
                btnView.classList.remove('active');
                const icon = btnView.querySelector('i');
                if (icon) icon.className = 'fa-regular fa-eye';
            }
        }
    }

    // 데이터 채우기 (팝업용 고화질 이미지 바인딩)
    const imgEl = document.getElementById('detailImg');
    const imgSrc = post.popup_image_path || post.POPUP_IMAGE_PATH || post.IMAGE_PATH || post.image_path || post.media_url || 
        ((post.file_path && post.list_file_name) ? (post.file_path.endsWith('/') ? post.file_path : post.file_path + '/') + post.list_file_name : '');
    if (imgEl) {
        imgEl.src = imgSrc;
    }

    const authorImgEl = document.getElementById('detailAuthorImg');
    if (authorImgEl) authorImgEl.src = post.PROFILE_URL || post.user_profile || '/static/image/profile/default_profile.png';

    const nicknameEl = document.getElementById('detailAuthorNickname');
    if (nicknameEl) nicknameEl.textContent = post.NK_NM || post.user_nickname || '집사';

    const petTagEl = document.getElementById('detailPetTag');
    if (petTagEl) {
        let kindNm = post.KIND_NM || post.pet_type || '반려동물';
        if (!/[🐕🐈🐹🦜🐇🦔🦎🐠🦦🐾🐶🐱🐰]/.test(kindNm)) {
            let icon = '🐾';
            if (kindNm.includes('강아지') || kindNm.includes('개')) icon = '🐕';
            else if (kindNm.includes('고양이')) icon = '🐈';
            else if (kindNm.includes('햄스터')) icon = '🐹';
            else if (kindNm.includes('앵무새') || kindNm.includes('새')) icon = '🦜';
            else if (kindNm.includes('토끼')) icon = '🐇';
            else if (kindNm.includes('고슴도치')) icon = '🦔';
            else if (kindNm.includes('파충류')) icon = '🦎';
            else if (kindNm.includes('어류') || kindNm.includes('관상어')) icon = '🐠';
            else if (kindNm.includes('페럿')) icon = '🦦';
            kindNm = `${icon} ${kindNm}`;
        }
        const petNm = post.PET_NM || post.pet_name || '';
        if (petNm) {
            petTagEl.innerHTML = `<span style="color: #e11d48; font-weight: 800; white-space: nowrap;">${kindNm}</span> <span style="color: #6d28d9; font-weight: 700; white-space: nowrap;">${petNm}</span>`;
        } else {
            petTagEl.innerHTML = `<span style="color: #e11d48; font-weight: 800; white-space: nowrap;">${kindNm}</span>`;
        }
    }

    const scoreNumEl = document.getElementById('detailScoreNum');
    if (scoreNumEl) scoreNumEl.textContent = Number(post.score || 0).toLocaleString();

    const titleEl = document.getElementById('detailTitle');
    if (titleEl) titleEl.textContent = post.title || '';

    const contentEl = document.getElementById('detailContent');
    if (contentEl) contentEl.textContent = post.content || '';

    const createdAtEl = document.getElementById('detailCreatedAt');
    if (createdAtEl) createdAtEl.textContent = post.created_at || '2026-07-28 00:00:00';

    const viewCountEl = document.getElementById('detailViewCount');
    if (viewCountEl) viewCountEl.textContent = (post.view_count !== undefined ? post.view_count : (post.VW_CNT !== undefined ? post.VW_CNT : 0));

    const likeCountEl = document.getElementById('detailLikeCount');
    if (likeCountEl) likeCountEl.textContent = (post.like_count !== undefined ? post.like_count : (post.LIKE_CNT !== undefined ? post.LIKE_CNT : 0));

    const commentCountEl = document.getElementById('detailCommentCount');
    if (commentCountEl) commentCountEl.textContent = (post.comment_count !== undefined ? post.comment_count : (post.CMT_CNT !== undefined ? post.CMT_CNT : 0));

    const shareCountEl = document.getElementById('detailShareCount');
    if (shareCountEl) shareCountEl.textContent = post.share_count || 0;

    const isCommented = (post.actions && post.actions.is_commented) || post.is_commented || false;
    window.currentDetailPost = post;
    window.currentDetailPostIsCommented = isCommented;

    btnCommentPopup = document.getElementById('detailBtnComment');
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

    // 현재 열린 게시물 ID 저장 및 댓글 로드
    window.currentDetailPostId = post.post_id;
    loadComments(post.post_id);

    // 본인 게시물 포함 모든 게시물에 댓글 작성 가능하도록 활성화
    const inputEl = document.getElementById('detailCommentInput');
    const submitBtn = inputEl ? inputEl.nextElementSibling : null;
    if (inputEl) {
        inputEl.disabled = false;
        inputEl.placeholder = '사랑스러운 응원의 한줄 댓글을 남겨보세요!';
        if (submitBtn) submitBtn.disabled = false;
    }

    // 랭킹 / 수상 배지 채우기 (오직 실물 메달/배지 이미지들만 전체부문 -> 품종부문 순서로 가로 나란히 표시)
    const medalsLeftEl = document.getElementById('detailMedalsLeft');
    const badgeEl = document.getElementById('detailRankBadge');

    if (medalsLeftEl) medalsLeftEl.innerHTML = '';

    if (post.awards && post.awards.length > 0) {
        const sortedAwards = [...post.awards].sort((a, b) => {
            const partA = a.award_part || a.AWARD_PART || '';
            const partB = b.award_part || b.AWARD_PART || '';
            return partA.localeCompare(partB);
        });

        const kindNm = post.KIND_NM || post.pet_type || '';
        let petIconClass = 'fa-solid fa-paw';
        if (kindNm.includes('강아지') || kindNm.includes('개')) petIconClass = 'fa-solid fa-dog';
        else if (kindNm.includes('고양이')) petIconClass = 'fa-solid fa-cat';
        else if (kindNm.includes('어류') || kindNm.includes('관상어') || kindNm.includes('물고기')) petIconClass = 'fa-solid fa-fish';
        else if (kindNm.includes('앵무새') || kindNm.includes('새')) petIconClass = 'fa-solid fa-crow';
        else if (kindNm.includes('말') || kindNm.includes('큰동물')) petIconClass = 'fa-solid fa-horse';

        if (badgeEl) {
            badgeEl.style.justifyContent = 'flex-end';
            badgeEl.style.right = '0.75rem';
            badgeEl.style.left = 'auto';

            let html = '<div style="display: flex; align-items: center; justify-content: flex-end; gap: 0.45rem; flex-wrap: wrap;">';
            sortedAwards.forEach(aw => {
                const awardCdStr = String(aw.award_cd || aw.AWARD_CD || '');
                const awardNmStr = String(aw.award_nm || aw.AWARD_NM || '');
                const awRank = aw.ranking || aw.RANKING;

                if (awardCdStr.includes('P001A101') || awardNmStr.includes('슈퍼')) {
                    html += `<div class="winner-title-badge superstar-badge" style="position: relative; top: 0; right: 0; margin: 0; font-size: 0.8rem; padding: 0.35rem 0.85rem;"><i class="fa-solid fa-crown"></i> <span>슈퍼스타</span></div>`;
                } else if (awardCdStr.includes('P001A102') || awardNmStr.includes('라이징')) {
                    html += `<div class="winner-title-badge risingstar-badge" style="position: relative; top: 0; right: 0; margin: 0; font-size: 0.8rem; padding: 0.35rem 0.85rem;"><i class="fa-solid fa-wand-magic-sparkles"></i> <span>라이징스타</span></div>`;
                } else if (awardCdStr.includes('P001A103') || awardNmStr.includes('브라이트')) {
                    html += `<div class="winner-title-badge brightstar-badge" style="position: relative; top: 0; right: 0; margin: 0; font-size: 0.8rem; padding: 0.35rem 0.85rem;"><i class="fa-solid fa-star"></i> <span>브라이트스타</span></div>`;
                } else {
                    const rankSuffix = awRank ? ` ${awRank}위` : '';
                    html += `<div class="winner-title-badge family-badge" style="position: relative; top: 0; right: 0; margin: 0; font-size: 0.8rem; padding: 0.35rem 0.85rem;"><span class="pet-emoji-icon"><i class="${petIconClass}"></i></span> <span>패밀리스타${rankSuffix}</span></div>`;
                }
            });
            html += '</div>';
            badgeEl.innerHTML = html;
        }
    } else {
        if (badgeEl) {
            if (post.rank_candidate && !isClosedRound) {
                badgeEl.style.justifyContent = 'flex-start';
                badgeEl.style.left = '0.75rem';
                badgeEl.style.right = 'auto';

                const kindNm = post.KIND_NM || post.pet_type || '';
                let petIconClass = 'fa-solid fa-paw';
                if (kindNm.includes('강아지') || kindNm.includes('개')) petIconClass = 'fa-solid fa-dog';
                else if (kindNm.includes('고양이')) petIconClass = 'fa-solid fa-cat';
                else if (kindNm.includes('어류') || kindNm.includes('관상어') || kindNm.includes('물고기')) petIconClass = 'fa-solid fa-fish';
                else if (kindNm.includes('앵무새') || kindNm.includes('새')) petIconClass = 'fa-solid fa-crow';
                else if (kindNm.includes('말') || kindNm.includes('큰동물')) petIconClass = 'fa-solid fa-horse';

                const urlParams = new URLSearchParams(window.location.search);
                const currentPetType = urlParams.get('pet_type') || 'all';
                const isFamily = (currentPetType && currentPetType !== 'all');
                const catPrefix = isFamily ? '패밀리스타 ' : '전체 ';
                const iconClass = isFamily ? petIconClass : 'fa-solid fa-medal';
                const prefix = (post.is_co_rank ? '공동 ' : '') + catPrefix;
                const rankTitle = `${prefix}${post.rank_candidate}위 후보`;
                if (isFamily) {
                    badgeEl.innerHTML = `<div class="winner-title-badge family-badge" style="position: relative; top: 0; left: 0; right: auto; margin: 0; font-size: 0.8rem; padding: 0.35rem 0.85rem;"><span class="pet-emoji-icon"><i class="${petIconClass}"></i></span> <span>${rankTitle}</span></div>`;
                } else {
                    if (post.rank_candidate === 1) {
                        badgeEl.innerHTML = `<div class="rank-ribbon rank-1" style="font-size: 0.8rem; padding: 0.35rem 0.85rem; margin: 0;"><i class="fa-solid fa-medal"></i> ${rankTitle}</div>`;
                    } else if (post.rank_candidate === 2) {
                        badgeEl.innerHTML = `<div class="rank-ribbon rank-2" style="font-size: 0.8rem; padding: 0.35rem 0.85rem; margin: 0;"><i class="fa-solid fa-medal"></i> ${rankTitle}</div>`;
                    } else if (post.rank_candidate === 3) {
                        badgeEl.innerHTML = `<div class="rank-ribbon rank-3" style="font-size: 0.8rem; padding: 0.35rem 0.85rem; margin: 0;"><i class="fa-solid fa-medal"></i> ${rankTitle}</div>`;
                    } else {
                        badgeEl.innerHTML = '';
                    }
                }
            } else {
                badgeEl.innerHTML = '';
            }
        }
    }

    // 모달 내부 버튼 이벤트 바인딩 & 좋아요 토글 처리
    const heartBtn = document.getElementById('detailHeartLikeBtn');
    const heartIcon = document.getElementById('detailHeartIcon');
    btnLike = document.getElementById('detailBtnLike');

    let isLiked = !!((post.actions && post.actions.is_liked) || post.is_liked);

    const updatePopupLikeUI = (likedState) => {
        if (btnLike) {
            const icon = btnLike.querySelector('i');
            if (likedState) {
                btnLike.classList.add('active');
                if (icon) icon.className = 'fa-solid fa-heart';
            } else {
                btnLike.classList.remove('active');
                if (icon) icon.className = 'fa-regular fa-heart';
            }
        }
        if (heartIcon) {
            heartIcon.className = likedState ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
            heartIcon.style.color = likedState ? '#e11d48' : '';
        }
    };

    const updatePopupCommentUI = (commentedState) => {
        const btnCommentPopup = document.getElementById('detailBtnComment');
        if (btnCommentPopup) {
            if (commentedState) {
                btnCommentPopup.classList.add('active');
                const icon = btnCommentPopup.querySelector('i');
                if (icon) icon.className = 'fa-solid fa-comment';
            } else {
                btnCommentPopup.classList.remove('active');
                const icon = btnCommentPopup.querySelector('i');
                if (icon) icon.className = 'fa-regular fa-comment';
            }
        }
    };

    // 팝업 열릴 때 즉각 하트 상태 100% 명시적 초기화 및 색상 채우기
    updatePopupLikeUI(isLiked);

    fetch(`/api/post/user_actions/${post.post_id}`)
        .then(res => res.json())
        .then(data => {
            if (data && data.success && data.actions) {
                isLiked = !!data.actions.is_liked;
                updatePopupLikeUI(isLiked);
                if (data.actions.is_commented !== undefined) {
                    window.currentDetailPostIsCommented = !!data.actions.is_commented;
                    updatePopupCommentUI(!!data.actions.is_commented);
                }
            }
        })
        .catch(err => {
            console.error(err);
            updatePopupLikeUI(isLiked);
        });

    const toggleLikeHandler = async () => {
        if (!isLiked) {
            const success = await triggerEvent(post.post_id, 'like');
            if (success !== false) {
                isLiked = true;
                updatePopupLikeUI(true);
            }
        } else {
            const success = await triggerEvent(post.post_id, 'unlike');
            if (success !== false) {
                isLiked = false;
                updatePopupLikeUI(false);
            }
        }
    };

    if (!isClosedRound) {
        if (heartBtn) heartBtn.onclick = toggleLikeHandler;
        if (btnLike) btnLike.onclick = toggleLikeHandler;
    } else {
        if (heartBtn) heartBtn.onclick = null;
        if (btnLike) btnLike.onclick = null;
    }

    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
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

// 전역 post 데이터 레지스트리
if (!window.postsDataStore) {
    window.postsDataStore = {};
}



function closeDetailModal() {
    const modal = document.getElementById('postDetailModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
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
                const count = data.comments ? data.comments.length : 0;
                const commentCountEl = document.getElementById('detailCommentCount');
                if (commentCountEl) commentCountEl.textContent = count;
                
                const card = document.getElementById(`post-card-${postId}`);
                if (card) {
                    const cardComment = card.querySelector('.comment-count');
                    if (cardComment) cardComment.textContent = count;
                }
            }
        })
        .catch(err => console.error('댓글 로드 실패:', err));
}

function renderDetailComments(comments) {
    const listEl = document.getElementById('detailCommentList');
    const headerCountEl = document.getElementById('detailCommentHeaderCount');
    if (headerCountEl) headerCountEl.textContent = `(${comments ? comments.length : 0})`;
    
    // 댓글 목록에서 현재 접속 유저가 쓴 댓글이 포함되어 있는지 점검 (초기 isCommented 상태 유지)
    const isInitiallyCommented = window.currentDetailPostIsCommented === true || (window.currentDetailPost && window.currentDetailPost.actions && window.currentDetailPost.actions.is_commented);
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

    const btnCommentPopup = document.getElementById('detailBtnComment');
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
        if (!data.success) {
            showToast(data.message || '댓글 작성 실패', 'warning');
            if (data.require_login) {
                const googleModal = document.getElementById('googleAuthModal');
                if (googleModal) googleModal.classList.add('show');
            }
            return;
        }
        
        inputEl.value = '';
        showToast('한줄 댓글 작성 완료! (+10점 반영)', 'success');
        
        window.currentDetailPostIsCommented = true;
        if (window.currentDetailPost) {
            window.currentDetailPost.is_commented = true;
            window.currentDetailPost.actions = window.currentDetailPost.actions || {};
            window.currentDetailPost.actions.is_commented = true;
        }

        const btnComment = document.getElementById('detailBtnComment');
        if (btnComment) {
            btnComment.classList.add('active');
            const icon = btnComment.querySelector('i');
            if (icon) icon.className = 'fa-solid fa-comment';
        }

        // 서버 DB에서 최종 재계산된 3요소 및 SCORE 데이터 활용
        const finalScore = Number(data.score !== undefined ? data.score : (data.new_score !== undefined ? data.new_score : (data.event_res ? data.event_res.score : 0)));
        const finalView = (data.view_count !== undefined ? data.view_count : (data.event_res ? data.event_res.view_count : undefined));
        const finalLike = (data.like_count !== undefined ? data.like_count : (data.event_res ? data.event_res.like_count : undefined));
        const finalComment = (data.comment_count !== undefined ? data.comment_count : (data.event_res ? data.event_res.comment_count : undefined));

        const postId = window.currentDetailPostId;
        if (postId) {
            if (window.postsDataStore && window.postsDataStore[postId]) {
                const storeItem = window.postsDataStore[postId];
                if (finalComment !== undefined) storeItem.comment_count = finalComment;
                if (finalComment !== undefined) storeItem.CMT_CNT = finalComment;
                if (finalScore) {
                    storeItem.score = finalScore;
                    storeItem.SCORE = finalScore;
                }
                storeItem.is_commented = true;
                storeItem.actions = storeItem.actions || {};
                storeItem.actions.is_commented = true;
            }

            const commentCountEl = document.getElementById('detailCommentCount');
            if (commentCountEl && finalComment !== undefined) {
                commentCountEl.textContent = finalComment;
            }

            const viewCountEl = document.getElementById('detailViewCount');
            if (viewCountEl && finalView !== undefined) {
                viewCountEl.textContent = finalView;
            }

            const likeCountEl = document.getElementById('detailLikeCount');
            if (likeCountEl && finalLike !== undefined) {
                likeCountEl.textContent = finalLike;
            }

            const scoreNumEl = document.getElementById('detailScoreNum');
            if (scoreNumEl && finalScore) {
                scoreNumEl.textContent = finalScore.toLocaleString();
            }

            const cleanId = String(postId);
            const rawEntId = cleanId.replace(/^\d+_/, '');
            const card = document.getElementById(`post-card-${cleanId}`) || 
                         document.getElementById(`post-card-${rawEntId}`) ||
                         document.querySelector(`[data-post-id="${cleanId}"]`) ||
                         document.querySelector(`[data-ent-user-id="${rawEntId}"]`) ||
                         document.querySelector(`[data-ent-user-id="${cleanId}"]`);
                         
            if (card) {
                const btnCardComment = card.querySelector('.btn-comment');
                if (btnCardComment) {
                    btnCardComment.classList.add('active');
                    const icon = btnCardComment.querySelector('i');
                    if (icon) icon.className = 'fa-solid fa-comment';
                }

                const cardComment = card.querySelector('.comment-count');
                if (cardComment && finalComment !== undefined) {
                    cardComment.textContent = finalComment;
                }
                const cardScore = card.querySelector('.score-num');
                if (cardScore && finalScore) {
                    cardScore.textContent = finalScore.toLocaleString();
                }
                const cardView = card.querySelector('.view-count');
                if (cardView && finalView !== undefined) {
                    cardView.textContent = finalView;
                }
                const cardLike = card.querySelector('.like-count');
                if (cardLike && finalLike !== undefined) {
                    cardLike.textContent = finalLike;
                }
            }
        }

        loadComments(window.currentDetailPostId);
    })
    .catch(err => {
        console.error('댓글 작성 오류:', err);
        showToast('댓글 등록 중 오류가 발생했습니다.', 'error');
    });
}

async function handleShareClick() {
    if (!window.currentDetailPostId) return;
    const btnShare = document.getElementById('detailBtnShare');
    const success = await triggerEvent(window.currentDetailPostId, 'share');
    if (btnShare) btnShare.classList.add('active');
}

async function toggleLikeCard(btn, postId) {
    if (typeof showToast === 'function') {
        showToast('💡 좋아요는 게시물을 클릭하여 상세 팝업창에서만 누르실 수 있습니다.');
    }
    return false;
}

async function deleteCurrentPost() {
    const postId = window.currentDetailPostId;
    if (!postId) {
        showToast('게시물 정보를 찾을 수 없습니다.', 'error');
        return;
    }

    if (!confirm('정말 이 출전물을 포기(삭제)하시겠습니까?\n삭제 후에는 해당 출전물과 관련 점수가 모두 제거되며 복구할 수 없습니다.')) {
        return;
    }

    try {
        const response = await fetch('/api/post/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ post_id: postId })
        });
        const result = await response.json();

        if (result.success) {
            showToast('🗑️ 출전이 성공적으로 포기(삭제)되었습니다.');
            closeDetailModal();
            const cardEl = document.getElementById(`post-card-${postId}`);
            if (cardEl) {
                cardEl.remove();
            } else {
                setTimeout(() => location.reload(), 500);
            }
        } else {
            showToast(result.message || '출전 포기 처리 중 오류가 발생했습니다.', 'error');
        }
    } catch (e) {
        console.error('deleteCurrentPost error:', e);
        showToast('서버 통신 중 오류가 발생했습니다.', 'error');
    }
}

// 전역 스코프 바인딩
window.openDetailModal = openDetailModal;
window.closeDetailModal = closeDetailModal;
window.deleteCurrentPost = deleteCurrentPost;
window.triggerEvent = triggerEvent;
window.toggleLikeCard = toggleLikeCard;
window.submitDetailComment = submitDetailComment;
window.handleShareClick = handleShareClick;
window.runAwardBatch = runAwardBatch;

// 출전 신청 및 로그인 필요 기능 가드
document.addEventListener('DOMContentLoaded', function() {
    // 1. URL login_required 쿼리 감지 시 로그인 유도 토스트 및 모달 표시
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('login_required') === 'true') {
        showToast('로그인이 필요한 서비스입니다. 먼저 로그인해주세요! 🐾', 'warning');
        const googleModal = document.getElementById('googleAuthModal') || document.getElementById('mGoogleAuthModal');
        if (googleModal) googleModal.classList.add('show');
    }

    // 2. 모든 출전 신청 링크/버튼 클릭 시 비로그인이면 즉시 로그인 모달 팝업 표출
    const uploadLinks = document.querySelectorAll('a[href="/upload"], a[href="/m/upload"], .btn-hero-cta');
    uploadLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // UI 상의 프로필/로그아웃 요소 존재 여부를 함께 체크하여 실제 로그인 상태 정확히 판별
            const hasProfileUI = document.querySelector('.profile-dropdown') || document.querySelector('.m-nav-profile') || document.querySelector('a[href="/logout"]') || document.querySelector('a[href="/api/logout"]');
            const isLoggedIn = window.isUserLoggedIn || !!hasProfileUI;

            if (!isLoggedIn) {
                e.preventDefault();
                e.stopPropagation();
                const targetPath = link.getAttribute('href') || '/upload';
                window.location.href = '/auth/google?next=' + encodeURIComponent(targetPath);
            }
        });
    });
});

function openGoogleLoginModal() {
    window.location.href = '/auth/google';
}
window.openGoogleLoginModal = openGoogleLoginModal;

// 아무런 액션 없이 30분(1800초) 경과 시 클라이언트 세션 자동 만료 모니터링
(function initInactivityTimer() {
    if (!window.isUserLoggedIn) return;

    const TIMEOUT_MS = 30 * 60 * 1000; // 30분 (1800초)
    let lastActionTime = Date.now();
    let isNotified = false;

    const resetInactivityTimer = () => {
        lastActionTime = Date.now();
    };

    ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart', 'click'].forEach(evtName => {
        window.addEventListener(evtName, resetInactivityTimer, { passive: true });
    });

    setInterval(() => {
        if (!window.isUserLoggedIn || isNotified) return;
        const idleDuration = Date.now() - lastActionTime;
        if (idleDuration >= TIMEOUT_MS) {
            isNotified = true;
            if (typeof showToast === 'function') {
                showToast('30분 동안 활동이 없어 세션이 만료되었습니다. 다시 로그인해주세요. 🐾', 'warning');
            } else {
                alert('30분 동안 활동이 없어 세션이 만료되었습니다. 다시 로그인해주세요. 🐾');
            }
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    }, 10000);
})();
