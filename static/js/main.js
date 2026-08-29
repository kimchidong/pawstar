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

/**
 * YouTube URL 또는 Video ID에서 11자리 비디오 ID 추출
 */
function getYouTubeVideoId(url) {
    if (!url || typeof url !== 'string') return null;
    url = url.trim();
    if (!url) return null;
    if (url.includes('/@') || url.includes('/channel/') || url.includes('/user/')) return null;
    const regExp = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = url.match(regExp);
    if (match && match[1]) return match[1];
    if (/^[a-zA-Z0-9_-]{11}$/.test(url)) return url;
    return null;
}

// YouTube IFrame API 스크립트 자동 로딩
if (typeof document !== 'undefined' && !document.getElementById('youtube-iframe-api-script')) {
    const tag = document.createElement('script');
    tag.id = 'youtube-iframe-api-script';
    tag.src = "https://www.youtube.com/iframe_api";
    const firstScriptTag = document.getElementsByTagName('script')[0];
    if (firstScriptTag && firstScriptTag.parentNode) {
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    }
}

/**
 * YouTube 동영상 재생 및 무한 순환 [이미지 3초 -> 동영상 재생 -> 이미지 3초 -> 동영상 재생] 헬퍼
 */
function setupYouTubePlayerWithEnding(containerId, imgId, videoId, fadeTimerKey, playerKey, loopTimerKey) {
    const container = document.getElementById(containerId);
    const imgEl = document.getElementById(imgId);
    if (!container) return;

    if (!loopTimerKey) loopTimerKey = fadeTimerKey + '_loop';

    if (window[fadeTimerKey]) {
        clearTimeout(window[fadeTimerKey]);
        window[fadeTimerKey] = null;
    }
    if (window[loopTimerKey]) {
        clearTimeout(window[loopTimerKey]);
        window[loopTimerKey] = null;
    }
    if (window[playerKey] && typeof window[playerKey].destroy === 'function') {
        try { window[playerKey].destroy(); } catch(e) {}
        window[playerKey] = null;
    }

    if (!videoId) {
        container.style.display = 'none';
        container.innerHTML = '';
        if (imgEl) imgEl.style.opacity = '1';
        return;
    }

    container.style.display = 'block';
    const iframeId = containerId + '_iframe';
    container.innerHTML = `<div id="${iframeId}" style="width: 100%; height: 100%;"></div>`;

    const initPlayer = () => {
        try {
            window[playerKey] = new YT.Player(iframeId, {
                width: '100%',
                height: '100%',
                videoId: videoId,
                playerVars: {
                    'autoplay': 1,
                    'mute': 1,
                    'playsinline': 1,
                    'enablejsapi': 1,
                    'rel': 0,
                    'controls': 1
                },
                events: {
                    'onReady': (event) => {
                        try { event.target.playVideo(); } catch(e) {}
                        window[fadeTimerKey] = setTimeout(() => {
                            if (imgEl) imgEl.style.opacity = '0';
                        }, 3000);
                    },
                    'onStateChange': (event) => {
                        // YT.PlayerState.ENDED = 0 (동영상 종료 시 이미지 3초 노출 후 재생 무한 반복)
                        if (event.data === 0 || (window.YT && window.YT.PlayerState && event.data === window.YT.PlayerState.ENDED)) {
                            if (imgEl) imgEl.style.opacity = '1';
                            try { event.target.seekTo(0); } catch(e) {}
                            
                            if (window[loopTimerKey]) clearTimeout(window[loopTimerKey]);
                            window[loopTimerKey] = setTimeout(() => {
                                try { event.target.playVideo(); } catch(e) {}
                                if (imgEl) imgEl.style.opacity = '0';
                            }, 3000);
                        }
                    }
                }
            });
        } catch(e) {
            container.innerHTML = `<iframe id="${iframeId}" src="https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&playsinline=1&enablejsapi=1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="width: 100%; height: 100%; border: none;"></iframe>`;
            window[fadeTimerKey] = setTimeout(() => {
                if (imgEl) imgEl.style.opacity = '0';
            }, 3000);
        }
    };

    if (window.YT && window.YT.Player) {
        initPlayer();
    } else {
        let attempts = 0;
        const timer = setInterval(() => {
            attempts++;
            if (window.YT && window.YT.Player) {
                clearInterval(timer);
                initPlayer();
            } else if (attempts > 30) {
                clearInterval(timer);
                initPlayer();
            }
        }, 100);
    }
}

/**
 * 일자시간 상대시간(방금 전, N초 전, N분 전, N시간 전, N일 전, N달 전, N년 전) 포맷팅
 */
function formatTimeAgo(dateInput) {
    if (!dateInput) return '방금 전';

    if (dateInput instanceof Date) {
        if (isNaN(dateInput.getTime())) return '방금 전';
        return _calculateTimeAgo(dateInput);
    }

    let dtStr = String(dateInput).trim();
    if (!dtStr) return '방금 전';
    if (dtStr.endsWith(' 전')) return dtStr;

    let date = null;
    const match = dtStr.match(/^(\d{4})[-/](\d{1,2})[-/](\d{1,2})[ T](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?/);
    if (match) {
        date = new Date(
            parseInt(match[1], 10),
            parseInt(match[2], 10) - 1,
            parseInt(match[3], 10),
            parseInt(match[4], 10),
            parseInt(match[5], 10),
            parseInt(match[6] || '0', 10)
        );
    } else {
        date = new Date(dtStr);
        if (isNaN(date.getTime())) {
            date = new Date(dtStr.replace(/-/g, '/'));
        }
    }

    if (!date || isNaN(date.getTime())) {
        return '방금 전';
    }

    return _calculateTimeAgo(date);
}

function _calculateTimeAgo(date) {
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffSec < 0 || diffSec < 10) {
        return '방금 전';
    }
    if (diffSec < 60) {
        return `${diffSec}초 전`;
    }
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) {
        return `${diffMin}분 전`;
    }
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) {
        return `${diffHour}시간 전`;
    }
    const diffDay = Math.floor(diffHour / 24);
    if (diffDay < 30) {
        return `${diffDay}일 전`;
    }
    const diffMonth = Math.floor(diffDay / 30);
    if (diffMonth < 12) {
        return `${diffMonth}달 전`;
    }
    let diffYear = Math.floor(diffDay / 365);
    if (diffYear < 1) diffYear = 1;
    return `${diffYear}년 전`;
}

window.formatTimeAgo = formatTimeAgo;
window.timeAgo = formatTimeAgo;

/**
 * 브라우저 쿠키(document.cookie) 기준 실시간 로그인 유효성 검사
 */
function checkCurrentLoginCookie() {
    if (!document.cookie) return false;
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const parts = cookies[i].trim().split('=');
        const name = parts[0];
        const val = parts[1] || '';
        if ((name === 'user_id' || name === 'pst_user_id' || name === 'user_uuid' || name === 'session') && val.trim() !== '' && val !== 'deleted' && val !== 'null') {
            return true;
        }
    }
    return false;
}
/**
 * 현재 시점 로그인 상태 엄격 체크 헬퍼
 * @param {Function} [onSuccess] 로그인 상태일 때 실행할 콜백
 * @returns {boolean} 로그인 상태 여부
 */
function ensureLoggedIn(onSuccess) {
    const isLoggedIn = !!(window.isUserLoggedIn || window.CURRENT_USER_ID);

    if (!isLoggedIn) {
        window.isUserLoggedIn = false;
        window.CURRENT_USER_ID = '';
        if (typeof openGoogleAuthModal === 'function') {
            openGoogleAuthModal();
        } else {
            const m = document.getElementById('googleAuthModal') || document.getElementById('mAuthModal');
            if (m) {
                m.style.display = 'flex';
                m.style.zIndex = '999999';
                m.classList.add('show', 'active');
            } else {
                window.location.href = '/auth/google';
            }
        }
        return false;
    }

    if (typeof onSuccess === 'function') {
        onSuccess();
    }
    return true;
}
window.ensureLoggedIn = ensureLoggedIn;

/**
 * 카드 클릭 전용 세션 체킹 래퍼 함수 (서버 세션 100% 검증 후 출전작 팝업 열기)
 */
async function handleCardClick(post, isHallOfFame = false) {
    if (!ensureLoggedIn()) return false;
    const isAlive = await verifyServerSessionAsync();
    if (!isAlive) {
        if (typeof openGoogleAuthModal === 'function') openGoogleAuthModal();
        return false;
    }
    openDetailModal(post, isHallOfFame);
}
window.handleCardClick = handleCardClick;

/**
 * 서버 측 세션 타임아웃 실시간 검증 헬퍼
 * @returns {Promise<boolean>}
 */
async function verifyServerSessionAsync() {
    try {
        const res = await fetch('/api/auth/check-session?t=' + Date.now(), {
            method: 'GET',
            headers: { 
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache'
            }
        });
        const data = await res.json();
        if (data && data.logged_in) {
            // 진짜 정상 로그인 회원 -> 로그인 상태 확정 및 pawstar_logged_out 플래그 제거
            window.isUserLoggedIn = true;
            if (data.user_id) window.CURRENT_USER_ID = data.user_id;
            try { localStorage.removeItem('pawstar_logged_out'); } catch(e) {}
            return true;
        }
    } catch (e) {
        console.warn('verifyServerSessionAsync error:', e);
        if (window.isUserLoggedIn) return true;
    }

    // 서버 세션 만료/로그아웃된 경우에만 세션 파기 및 기존 열린 팝업 닫기 후 구글 로그인 안내 모달 발동
    window.isUserLoggedIn = false;
    window.CURRENT_USER_ID = '';
    try {
        localStorage.setItem('pawstar_logged_out', 'true');
    } catch(e) {}

    if (typeof closeDetailModal === 'function') closeDetailModal();
    if (typeof closeMobileDetailModal === 'function') closeMobileDetailModal();

    if (typeof openGoogleAuthModal === 'function') {
        openGoogleAuthModal();
    } else {
        ['googleAuthModal', 'mGoogleAuthModal', 'mAuthModal'].forEach(id => {
            const m = document.getElementById(id);
            if (m) {
                m.style.display = 'flex';
                m.style.zIndex = '9999999';
                m.classList.add('show', 'active');
            }
        });
    }
    return false;
}
window.verifyServerSessionAsync = verifyServerSessionAsync;

// 멀티 탭 동기화: 다른 탭에서 로그아웃 발생 시 즉시 상태 동기화
window.addEventListener('storage', (e) => {
    if (e.key === 'pawstar_auth_event' || e.key === 'pawstar_logged_out') {
        if (localStorage.getItem('pawstar_logged_out') === 'true' || (e.newValue && e.newValue.startsWith('logout_'))) {
            window.isUserLoggedIn = false;
            window.CURRENT_USER_ID = '';
            if (typeof closeDetailModal === 'function') closeDetailModal();
        }
    }
});

document.addEventListener('DOMContentLoaded', () => {
    initEventHandlers();
});

function initEventHandlers() {
    // 회차 선택 셀렉트박스 배경색 실시간 동기화 (진행중 VS 종료)
    document.querySelectorAll('.select-custom, .m-select-custom').forEach(selectEl => {
        const updateSelectBg = () => {
            const selectedOpt = selectEl.options[selectEl.selectedIndex];
            if (selectedOpt) {
                const isInProg = selectedOpt.classList.contains('opt-in-progress') || selectedOpt.getAttribute('data-is-in-progress') === 'true' || selectedOpt.textContent.includes('진행중');
                if (isInProg) {
                    selectEl.classList.add('stat-in-progress');
                    selectEl.classList.remove('stat-closed');
                } else {
                    selectEl.classList.add('stat-closed');
                    selectEl.classList.remove('stat-in-progress');
                }
            }
        };
        updateSelectBg();
        selectEl.addEventListener('change', updateSelectBg);
    });

    const contestSelect = document.getElementById('contestSelect');
    if (contestSelect) {
        contestSelect.addEventListener('change', (e) => {
            const contestId = e.target.value;
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('contest_id', contestId);
            window.location.href = currentUrl.toString();
        });
    }

    // 단색 FontAwesome 동물 아이콘 지원 커스텀 드롭다운 핸들러
    const customDropdown = document.getElementById('customPetTypeDropdown');
    const customContestDropdown = document.getElementById('customContestDropdown');

    if (customContestDropdown) {
        const cTrigger = customContestDropdown.querySelector('.custom-contest-trigger');
        const cOptions = customContestDropdown.querySelectorAll('.custom-contest-option');

        if (cTrigger) {
            cTrigger.addEventListener('click', (e) => {
                e.stopPropagation();
                if (customDropdown) customDropdown.classList.remove('open');
                customContestDropdown.classList.toggle('open');
            });
        }

        cOptions.forEach(opt => {
            opt.addEventListener('click', (e) => {
                e.stopPropagation();
                const contestId = opt.getAttribute('data-value');
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('contest_id', contestId);
                window.location.href = currentUrl.toString();
            });
        });
    }

    if (customDropdown) {
        const trigger = customDropdown.querySelector('.custom-pet-trigger');
        const options = customDropdown.querySelectorAll('.custom-pet-option');

        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            if (customContestDropdown) customContestDropdown.classList.remove('open');
            customDropdown.classList.toggle('open');
        });

        options.forEach(opt => {
            opt.addEventListener('click', (e) => {
                const val = opt.getAttribute('data-value');
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('pet_type', val);
                window.location.href = currentUrl.toString();
            });
        });
    }

    document.addEventListener('click', (e) => {
        if (customDropdown && !customDropdown.contains(e.target)) {
            customDropdown.classList.remove('open');
        }
        if (customContestDropdown && !customContestDropdown.contains(e.target)) {
            customContestDropdown.classList.remove('open');
        }
    });

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
        let isMouseDownOnBackdrop = false;
        detailModal.addEventListener('mousedown', (e) => {
            isMouseDownOnBackdrop = (e.target === detailModal);
        });
        detailModal.addEventListener('click', (e) => {
            if (e.target === detailModal && isMouseDownOnBackdrop) closeDetailModal();
            isMouseDownOnBackdrop = false;
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

    // Note: 프로필 정보 수정 폼 제출은 profile.html 및 m_profile.html 각 템플릿에서 개별 처리함


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
                    showToast('🎉 출전 등록이 성공적으로 완료되었습니다! 🐾');
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
    if (window.currentDetailPostData && String(window.currentDetailPostData.post_id || window.currentDetailPostData.POST_ID) === String(postId)) {
        const curUserId = String(window.CURRENT_USER_ID || '').trim();
        const postOwnerId = String(window.currentDetailPostData.ENT_USER_ID || window.currentDetailPostData.user_id || '').trim();
        if (curUserId && postOwnerId && curUserId === postOwnerId) {
            if (eventType === 'like' || eventType === 'unlike' || eventType === 'toggle_like') {
                showToast('본인의 게시물은 평가에 반영할 수 없습니다.', 'warning');
                return false;
            }
        }
    }

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
                showToast(res.message || '로그인이 필요한 서비스입니다. 먼저 로그인해주세요! 🐾', 'warning');
                window.location.href = '/auth/google';
            } else if (res.is_owner || res.is_author) {
                if (eventType === 'like') {
                    showToast(res.message || '💡 본인의 게시물은 평가에 반영할 수 없습니다. 🐾', 'warning');
                }
                return false;
            } else if (res.already_viewed || res.is_ended) {
                // 이미 조회했거나 마감된 회차인 경우 조용히 무시
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
            const cardTotalScoreEl = card.querySelector('.card-total-score');
            if (scoreDisplay) {
                const cardScoreVal = Number((data && data.new_score !== undefined) ? data.new_score : ((data && data.score) || 0));
                scoreDisplay.textContent = cardScoreVal.toLocaleString();
                if (cardTotalScoreEl) {
                    cardTotalScoreEl.classList.toggle('has-score', cardScoreVal >= 1);
                }
                
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
            detailViewCountEl.textContent = Number(data.view_count || 0).toLocaleString();
        }
        const mDetailViewCountEl = document.getElementById('mDetailViewCount');
        if (mDetailViewCountEl && data.view_count !== undefined) {
            mDetailViewCountEl.textContent = Number(data.view_count || 0).toLocaleString();
        }

        if (data.new_score !== undefined || data.score !== undefined) {
            const scoreVal = Number(data.new_score !== undefined ? data.new_score : data.score);
            const scoreBadge = document.getElementById('detailScoreBadge');
            const detailScoreNumEl = document.getElementById('detailScoreNum');
            if (detailScoreNumEl) detailScoreNumEl.textContent = scoreVal.toLocaleString();
            if (scoreBadge) {
                if (scoreVal >= 1) {
                    scoreBadge.style.background = '#fefce8';
                    scoreBadge.style.borderColor = '#fde047';
                    scoreBadge.style.color = '#d97706';
                    scoreBadge.style.boxShadow = '0 3px 10px rgba(234, 179, 8, 0.2)';
                } else {
                    scoreBadge.style.background = '#ffffff';
                    scoreBadge.style.borderColor = '#e2e8f0';
                    scoreBadge.style.color = '#94a3b8';
                    scoreBadge.style.boxShadow = 'none';
                }
            }
        }
        if (eventType === 'view' || data.is_viewed !== undefined || data.view_count !== undefined) {
            const isUserLoggedIn = !!(window.isUserLoggedIn || window.CURRENT_USER_ID);
            const curUserId = String(window.CURRENT_USER_ID || '').trim();
            const postOwnerId = String((window.currentDetailPostData || {}).ENT_USER_ID || (window.currentDetailPostData || {}).user_id || '').trim();
            const isMine = !!(curUserId && postOwnerId && curUserId === postOwnerId);
            const isViewAct = isUserLoggedIn && !isMine && (data.is_viewed === true || data.is_viewed === undefined);

            const detailBtnViewPopup = document.getElementById('detailBtnView');
            if (detailBtnViewPopup) {
                detailBtnViewPopup.classList.toggle('active', isViewAct);
                const icon = detailBtnViewPopup.querySelector('i');
                if (icon) icon.className = isViewAct ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
            }
            if (card) {
                const btnView = card.querySelector('.btn-view');
                if (btnView) {
                    btnView.classList.toggle('active', isViewAct);
                    const icon = btnView.querySelector('i');
                    if (icon) icon.className = isViewAct ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
                }
            }
        }
        const dLike = document.getElementById('detailLikeCount');
        if (dLike && data && data.like_count !== undefined) dLike.textContent = Number(data.like_count || 0).toLocaleString();
        if (data && data.is_liked !== undefined) {
            const detailBtnLike = document.getElementById('detailBtnLike');
            const detailHeartLikeBtn = document.getElementById('detailHeartLikeBtn');
            const detailHeartIcon = document.getElementById('detailHeartIcon');
            if (detailBtnLike) {
                detailBtnLike.classList.toggle('active', !!data.is_liked);
                const icon = detailBtnLike.querySelector('i');
                if (icon) icon.className = data.is_liked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
            }
            if (detailHeartLikeBtn) {
                detailHeartLikeBtn.classList.toggle('active', !!data.is_liked);
            }
            if (detailHeartIcon) {
                detailHeartIcon.className = data.is_liked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
                detailHeartIcon.style.color = '#e11d48';
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

/** 토스트 메시지 팝업 대신 alert 팝업으로 출력 */
function showToast(message) {
    if (!message) return;
    alert(message);
}

// 전역 post 데이터 레지스트리
if (!window.postsDataStore) {
    window.postsDataStore = {};
}

/**
 * PC 상세보기 모달 스크롤 100% 최상단 리셋 헬퍼
 */
function resetPcModalScroll() {
    const modal = document.getElementById('postDetailModal');
    if (!modal) return;
    modal.scrollTop = 0;
    const targets = [
        modal.querySelector('.detail-info-container'),
        modal.querySelector('.detail-modal-content'),
        modal.querySelector('.detail-modal-body'),
        document.getElementById('detailCommentList'),
        document.querySelector('.detail-info-container')
    ];
    targets.forEach(el => {
        if (el) {
            el.scrollTop = 0;
        }
    });
}
window.resetPcModalScroll = resetPcModalScroll;

/**
 * 게시물 상세 레이어 팝업 모달 띄우기
 */
async function openDetailModal(post, isHallOfFame = false) {
    if (!ensureLoggedIn()) {
        return;
    }
    const isServerSessionAlive = await verifyServerSessionAsync();
    if (!isServerSessionAlive) {
        return;
    }

    const modal = document.getElementById('postDetailModal');
    if (!modal || !post) return;
    modal.style.display = '';

    // 객체 데이터 속성 표준화
    post.post_id = post.post_id || post.POST_ID || ((post.CONTEST_ROUND || post.contest_id) && (post.ROUND_NO || post.round_no) ? `${post.CONTEST_ROUND || post.contest_id}_${post.ROUND_NO || post.round_no}` : (post.ROUND_NO || post.round_no));
    post.title = post.title || post.TITLE || '';
    post.content = post.content || post.CONTS || post.conts || '';
    post.score = post.score !== undefined ? post.score : (post.SCORE !== undefined ? post.SCORE : 0);
    post.created_at = post.created_at || post.ENT_DT || '';

    // 최신 메모리 데이터 객체 및 전역 포인터 즉시 동기화
    window.currentDetailPostData = post;
    window.currentDetailPostId = post.post_id;
    if (!window.postsDataStore[post.post_id]) {
        window.postsDataStore[post.post_id] = Object.assign({}, post);
    }
    post = window.postsDataStore[post.post_id];

    // 모달 및 스크롤 영역 최상단 스크롤 초기화
    resetPcModalScroll();

    // 회차 종료/마감 여부 판별 (회차 번호 비교 및 온갖 마감 키 값 종합 검증)
    const pcPostRoundNum = parseInt(post.CONTEST_ROUND || post.contest_round || post.contest_id || (String(post.post_id || '').split('_')[0]) || '0', 10);
    const pcActiveRoundNum = parseInt(window.CURRENT_CONTEST_ROUND || window.ACTIVE_CONTEST_ROUND || (document.getElementById('currentActiveRound') ? document.getElementById('currentActiveRound').value : '0') || '0', 10);

    const isClosedRound = isHallOfFame || 
                          post.contest_stat === 'G001C002' || 
                          post.CONTEST_STAT === 'G001C002' || 
                          post.STATUS_CD === 'G001C002' ||
                          post.status_cd === 'G001C002' ||
                          post.is_closed === true || 
                          post.closed === true || 
                          post.is_ended === true || 
                          post.IS_ENDED === true ||
                          (pcPostRoundNum > 0 && pcActiveRoundNum > 0 && pcPostRoundNum < pcActiveRoundNum);

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
    const shareIconBtn = document.getElementById('detailShareIconBtn');
    let btnLike = document.getElementById('detailBtnLike');

    let btnViewPopup = document.getElementById('detailBtnView');
    let btnCommentPopup = document.getElementById('detailBtnComment');
    let btnSharePopup = document.getElementById('detailBtnShare');

    if (isClosedRound) {
        if (commentFormContainer) commentFormContainer.style.display = 'none';
        if (commentScoreNotice) commentScoreNotice.style.display = 'none';
        if (heartLikeBtn) heartLikeBtn.style.display = 'none';
        if (shareIconBtn) {
            shareIconBtn.style.display = 'inline-flex';
            shareIconBtn.style.pointerEvents = 'auto';
            shareIconBtn.style.cursor = 'pointer';
            shareIconBtn.onclick = function(e) {
                if (e) e.stopPropagation();
                handleShareClick();
            };
        }
        [btnViewPopup, btnLike, btnCommentPopup].forEach(el => {
            if (el) {
                el.style.display = 'flex';
                el.style.pointerEvents = 'none';
                el.style.cursor = 'default';
            }
        });
        if (btnSharePopup) {
            btnSharePopup.style.display = 'flex';
            btnSharePopup.style.pointerEvents = 'auto';
            btnSharePopup.style.cursor = 'pointer';
            btnSharePopup.onclick = function(e) {
                if (e) e.stopPropagation();
                handleShareClick();
            };
        }
    } else {
        if (commentFormContainer) commentFormContainer.style.display = 'flex';
        if (commentScoreNotice) commentScoreNotice.style.display = '';
        if (heartLikeBtn) heartLikeBtn.style.display = 'flex';
        if (shareIconBtn) shareIconBtn.style.display = 'inline-flex';
        [btnViewPopup, btnLike, btnCommentPopup, btnSharePopup].forEach(el => {
            if (el) {
                el.style.display = 'flex';
                el.style.pointerEvents = '';
                el.style.cursor = '';
            }
        });
        
        // 진행 중인 회차 팝업 시만 자동 조회수 증가 (단, 본인 게시물이 아닐 때만)
        const curUserId = String(window.CURRENT_USER_ID || '').trim();
        const postOwnerId = String(post.ENT_USER_ID || post.user_id || '').trim();
        if (!curUserId || !postOwnerId || curUserId !== postOwnerId) {
            triggerEvent(post.post_id, 'view');
        }
    }

    // 출전 포기(삭제) 버튼 제어 (진행 중인 회차는 "출전 포기", 지난 회차는 "삭제")
    const deleteBtn = document.getElementById('detailDeleteBtn');
    if (deleteBtn) {
        const currentUserId = String(window.CURRENT_USER_ID || '').trim();
        const postOwnerId = String(post.ENT_USER_ID || post.user_id || '').trim();
        if (currentUserId && postOwnerId && (currentUserId === postOwnerId || currentUserId === 'admin')) {
            deleteBtn.style.display = 'inline-flex';
            if (isClosedRound) {
                deleteBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i> 삭제';
            } else {
                deleteBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i> 출전 포기';
            }
        } else {
            deleteBtn.style.display = 'none';
        }
    }

    const cleanId = String(post.post_id);
    const rawEntId = cleanId.replace(/^\d+_/, '');
    const entUserIdVal = String(post.ENT_USER_ID || post.user_id || '').trim();
    const card = (entUserIdVal ? document.getElementById(`post-card-${entUserIdVal}`) : null) ||
                 document.getElementById(`post-card-${cleanId}`) || 
                 document.getElementById(`post-card-${rawEntId}`) ||
                 document.querySelector(`[data-post-id="${cleanId}"]`) ||
                 document.querySelector(`[data-ent-user-id="${rawEntId}"]`) ||
                 document.querySelector(`[data-ent-user-id="${cleanId}"]`);
    const curUserId = String(window.CURRENT_USER_ID || '').trim();
    const postOwnerId = entUserIdVal;
    const isMine = !!(curUserId && postOwnerId && curUserId === postOwnerId);

    const isUserLoggedIn = !!(window.isUserLoggedIn || window.CURRENT_USER_ID);
    const isViewAct = isUserLoggedIn && !isMine && (!isClosedRound || !!(post.is_viewed || (post.actions && post.actions.is_viewed) || (card && card.querySelector('.btn-view.active'))));

    if (card) {
        const btnView = card.querySelector('.btn-view');
        if (btnView) {
            btnView.classList.toggle('active', isViewAct);
            const icon = btnView.querySelector('i');
            if (icon) icon.className = isViewAct ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
        }
    }
    const detailBtnViewPopup = document.getElementById('detailBtnView');
    if (detailBtnViewPopup) {
        detailBtnViewPopup.classList.toggle('active', isViewAct);
        const icon = detailBtnViewPopup.querySelector('i');
        if (icon) icon.className = isViewAct ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
    }

    // PC 대회 정보 (제 N회 & 실제 대회명 분리 뱃지) 바인딩 함수
    const updatePcContestBadgeUI = (pObj) => {
        const pcContestBadge = document.getElementById('detailContestBadge');
        if (!pcContestBadge || !pObj) return;

        const pIsClosed = isClosedRound;

        let rawRound = pObj.CONTEST_ROUND || pObj.contest_round || pObj.contest_id;
        if (!rawRound && pObj.post_id && String(pObj.post_id).includes('_')) {
            rawRound = String(pObj.post_id).split('_')[0];
        }
        if (!rawRound) {
            const pageRoundEl = document.querySelector('.hero-round-badge') || document.querySelector('.round-badge-text') || document.getElementById('selectedContestRound');
            if (pageRoundEl) {
                let txt = pageRoundEl.innerText || pageRoundEl.textContent || '';
                let m = txt.match(/\d+/);
                if (m) rawRound = m[0];
            }
        }
        let roundNo = '1';
        if (rawRound) {
            let m = String(rawRound).match(/\d+/);
            roundNo = m ? m[0] : String(rawRound).trim();
        }
        
        let contestTitle = pObj.CONTEST_TITLE || pObj.contest_title || pObj.THEME_NM || pObj.theme_nm || pObj.CONTEST_NM || pObj.contest_nm || pObj.theme_title || '';
        if (!contestTitle) {
            const pageContestEl = document.querySelector('.hero-title') || document.querySelector('.selected-text') || document.getElementById('selectedContestTitle');
            if (pageContestEl) {
                let fullTxt = pageContestEl.innerText || pageContestEl.textContent || '';
                contestTitle = fullTxt.replace(/제\s*\d+\s*회/g, '').trim();
            }
        }
        if (!contestTitle) contestTitle = '포스타 콘테스트';

        const bStyle = pIsClosed 
            ? 'color: #475569; background: #f1f5f9; border: 1.5px solid #cbd5e1; box-shadow: 0 2px 6px rgba(100, 116, 139, 0.12);' 
            : 'color: #db2777; background: #fce7f3; border: 1.5px solid #fbcfe8; box-shadow: 0 2px 6px rgba(219, 39, 119, 0.12);';

        pcContestBadge.innerHTML = `
            <span style="font-size: 0.75rem; font-weight: 800; ${bStyle} padding: 0.22rem 0.65rem; border-radius: 14px; display: inline-flex; align-items: center; gap: 0.25rem; flex-shrink: 0;">
                제 ${roundNo}회
            </span>
            <span style="font-size: 0.8rem; font-weight: 800; background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.02em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; filter: drop-shadow(0 1px 2px rgba(124, 58, 237, 0.12));">
                ${contestTitle}
            </span>
        `;
    };

    updatePcContestBadgeUI(post);

    const imgEl = document.getElementById('detailImg');
    const imgSrc = post.popup_image_path || post.POPUP_IMAGE_PATH || post.IMAGE_PATH || post.image_path || post.media_url || 
        ((post.file_path && post.list_file_name) ? (post.file_path.endsWith('/') ? post.file_path : post.file_path + '/') + post.list_file_name : '');
    if (imgEl) {
        imgEl.style.opacity = '0';
        imgEl.style.transition = 'opacity 0.2s ease-in-out';
        imgEl.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>';
        if (imgSrc) {
            const tempImg = new Image();
            tempImg.onload = () => {
                imgEl.src = imgSrc;
                imgEl.style.opacity = '1';
            };
            tempImg.src = imgSrc;
            if (tempImg.complete) {
                imgEl.src = imgSrc;
                imgEl.style.opacity = '1';
            }
        }
    }

    // SNS_YTB 컬럼값이 있을 경우 유튜브 동영상 임베드 및 자동 재생 (재생 완료 시 대표 이미지 페이드인 복구)
    const rawYtb = (post.SNS_YTB || post.sns_ytb || '').trim();
    const ytbId = getYouTubeVideoId(rawYtb);
    setupYouTubePlayerWithEnding('detailYtbContainer', 'detailImg', ytbId, 'pcYtbFadeTimer', 'pcYtbPlayer');

    const authorImgEl = document.getElementById('detailAuthorImg');
    if (authorImgEl) authorImgEl.src = post.PROFILE_URL || post.user_profile || '/static/image/profile/default_profile.png';

    const nicknameEl = document.getElementById('detailAuthorNickname');
    if (nicknameEl) nicknameEl.textContent = post.NK_NM || post.user_nickname || '집사';

    const petTagEl = document.getElementById('detailPetTag');
    if (petTagEl) {
        let rawKind = post.KIND_NM || post.pet_type || '반려동물';
        const cleanKind = rawKind.replace(/[🐕🐈🐹🦜🐇🦔🦎🐠🦦🐾🐶🐱🐰🐟🐢🐴🐷☎️]/g, '').trim();
        
        let faIcon = 'fa-solid fa-paw';
        if (cleanKind.includes('강아지') || cleanKind.includes('개')) faIcon = 'fa-solid fa-dog';
        else if (cleanKind.includes('고양이')) faIcon = 'fa-solid fa-cat';
        else if (cleanKind.includes('햄스터') || cleanKind.includes('소동물') || cleanKind.includes('토끼') || cleanKind.includes('고슴도치') || cleanKind.includes('작은동물')) faIcon = 'fa-solid fa-otter';
        else if (cleanKind.includes('거북이') || cleanKind.includes('파충류') || cleanKind.includes('도마뱀')) faIcon = 'fa-solid fa-frog';
        else if (cleanKind.includes('어류') || cleanKind.includes('관상어') || cleanKind.includes('물고기')) faIcon = 'fa-solid fa-fish';
        else if (cleanKind.includes('앵무새') || cleanKind.includes('새') || cleanKind.includes('조류')) faIcon = 'fa-solid fa-crow';
        else if (cleanKind.includes('말') || cleanKind.includes('큰동물')) faIcon = 'fa-solid fa-horse';

        const petNm = post.PET_NM || post.pet_name || '';
        const kindHtml = `<span style="background: #ffe4e6; color: #e11d48; padding: 0.18rem 0.6rem; border-radius: 12px; font-size: 0.74rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.25rem; box-shadow: 0 2px 5px rgba(225, 29, 72, 0.08); flex-shrink: 0;"><i class="${faIcon}"></i> ${cleanKind}</span>`;
        if (petNm) {
            petTagEl.innerHTML = `${kindHtml}<span style="background: #f3e8ff; color: #7c3aed; padding: 0.18rem 0.6rem; border-radius: 12px; font-size: 0.74rem; font-weight: 700; margin-left: 0.3rem; display: inline-flex; align-items: center; gap: 0.2rem; box-shadow: 0 2px 5px rgba(124, 58, 237, 0.08); max-width: 220px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-shrink: 1;" title="${escapeHtml(petNm)}"><span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; display: inline-block; max-width: 100%;">${escapeHtml(petNm)}</span></span>`;
        } else {
            petTagEl.innerHTML = kindHtml;
        }
    }

    // 작성자 SNS 링크 동적 생성 (저장된 주소가 있는 아이콘들만 나란히 표시)
    const snsContainer = document.getElementById('detailAuthorSnsLinks');
    if (snsContainer) {
        snsContainer.innerHTML = '';
        
        const rawInst = (post.SNS_INST || post.sns_inst || '').trim();
        const rawYtb = (post.SNS_YTB || post.sns_ytb || '').trim();
        const rawFsb = (post.SNS_FSB || post.sns_fsb || '').trim();
        const rawBlg = (post.SNS_BLG || post.sns_blg || '').trim();

        const formatUrl = (url) => {
            if (!url) return '';
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                return 'https://' + url;
            }
            return url;
        };

        const snsItems = [
            { type: 'instagram', rawUrl: rawInst, icon: 'fa-brands fa-instagram', title: 'Instagram' },
            { type: 'youtube', rawUrl: rawYtb, icon: 'fa-brands fa-youtube', title: 'YouTube' },
            { type: 'facebook', rawUrl: rawFsb, icon: 'fa-brands fa-facebook-f', title: 'Facebook' },
            { type: 'blog', rawUrl: rawBlg, icon: 'fa-solid fa-blog', title: 'Blog' }
        ];

        snsItems.forEach(item => {
            if (item.rawUrl) {
                const finalUrl = formatUrl(item.rawUrl);
                const aBtn = document.createElement('a');
                aBtn.href = finalUrl;
                aBtn.target = '_blank';
                aBtn.rel = 'noopener noreferrer';
                aBtn.className = `profile-social-btn ${item.type}`;
                aBtn.title = item.title;
                aBtn.style.width = '34px';
                aBtn.style.height = '34px';
                aBtn.style.fontSize = '0.9rem';
                aBtn.style.display = 'inline-flex';
                aBtn.style.alignItems = 'center';
                aBtn.style.justifyContent = 'center';
                aBtn.style.padding = '0';
                aBtn.style.lineHeight = '1';
                aBtn.style.flexShrink = '0';
                aBtn.innerHTML = `<i class="${item.icon}"></i>`;
                snsContainer.appendChild(aBtn);
            }
        });
    }

    const updateScoreBadgeUI = (scoreVal) => {
        const num = Number(scoreVal || 0);
        const scoreBadge = document.getElementById('detailScoreBadge');
        const scoreNumEl = document.getElementById('detailScoreNum');
        if (scoreNumEl) scoreNumEl.textContent = num.toLocaleString();
        if (scoreBadge) {
            if (num >= 1) {
                scoreBadge.style.background = '#fefce8';
                scoreBadge.style.borderColor = '#fde047';
                scoreBadge.style.color = '#d97706';
                scoreBadge.style.boxShadow = '0 3px 10px rgba(234, 179, 8, 0.2)';
            } else {
                scoreBadge.style.background = '#ffffff';
                scoreBadge.style.borderColor = '#e2e8f0';
                scoreBadge.style.color = '#94a3b8';
                scoreBadge.style.boxShadow = 'none';
            }
        }
    };

    updateScoreBadgeUI(post.score || post.SCORE || 0);

    const pcTitleText = (post.title || post.TITLE || '').trim();
    let pcContentText = (post.content || post.CONTS || '').trim();
    if (post.is_post_deleted || pcTitleText === '출전자에 의해 삭제된 출전작입니다' || pcTitleText.includes('삭제된 출전작')) {
        pcContentText = '';
    }

    const titleEl = document.getElementById('detailTitle');
    if (titleEl) titleEl.textContent = pcTitleText;

    const contentEl = document.getElementById('detailContent');
    if (contentEl) contentEl.textContent = pcContentText;

    const createdAtEl = document.getElementById('detailCreatedAt');
    if (createdAtEl) createdAtEl.textContent = formatTimeAgo(post.created_at || post.ENT_DT || '');

    const viewCountVal = post.view_count !== undefined ? post.view_count : (post.VW_CNT !== undefined ? post.VW_CNT : 0);
    const likeCountVal = post.like_count !== undefined ? post.like_count : (post.LIKE_CNT !== undefined ? post.LIKE_CNT : 0);
    const commentCountVal = post.comment_count !== undefined ? post.comment_count : (post.CMT_CNT !== undefined ? post.CMT_CNT : 0);

    const viewCountEl = document.getElementById('detailViewCount');
    if (viewCountEl) viewCountEl.textContent = Number(viewCountVal || 0).toLocaleString();

    const likeCountEl = document.getElementById('detailLikeCount');
    if (likeCountEl) likeCountEl.textContent = Number(likeCountVal || 0).toLocaleString();

    const commentCountEl = document.getElementById('detailCommentCount');
    if (commentCountEl) commentCountEl.textContent = Number(commentCountVal || 0).toLocaleString();

    const shareCountEl = document.getElementById('detailShareCount');
    if (shareCountEl) shareCountEl.textContent = Number(post.share_count || 0).toLocaleString();

    updatePcContestBadgeUI(post);

    const isCommented = (post.actions && post.actions.is_commented) || post.is_commented || false;
    window.currentDetailPost = post;
    window.currentDetailPostData = post;
    window.currentDetailPostIsCommented = isCommented;

    const curUserIdVal = String(window.CURRENT_USER_ID || '').trim();
    const postOwnerIdVal = String(post.ENT_USER_ID || post.user_id || '').trim();
    const isMineVal = !!(curUserIdVal && postOwnerIdVal && curUserIdVal === postOwnerIdVal);
    const isUserLoggedInVal = !!(window.isUserLoggedIn || window.CURRENT_USER_ID);
    const isViewActiveVal = isUserLoggedInVal && !isMineVal && (!isClosedRound || !!((card && card.querySelector('.btn-view.active')) || (post.actions && post.actions.is_viewed) || post.is_viewed));

    btnViewPopup = document.getElementById('detailBtnView');
    if (btnViewPopup) {
        btnViewPopup.classList.toggle('active', isViewActiveVal);
        const icon = btnViewPopup.querySelector('i');
        if (icon) icon.className = isViewActiveVal ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
    }

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

    // 참가번호 뱃지 바인딩 (이미지 좌측 하단)
    const entryNoEl = document.getElementById('detailEntryNoText');
    const entryNoBadge = document.getElementById('detailEntryNoBadge');
    const roundNoVal = post.ROUND_NO || post.round_no || (post.post_id && String(post.post_id).includes('_') ? String(post.post_id).split('_')[1] : null);
    if (entryNoBadge && entryNoEl) {
        if (roundNoVal) {
            entryNoEl.textContent = `참가 ${roundNoVal}번`;
            entryNoBadge.style.display = 'inline-flex';
        } else {
            entryNoBadge.style.display = 'none';
        }
    }

    // 랭킹 / 수상 배지 채우기 (오직 실물 메달/배지 이미지들만 전체부문 -> 품종부문 순서로 가로 나란히 표시)
    const medalsLeftEl = document.getElementById('detailMedalsLeft');
    const badgeEl = document.getElementById('detailRankBadge');

    if (medalsLeftEl) medalsLeftEl.innerHTML = '';

    let awardsData = (post.awards && post.awards.length > 0) ? post.awards : [];
    if (awardsData.length === 0) {
        const cd = post.award_cd || post.AWARD_CD;
        let rk = post.ranking || post.RANKING || post.rank || post.final_rank || post.AWARD_RANK || post.rank_no;
        if (!rk && (isHallOfFame || post.is_closed) && post.round_no && (post.round_no == 1 || post.round_no == 2 || post.round_no == 3)) {
            rk = Number(post.round_no);
        }

        if (cd) {
            const nm = post.award_nm || post.AWARD_NM || '수상 메달';
            const part = post.award_part || post.AWARD_PART || (cd.startsWith('P001') ? 'G002P001' : 'G002P002');
            const img = post.badge_img || post.badge_image_path || post.BADGE_IMAGE_PATH || `/static/image/badge/${cd}.png`;
            awardsData = [{ award_cd: cd, award_nm: nm, award_part: part, badge_img: img, ranking: rk }];
        } else if (rk && (rk == 1 || rk == 2 || rk == 3)) {
            const rkNum = Number(rk);
            const cdMap = { 1: 'P001A101', 2: 'P001A102', 3: 'P001A103' };
            const nmMap = { 1: '슈퍼스타', 2: '브라이트스타', 3: '라이징스타' };
            const autoCd = cdMap[rkNum];
            const autoNm = nmMap[rkNum];
            awardsData = [{
                award_cd: autoCd,
                award_nm: autoNm,
                award_part: 'G002P001',
                badge_img: `/static/image/badge/${autoCd}.png`,
                ranking: rkNum
            }];
        }
    }

    if (awardsData.length > 0) {
        const sortedAwards = [...awardsData].sort((a, b) => {
            const cdA = String(a.award_cd || a.AWARD_CD || '');
            const nmA = String(a.award_nm || a.AWARD_NM || '');
            const isStarA = (cdA.includes('P001') || nmA.includes('슈퍼') || nmA.includes('라이징') || nmA.includes('브라이트'));
            const cdB = String(b.award_cd || b.AWARD_CD || '');
            const nmB = String(b.award_nm || b.AWARD_NM || '');
            const isStarB = (cdB.includes('P001') || nmB.includes('슈퍼') || nmB.includes('라이징') || nmB.includes('브라이트'));
            if (isStarA && !isStarB) return -1;
            if (!isStarA && isStarB) return 1;
            return 0;
        });

        const kindNm = post.KIND_NM || post.pet_type || '';
        let petIconClass = 'fa-solid fa-paw';
        if (kindNm.includes('강아지') || kindNm.includes('개')) petIconClass = 'fa-solid fa-dog';
        else if (kindNm.includes('고양이')) petIconClass = 'fa-solid fa-cat';
        else if (kindNm.includes('햄스터') || kindNm.includes('소동물') || kindNm.includes('토끼') || kindNm.includes('고슴도치')) petIconClass = 'fa-solid fa-otter';
        else if (kindNm.includes('거북이') || kindNm.includes('파충류') || kindNm.includes('도마뱀')) petIconClass = 'fa-solid fa-frog';
        else if (kindNm.includes('어류') || kindNm.includes('관상어') || kindNm.includes('물고기')) petIconClass = 'fa-solid fa-fish';
        else if (kindNm.includes('앵무새') || kindNm.includes('새') || kindNm.includes('조류')) petIconClass = 'fa-solid fa-crow';
        else if (kindNm.includes('말') || kindNm.includes('큰동물')) petIconClass = 'fa-solid fa-horse';

        if (medalsLeftEl) {
            let leftHtml = '';
            sortedAwards.forEach(aw => {
                const awardCdStr = String(aw.award_cd || aw.AWARD_CD || '');
                const awardNmStr = String(aw.award_nm || aw.AWARD_NM || '');
                const awRank = aw.ranking || aw.RANKING;
                let displayTitle = aw.award_nm || aw.AWARD_NM || '';

                if (awardCdStr.includes('P001A101')) displayTitle = '슈퍼스타';
                else if (awardCdStr.includes('P001A102')) displayTitle = '브라이트스타';
                else if (awardCdStr.includes('P001A103')) displayTitle = '라이징스타';
                else if (awardNmStr.includes('슈퍼')) displayTitle = '슈퍼스타';
                else if (awardNmStr.includes('브라이트')) displayTitle = '브라이트스타';
                else if (awardNmStr.includes('라이징')) displayTitle = '라이징스타';
                else if (awardCdStr.includes('P002A901')) displayTitle = '패밀리 1위';
                else if (awardCdStr.includes('P002A902')) displayTitle = '패밀리 2위';
                else if (awardCdStr.includes('P002A903')) displayTitle = '패밀리 3위';
                else if (awRank) displayTitle = `패밀리 ${awRank}위`;

                const badgeImgSrc = aw.badge_img || aw.badge_image_path || aw.BADGE_IMAGE_PATH || (awardCdStr ? `/static/image/badge/${awardCdStr}.png` : '');
                if (badgeImgSrc) {
                    leftHtml += `<img src="${badgeImgSrc}" class="hall-medal-effect badge-zoomable-img" data-badge-src="${badgeImgSrc}" data-badge-title="${displayTitle}" style="width: 64px; height: 64px; object-fit: contain; flex-shrink: 0; pointer-events: auto; cursor: pointer;" alt="${displayTitle}">`;
                }
            });
            medalsLeftEl.innerHTML = leftHtml;
        }

        if (badgeEl) {
            badgeEl.style.justifyContent = 'flex-end';
            badgeEl.style.right = '0.75rem';
            badgeEl.style.left = 'auto';

            let rightHtml = '<div style="display: flex; align-items: center; justify-content: flex-end; gap: 0.45rem; flex-wrap: wrap;">';
            sortedAwards.forEach(aw => {
                const awardCdStr = String(aw.award_cd || aw.AWARD_CD || '');
                const awardNmStr = String(aw.award_nm || aw.AWARD_NM || '');
                const badgeImgSrc = aw.badge_img || aw.badge_image_path || aw.BADGE_IMAGE_PATH || (awardCdStr ? `/static/image/badge/${awardCdStr}.png` : '');
                const awRank = aw.ranking || aw.RANKING;

                if (awardCdStr.includes('P001A101') || (!awardCdStr && awardNmStr.includes('슈퍼'))) {
                    rightHtml += `<div class="winner-title-badge superstar-badge" style="position: relative; top: 0; right: 0; margin: 0; font-size: 1.05rem; padding: 0.45rem 1.05rem; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '슈퍼스타');"><i class="fa-solid fa-star"></i> <span>슈퍼스타</span></div>`;
                } else if (awardCdStr.includes('P001A102') || (!awardCdStr && awardNmStr.includes('브라이트'))) {
                    rightHtml += `<div class="winner-title-badge brightstar-badge" style="position: relative; top: 0; right: 0; margin: 0; font-size: 1.05rem; padding: 0.45rem 1.05rem; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '브라이트스타');"><i class="fa-solid fa-star"></i> <span>브라이트스타</span></div>`;
                } else if (awardCdStr.includes('P001A103') || (!awardCdStr && awardNmStr.includes('라이징'))) {
                    rightHtml += `<div class="winner-title-badge risingstar-badge" style="position: relative; top: 0; right: 0; margin: 0; font-size: 1.05rem; padding: 0.45rem 1.05rem; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '라이징스타');"><i class="fa-solid fa-star"></i> <span>라이징스타</span></div>`;
                } else {
                    const titleText = awRank ? `패밀리 ${awRank}위` : '패밀리';
                    rightHtml += `<div class="winner-title-badge family-badge" style="position: relative; top: 0; right: 0; margin: 0; font-size: 1.05rem; padding: 0.45rem 1.05rem; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '${titleText}');"><span class="pet-emoji-icon"><i class="${petIconClass}"></i></span> <span>${titleText}</span></div>`;
                }
            });
            rightHtml += '</div>';
            badgeEl.innerHTML = rightHtml;
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
                else if (kindNm.includes('햄스터') || kindNm.includes('소동물') || kindNm.includes('토끼') || kindNm.includes('고슴도치')) petIconClass = 'fa-solid fa-otter';
                else if (kindNm.includes('거북이') || kindNm.includes('파충류') || kindNm.includes('도마뱀')) petIconClass = 'fa-solid fa-frog';
                else if (kindNm.includes('어류') || kindNm.includes('관상어') || kindNm.includes('물고기')) petIconClass = 'fa-solid fa-fish';
                else if (kindNm.includes('앵무새') || kindNm.includes('새') || kindNm.includes('조류')) petIconClass = 'fa-solid fa-crow';
                else if (kindNm.includes('말') || kindNm.includes('큰동물')) petIconClass = 'fa-solid fa-horse';

                const urlParams = new URLSearchParams(window.location.search);
                const currentPetType = urlParams.get('pet_type') || 'all';
                const isFamily = (currentPetType && currentPetType !== 'all');
                const catPrefix = isFamily ? '패밀리 ' : '전체 ';
                const iconClass = isFamily ? petIconClass : 'fa-solid fa-medal';
                const prefix = catPrefix + (post.is_co_rank ? '공동 ' : '');
                const rankTitle = `${prefix}${post.rank_candidate}위 후보`;
                if (isFamily) {
                    badgeEl.innerHTML = `<div class="winner-title-badge family-badge" style="position: relative; top: 0; left: 0; right: auto; margin: 0; font-size: 1.05rem; padding: 0.45rem 1.05rem; font-weight: 800;"><span class="pet-emoji-icon"><i class="${petIconClass}"></i></span> <span>${rankTitle}</span></div>`;
                } else {
                    if (post.rank_candidate == 1) {
                        badgeEl.innerHTML = `<div class="rank-ribbon rank-1" style="position: relative; top: 0; left: 0; right: auto; margin: 0; font-size: 1.05rem; padding: 0.45rem 1.05rem; font-weight: 800;"><i class="fa-solid fa-medal"></i> <span>${rankTitle}</span></div>`;
                    } else if (post.rank_candidate == 2) {
                        badgeEl.innerHTML = `<div class="rank-ribbon rank-2" style="position: relative; top: 0; left: 0; right: auto; margin: 0; font-size: 1.05rem; padding: 0.45rem 1.05rem; font-weight: 800;"><i class="fa-solid fa-medal"></i> <span>${rankTitle}</span></div>`;
                    } else if (post.rank_candidate == 3) {
                        badgeEl.innerHTML = `<div class="rank-ribbon rank-3" style="position: relative; top: 0; left: 0; right: auto; margin: 0; font-size: 1.05rem; padding: 0.45rem 1.05rem; font-weight: 800;"><i class="fa-solid fa-medal"></i> <span>${rankTitle}</span></div>`;
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
        const heartBtnPopup = document.getElementById('detailHeartLikeBtn');
        const heartIconPopup = document.getElementById('detailHeartIcon');
        const btnLikePopup = document.getElementById('detailBtnLike');

        if (btnLikePopup) {
            btnLikePopup.classList.toggle('active', !!likedState);
            const icon = btnLikePopup.querySelector('i');
            if (icon) icon.className = likedState ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
        }
        if (heartBtnPopup) {
            heartBtnPopup.classList.toggle('active', !!likedState);
        }
        if (heartIconPopup) {
            heartIconPopup.className = likedState ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
            heartIconPopup.style.color = '#e11d48';
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

    const updatePopupViewUI = (isViewedState) => {
        const btnView = document.getElementById('detailBtnView');
        const curUserId = String(window.CURRENT_USER_ID || '').trim();
        const postOwnerId = String((window.currentDetailPostData || {}).ENT_USER_ID || (window.currentDetailPostData || {}).user_id || '').trim();
        const isMine = !!(curUserId && postOwnerId && curUserId === postOwnerId);
        const isUserLoggedIn = !!(window.isUserLoggedIn || window.CURRENT_USER_ID);
        const isViewAct = isUserLoggedIn && !isMine && !!isViewedState;
        if (btnView) {
            btnView.classList.toggle('active', isViewAct);
            const icon = btnView.querySelector('i');
            if (icon) icon.className = isViewAct ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
        }
    };

    const updatePopupShareUI = (sharedState) => {
        const btnShare = document.getElementById('detailBtnShare');
        const iconShare = document.getElementById('detailShareIconBtn');
        if (btnShare) btnShare.classList.toggle('active', !!sharedState);
        if (iconShare) iconShare.classList.toggle('active', !!sharedState);
    };

    // 팝업 열릴 때 초기 상태 동기화
    updatePopupLikeUI(isLiked);
    updatePopupCommentUI(!!isCommented);
    updatePopupViewUI(!!(post.is_viewed || (post.actions && post.actions.is_viewed)));
    updatePopupShareUI(!!(post.is_shared || (post.actions && post.actions.is_shared)));

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
                if (data.actions.is_shared !== undefined) {
                    updatePopupShareUI(!!data.actions.is_shared);
                }
                if (data.actions.is_viewed !== undefined) {
                    updatePopupViewUI(!!data.actions.is_viewed);
                }
            }
        })
        .catch(err => {
            console.error(err);
            updatePopupLikeUI(isLiked);
        });

    const toggleLikeHandler = async () => {
        const curUserId = String(window.CURRENT_USER_ID || '').trim();
        const postOwnerId = String(post.ENT_USER_ID || post.user_id || '').trim();
        if (curUserId && postOwnerId && curUserId === postOwnerId) {
            showToast('본인의 게시물은 평가에 반영할 수 없습니다.', 'warning');
            return;
        }

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

    // PC 상세보기 팝업 우측 스크롤바 동적 감지 (스크롤 안 하면 100% 완전 숨김)
    const detailInfoScrollContainer = modal.querySelector('.detail-info-container');
    if (detailInfoScrollContainer) {
        detailInfoScrollContainer.classList.remove('is-scrolling');
        let scrollTimer = null;
        detailInfoScrollContainer.onscroll = () => {
            detailInfoScrollContainer.classList.add('is-scrolling');
            if (scrollTimer) clearTimeout(scrollTimer);
            scrollTimer = setTimeout(() => {
                detailInfoScrollContainer.classList.remove('is-scrolling');
            }, 800);
        };
    }

    modal.classList.add('show');
    document.body.style.overflow = 'hidden';

    // 팝업 show 활성화 틱 및 애니메이션 후 스크롤 100% 최상단 보정
    resetPcModalScroll();
    requestAnimationFrame(() => {
        resetPcModalScroll();
        setTimeout(resetPcModalScroll, 0);
        setTimeout(resetPcModalScroll, 50);
        setTimeout(resetPcModalScroll, 150);
    });
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

/** 토스트 메시지 팝업 대신 alert 팝업으로 출력 */
function showToast(message) {
    if (!message) return;
    alert(message);
}

// 전역 post 데이터 레지스트리
if (!window.postsDataStore) {
    window.postsDataStore = {};
}



function closeDetailModal() {
    if (window.pcYtbFadeTimer) {
        clearTimeout(window.pcYtbFadeTimer);
        window.pcYtbFadeTimer = null;
    }
    if (window.pcYtbFadeTimer_loop) {
        clearTimeout(window.pcYtbFadeTimer_loop);
        window.pcYtbFadeTimer_loop = null;
    }
    if (window.pcYtbPlayer && typeof window.pcYtbPlayer.destroy === 'function') {
        try { window.pcYtbPlayer.destroy(); } catch(e) {}
        window.pcYtbPlayer = null;
    }
    const modal = document.getElementById('postDetailModal');
    if (modal) {
        modal.classList.remove('show', 'active');
        modal.style.display = '';
        resetPcModalScroll();
        document.body.style.overflow = '';
    }
    const imgEl = document.getElementById('detailImg');
    if (imgEl) {
        imgEl.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>';
        imgEl.style.opacity = '1';
    }
    const ytbContainer = document.getElementById('detailYtbContainer');
    if (ytbContainer) {
        ytbContainer.innerHTML = '';
        ytbContainer.style.display = 'none';
    }
}
window.closeDetailModal = closeDetailModal;
window.closePostDetailModal = closeDetailModal;

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
    
    const rawCurrentId = String(window.CURRENT_USER_ID || '');
    const currentUserId = rawCurrentId.split('_post_')[0];
    const currentNickname = window.CURRENT_USER_NICKNAME;

    listEl.innerHTML = comments.map(c => {
        const rawCUserId = String(c.user_id || c.USER_ID || c.CMT_USER_ID || '');
        const cUserId = rawCUserId.split('_post_')[0];
        const cNickname = c.user_nickname || c.NK_NM;
        const isMine = c.is_mine === true || (currentUserId && cUserId && cUserId === currentUserId) || (currentNickname && cNickname && cNickname === currentNickname);

        const deleteBtnHtml = isMine ? `
            <button onclick="deleteDetailComment('${c.CMT_USER_ID || c.user_id || c.USER_ID}')" style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); color: #ef4444; font-size: 0.72rem; cursor: pointer; padding: 0.15rem 0.45rem; border-radius: 6px; font-weight: 700; transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.25rem;" title="댓글 삭제">
                <i class="fa-solid fa-trash-can" style="font-size: 0.68rem;"></i> 삭제
            </button>
        ` : '';

        return `
            <div style="background: #f8fafc; border: 1px solid var(--border-light); border-radius: 12px; padding: 0.5rem 0.75rem; font-size: 0.82rem; display: flex; flex-direction: column; gap: 0.2rem;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <a href="${cUserId ? `/profile?user_id=${encodeURIComponent(cUserId)}` : 'javascript:void(0)'}" style="display: flex; align-items: center; gap: 0.35rem; font-weight: 800; color: var(--text-primary); text-decoration: none; cursor: ${cUserId ? 'pointer' : 'default'}; transition: opacity 0.2s;" ${cUserId ? `title="${escapeHtml(cNickname || '집사')} 님의 프로필 보기"` : ''} onmouseover="if('${cUserId}') this.style.opacity='0.75'" onmouseout="this.style.opacity='1'">
                        <img src="${c.user_profile || '/static/image/profile/default_profile.png'}" style="width: 18px; height: 18px; border-radius: 50%; object-fit: cover;">
                        <span>${escapeHtml(c.user_nickname || '집사')}</span>
                    </a>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 0.72rem; color: var(--text-muted);">${formatTimeAgo(c.created_at || c.ENT_DT || c.CMT_DT || '')}</span>
                        ${deleteBtnHtml}
                    </div>
                </div>
                <div style="color: var(--text-secondary); font-weight: 500; word-break: break-all; padding-left: 1.4rem;">
                    ${escapeHtml(c.content)}
                </div>
            </div>
        `;
    }).join('');
}

function deleteDetailComment(cmtUserId) {
    if (!window.currentDetailPostId) return;
    if (!confirm('작성하신 댓글을 삭제하시겠습니까?')) return;

    fetch(`/api/comments/${window.currentDetailPostId}/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cmt_user_id: cmtUserId })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            showToast(data.message || '댓글 삭제 실패', 'warning');
            return;
        }
        showToast('댓글이 삭제되었습니다.', 'info');
        loadComments(window.currentDetailPostId);
        
        // 차감된 수치 및 점수 UI 실시간 반영
        const finalScore = Number(data.score !== undefined ? data.score : (data.new_score !== undefined ? data.new_score : (data.event_res ? data.event_res.score : 0)));
        const finalView = (data.view_count !== undefined ? data.view_count : (data.event_res ? data.event_res.view_count : undefined));
        const finalLike = (data.like_count !== undefined ? data.like_count : (data.event_res ? data.event_res.like_count : undefined));
        const finalComment = (data.comment_count !== undefined ? data.comment_count : (data.event_res ? data.event_res.comment_count : undefined));

        const postId = window.currentDetailPostId;
        
        window.currentDetailPostIsCommented = false;
        if (window.currentDetailPost) {
            window.currentDetailPost.is_commented = false;
            if (window.currentDetailPost.actions) window.currentDetailPost.actions.is_commented = false;
        }

        const btnComment = document.getElementById('detailBtnComment');
        if (btnComment) {
            btnComment.classList.remove('active');
            const icon = btnComment.querySelector('i');
            if (icon) icon.className = 'fa-regular fa-comment';
        }

        if (postId) {
            if (window.postsDataStore && window.postsDataStore[postId]) {
                const storeItem = window.postsDataStore[postId];
                if (finalComment !== undefined) storeItem.comment_count = finalComment;
                if (finalComment !== undefined) storeItem.CMT_CNT = finalComment;
                if (finalScore !== undefined) {
                    storeItem.score = finalScore;
                    storeItem.SCORE = finalScore;
                }
                storeItem.is_commented = false;
                if (storeItem.actions) storeItem.actions.is_commented = false;
            }

            const commentCountEl = document.getElementById('detailCommentCount');
            if (commentCountEl && finalComment !== undefined) {
                commentCountEl.textContent = Number(finalComment || 0).toLocaleString();
            }

            const viewCountEl = document.getElementById('detailViewCount');
            if (viewCountEl && finalView !== undefined) {
                viewCountEl.textContent = Number(finalView || 0).toLocaleString();
            }

            const likeCountEl = document.getElementById('detailLikeCount');
            if (likeCountEl && finalLike !== undefined) {
                likeCountEl.textContent = Number(finalLike || 0).toLocaleString();
            }

            const scoreNumEl = document.getElementById('detailScoreNum');
            if (scoreNumEl && finalScore !== undefined) {
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
                    btnCardComment.classList.remove('active');
                    const icon = btnCardComment.querySelector('i');
                    if (icon) icon.className = 'fa-regular fa-comment';
                }

                const cardComment = card.querySelector('.comment-count');
                if (cardComment && finalComment !== undefined) {
                    cardComment.textContent = finalComment;
                }
                const cardScore = card.querySelector('.score-num');
                if (cardScore && finalScore !== undefined) {
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
    })
    .catch(err => {
        console.error('댓글 삭제 오류:', err);
        showToast('댓글 삭제 중 오류가 발생했습니다.', 'error');
    });
}

function submitDetailComment() {
    const inputEl = document.getElementById('detailCommentInput');
    if (!inputEl || !window.currentDetailPostId) return;

    if (window.currentDetailPostData) {
        const curUserId = String(window.CURRENT_USER_ID || '').trim();
        const postOwnerId = String(window.currentDetailPostData.ENT_USER_ID || window.currentDetailPostData.user_id || '').trim();
        if (curUserId && postOwnerId && curUserId === postOwnerId) {
            showToast('💡 본인이 등록한 게시물에는 댓글을 남기실 수 없습니다. 🐾', 'warning');
            return;
        }
    }

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
                commentCountEl.textContent = Number(finalComment || 0).toLocaleString();
            }

            const viewCountEl = document.getElementById('detailViewCount');
            if (viewCountEl && finalView !== undefined) {
                viewCountEl.textContent = Number(finalView || 0).toLocaleString();
            }

            const likeCountEl = document.getElementById('detailLikeCount');
            if (likeCountEl && finalLike !== undefined) {
                likeCountEl.textContent = Number(finalLike || 0).toLocaleString();
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

async function copyPostShareUrl(contestRound, roundNo, shareSn) {
    if (contestRound === 'None' || contestRound === 'undefined' || contestRound === 'null') contestRound = null;
    if (roundNo === 'None' || roundNo === 'undefined' || roundNo === 'null') roundNo = null;
    if (shareSn === 'None' || shareSn === 'undefined' || shareSn === 'null') shareSn = null;

    if (!contestRound || !roundNo) {
        if (window.currentDetailPostData) {
            const p = window.currentDetailPostData;
            contestRound = p.contest_id || p.CONTEST_ROUND || contestRound;
            roundNo = p.round_no || p.ROUND_NO || roundNo;
            shareSn = p.share_sn || p.SHARE_SN || shareSn;
        }
        if ((!contestRound || !roundNo) && window.currentDetailPostId) {
            const parts = String(window.currentDetailPostId).split('_');
            if (parts.length >= 2) {
                contestRound = parts[0];
                roundNo = parts[1];
            }
        }
    }

    let isClosedContest = false;
    if (window.currentDetailPostData) {
        const p = window.currentDetailPostData;
        if (p.is_closed || p.closed || p.STATUS_CD === 'G001C002' || p.CONTEST_STAT === 'G001C002') {
            isClosedContest = true;
        }
    }

    let shareUrl = '';
    if (contestRound && roundNo) {
        try {
            const res = await fetch(`/api/contest/share_url?contest_round=${contestRound}&round_no=${roundNo}`);
            const data = await res.json();
            if (data.success && data.share_url) {
                shareUrl = data.share_url;
                if (data.is_closed) {
                    isClosedContest = true;
                }
            }
        } catch (e) {
            console.error('copyPostShareUrl API error:', e);
        }
    }

    if (!shareUrl && contestRound && roundNo) {
        const sn = shareSn || 'S-UUID';
        shareUrl = `${window.location.origin}/share?contest_round=${contestRound}&round_no=${roundNo}&share_sn=${sn}`;
    }

    if (!shareUrl) {
        shareUrl = window.location.href;
    }

    const alertMsg = isClosedContest 
        ? '🔗 전용 공유주소가 복사되었습니다!' 
        : '🔗 전용 공유주소가 복사되었습니다!\n이 주소로 접근해 회원가입이나 로그인 시 공유점수 +10점이 적립됩니다.';

    try {
        await navigator.clipboard.writeText(shareUrl);
        alert(alertMsg);
    } catch (err) {
        const tempInput = document.createElement('input');
        tempInput.value = shareUrl;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        alert(alertMsg);
    }
}

async function handleShareClick() {
    if (!window.currentDetailPostId) return;
    if (window.currentDetailPostData) {
        const p = window.currentDetailPostData;
        const cRound = p.contest_id || p.CONTEST_ROUND;
        const rNo = p.round_no || p.ROUND_NO;
        const sSn = p.share_sn || p.SHARE_SN;
        await copyPostShareUrl(cRound, rNo, sSn);
    } else {
        await copyPostShareUrl();
    }
}

window.copyPostShareUrl = copyPostShareUrl;

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

    // 2. 모든 출전 신청 링크/버튼 클릭 시 비로그인이면 즉시 반투명 구글 인증 모달 팝업 표출
    const uploadLinks = document.querySelectorAll('a[href="/upload"], a[href="/m/upload"], .btn-hero-cta, .m-btn-hero-cta');
    uploadLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const hasProfileUI = document.querySelector('.profile-dropdown') || document.querySelector('.m-nav-profile') || document.querySelector('a[href="/logout"]') || document.querySelector('a[href="/api/logout"]');
            const isLoggedIn = window.isUserLoggedIn || !!hasProfileUI;

            if (!isLoggedIn) {
                e.preventDefault();
                e.stopPropagation();
                if (typeof openGoogleAuthModal === 'function') {
                    openGoogleAuthModal();
                } else {
                    const m = document.getElementById('googleAuthModal') || document.getElementById('mAuthModal');
                    if (m) {
                        m.style.display = 'flex';
                        m.style.zIndex = '999999';
                        m.classList.add('show', 'active');
                    }
                }
            }
        });
    });
});

function openGoogleLoginModal() {
    if (typeof openGoogleAuthModal === 'function') {
        openGoogleAuthModal();
    } else {
        const m = document.getElementById('googleAuthModal') || document.getElementById('mAuthModal');
        if (m) {
            m.style.display = 'flex';
            m.style.zIndex = '999999';
            m.classList.add('show', 'active');
        }
    }
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

// 🏆 메달 / 배지 중앙 확대 라이트박스 팝업 컨트롤러 (Bulletproof Body Lightbox)
function openBadgeZoomModal(imgSrc, title = '수상 메달 / 배지', petIcon = '') {
    if (!imgSrc) return;

    // 메달/배지가 확대되어 표시된 경우 문구 및 글자 색상 분리 적용
    let displayHtml = '';
    let rawTitle = title || '수상 메달 / 배지';

    const getIconClassFromKind = (kindNm) => {
        if (!kindNm) return 'fa-solid fa-paw';
        if (kindNm.includes('강아지') || kindNm.includes('개')) return 'fa-solid fa-dog';
        if (kindNm.includes('고양이')) return 'fa-solid fa-cat';
        if (kindNm.includes('햄스터') || kindNm.includes('소동물') || kindNm.includes('토끼') || kindNm.includes('고슴도치') || kindNm.includes('작은동물')) return 'fa-solid fa-otter';
        if (kindNm.includes('거북이') || kindNm.includes('파충류') || kindNm.includes('도마뱀')) return 'fa-solid fa-frog';
        if (kindNm.includes('어류') || kindNm.includes('관상어') || kindNm.includes('물고기')) return 'fa-solid fa-fish';
        if (kindNm.includes('앵무새') || kindNm.includes('새') || kindNm.includes('조류')) return 'fa-solid fa-crow';
        if (kindNm.includes('말') || kindNm.includes('큰동물')) return 'fa-solid fa-horse';
        return 'fa-solid fa-paw';
    };

    if (rawTitle.includes('슈퍼스타')) {
        displayHtml = '<span style="margin-right: 0.45rem; color: #fef08a; font-size: 1.1em; display: inline-flex; align-items: center; justify-content: center; filter: none !important;"><i class="fa-solid fa-star"></i></span><span style="color: #e2e8f0; font-weight: 700; margin-right: 0.35rem;">전체 1위</span><span style="color: #fef08a; font-weight: 900; text-shadow: 0 0 12px rgba(254, 240, 138, 0.85);">슈퍼스타</span>';
    } else if (rawTitle.includes('브라이트스타')) {
        displayHtml = '<span style="margin-right: 0.45rem; color: #7dd3fc; font-size: 1.1em; display: inline-flex; align-items: center; justify-content: center; filter: none !important;"><i class="fa-solid fa-star"></i></span><span style="color: #e2e8f0; font-weight: 700; margin-right: 0.35rem;">전체 2위</span><span style="color: #7dd3fc; font-weight: 900; text-shadow: 0 0 12px rgba(125, 211, 252, 0.85);">브라이트스타</span>';
    } else if (rawTitle.includes('라이징스타')) {
        displayHtml = '<span style="margin-right: 0.45rem; color: #a3e635; font-size: 1.1em; display: inline-flex; align-items: center; justify-content: center; filter: none !important;"><i class="fa-solid fa-star"></i></span><span style="color: #e2e8f0; font-weight: 700; margin-right: 0.35rem;">전체 3위</span><span style="color: #a3e635; font-weight: 900; text-shadow: 0 0 12px rgba(163, 230, 53, 0.85);">라이징스타</span>';
    } else if (rawTitle.includes('패밀리스타') || rawTitle.includes('패밀리')) {
        let resolvedIcon = petIcon;
        if (!resolvedIcon) {
            const curPost = window.currentDetailPost || window.currentMobileDetailPost;
            if (curPost) {
                resolvedIcon = getIconClassFromKind(curPost.KIND_NM || curPost.pet_type);
            }
        }
        if (!resolvedIcon || !resolvedIcon.includes('fa-')) {
            resolvedIcon = 'fa-solid fa-paw';
        }

        const iconHtml = `<span class="pet-emoji-icon" style="margin-right: 0.45rem; display: inline-flex; align-items: center; justify-content: center;"><i class="${resolvedIcon}" style="color: #c084fc; font-size: 1.15em; filter: none !important;"></i></span>`;
        const rankMatch = rawTitle.match(/(\d+위)/);
        if (rankMatch) {
            const rankStr = rankMatch[1];
            let rankColor = '#e2e8f0';
            if (rankStr === '1위') rankColor = '#fef08a';
            else if (rankStr === '2위') rankColor = '#cbd5e1';
            else if (rankStr === '3위') rankColor = '#fed7aa';

            displayHtml = `${iconHtml}<span style="color: #c084fc; font-weight: 900; text-shadow: 0 0 12px rgba(192, 132, 252, 0.85); margin-right: 0.35rem;">패밀리</span><span style="color: ${rankColor}; font-weight: 800;">${rankStr}</span>`;
        } else {
            displayHtml = `${iconHtml}<span style="color: #c084fc; font-weight: 900; text-shadow: 0 0 12px rgba(192, 132, 252, 0.85);">패밀리</span>`;
        }
    } else if (rawTitle.includes('루키스타')) {
        const rankMatch = rawTitle.match(/(\d+위)/);
        if (rankMatch) {
            const rankStr = rankMatch[1];
            let rankColor = '#e2e8f0';
            if (rankStr === '1위') rankColor = '#fef08a';
            else if (rankStr === '2위') rankColor = '#cbd5e1';
            else if (rankStr === '3위') rankColor = '#fed7aa';

            displayHtml = `<span style="color: #34d399; font-weight: 900; text-shadow: 0 0 12px rgba(52, 211, 153, 0.85); margin-right: 0.35rem;">루키스타</span><span style="color: ${rankColor}; font-weight: 800;">${rankStr}</span>`;
        } else {
            displayHtml = `<span style="color: #34d399; font-weight: 900; text-shadow: 0 0 12px rgba(52, 211, 153, 0.85);">루키스타</span>`;
        }
    } else {
        displayHtml = `<span style="color: #ffffff; font-weight: 800;">${rawTitle}</span>`;
    }

    let modal = document.getElementById('globalBadgeZoomModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'globalBadgeZoomModal';
        modal.style.cssText = 'position: fixed; inset: 0; z-index: 99999999; background: rgba(0, 0, 0, 0.88); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.25s ease; cursor: pointer;';
        modal.innerHTML = `
            <div style="position: relative; max-width: 90vw; max-height: 90vh; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1.5rem; transform: scale(0.75); transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);" onclick="event.stopPropagation()">
                <button type="button" class="zoom-close-btn" style="position: absolute; top: -2.8rem; right: -0.8rem; background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.4); color: #ffffff; width: 44px; height: 44px; border-radius: 50%; font-size: 2rem; line-height: 1; cursor: pointer; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(6px); box-shadow: 0 4px 14px rgba(0,0,0,0.6);">&times;</button>
                <img class="zoom-img hall-medal-effect" src="" alt="확대 메달/배지" style="width: 310px; height: 310px; max-width: 80vw; max-height: 55vh; object-fit: contain; filter: drop-shadow(0 0 35px rgba(255,255,255,1)) drop-shadow(0 0 75px rgba(254,240,138,1)) brightness(1.25);">
                <div class="zoom-title" style="color: #ffffff; font-size: 1.25rem; font-weight: 800; text-align: center; background: #192131; padding: 0.55rem 1.7rem; border-radius: 30px; border: 1.5px solid #fde68a; box-shadow: 0 6px 20px rgba(0,0,0,0.6); letter-spacing: -0.3px; display: inline-flex; align-items: center; justify-content: center;"></div>
            </div>
        `;
        document.body.appendChild(modal);
        modal.addEventListener('click', closeBadgeZoomModal);
        const closeBtn = modal.querySelector('.zoom-close-btn');
        if (closeBtn) closeBtn.addEventListener('click', closeBadgeZoomModal);
    }

    const img = modal.querySelector('.zoom-img');
    const titleEl = modal.querySelector('.zoom-title');

    if (img) img.src = imgSrc;
    if (titleEl) titleEl.innerHTML = displayHtml;

    modal.style.display = 'flex';
    requestAnimationFrame(() => {
        modal.style.opacity = '1';
        const inner = modal.firstElementChild;
        if (inner) inner.style.transform = 'scale(1)';
    });
}

function closeBadgeZoomModal() {
    const modal = document.getElementById('globalBadgeZoomModal');
    if (modal && modal.style.display !== 'none') {
        modal.style.opacity = '0';
        const inner = modal.firstElementChild;
        if (inner) inner.style.transform = 'scale(0.75)';
        setTimeout(() => {
            modal.style.display = 'none';
        }, 250);
    }
}

// 전역 캡처링 단계 이벤트 위임: 메달/배지 및 배지 요소 클릭 100% 보장
document.addEventListener('click', function(e) {
    const target = e.target.closest('.badge-zoomable-img, #detailMedalsLeft img, #mDetailMedalsLeft img, .winner-title-badge, .m-card-badge');
    if (target) {
        let imgSrc = target.getAttribute('data-badge-src') || target.querySelector('img')?.src;
        if (!imgSrc && target.tagName === 'IMG') {
            imgSrc = target.src;
        }
        let title = target.getAttribute('data-badge-title') || target.alt || target.textContent.trim();
        let petIcon = target.getAttribute('data-pet-icon') || target.querySelector('.pet-emoji-icon i, i')?.className;

        if (imgSrc) {
            e.stopPropagation();
            e.preventDefault();
            openBadgeZoomModal(imgSrc, title, petIcon);
        }
    }
}, true);

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeBadgeZoomModal();
        closeOriginalImageModal();
    }
});

window.openBadgeZoomModal = openBadgeZoomModal;
window.closeBadgeZoomModal = closeBadgeZoomModal;

// 게시물 ID 또는 (ROUND_ENTRYNO) 기반 즉시 팝업 모달 오픈 헬퍼 함수
async function openPostById(postId, isHallOfFame = false) {
    if (!postId) return;
    if (!ensureLoggedIn()) return;
    const isServerSessionAlive = await verifyServerSessionAsync();
    if (!isServerSessionAlive) return;
    if (window.postsDataStore && window.postsDataStore[postId]) {
        openDetailModal(window.postsDataStore[postId], isHallOfFame);
    } else {
        fetch(`/api/post/detail/${postId}`)
            .then(res => res.json())
            .then(data => {
                if (data.success && data.post) {
                    openDetailModal(data.post, isHallOfFame);
                } else if (typeof showToast === 'function') {
                    showToast('해당 출전작 정보를 불러올 수 없습니다.', 'warning');
                }
            })
            .catch(err => console.error('출전작 팝업 로드 실패:', err));
    }
}
window.openPostById = openPostById;

// URL 쿼리 파라미터 open_post 감지 시 자동 팝업 오픈
function checkAndAutoOpenPost() {
    const urlParams = new URLSearchParams(window.location.search);
    const openPostId = urlParams.get('open_post');
    if (openPostId) {
        const isHOFPage = window.location.pathname.includes('hall-of-fame');
        openPostById(openPostId, isHOFPage);
        const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
        window.history.replaceState({ path: cleanUrl }, '', cleanUrl);
    }
}

// 푸터 공동 순위 슬롯 자동 순차 페이드 로테이션 (3.5초 간격 전환)
function initFooterCoWinnerRotation() {
    const coWinnerSlots = document.querySelectorAll('.footer-rank-slot-wrapper.is-co-winner-slot');
    coWinnerSlots.forEach(slot => {
        const items = slot.querySelectorAll('.footer-star-photo-item');
        if (items.length <= 1) return;
        
        let currentIndex = 0;
        let timer = setInterval(() => {
            items[currentIndex].classList.remove('active');
            currentIndex = (currentIndex + 1) % items.length;
            items[currentIndex].classList.add('active');
        }, 3500);

        slot.addEventListener('mouseenter', () => clearInterval(timer));
        slot.addEventListener('mouseleave', () => {
            timer = setInterval(() => {
                items[currentIndex].classList.remove('active');
                currentIndex = (currentIndex + 1) % items.length;
                items[currentIndex].classList.add('active');
            }, 3500);
        });
    });
}

let ogScale = 1;
let ogTranslateX = 0;
let ogTranslateY = 0;
let isOgDragging = false;
let ogStartX = 0;
let ogStartY = 0;
let ogInitialPinchDistance = null;
let ogInitialScale = 1;
let ogEventsInitialized = false;

function updateOgImageTransform(animated = false) {
    const targetImg = document.getElementById('originalImageViewImg');
    const zoomText = document.getElementById('ogZoomPercent');
    const zoomContainer = document.getElementById('ogImageZoomContainer');
    
    if (!targetImg) return;
    
    if (animated) {
        targetImg.style.transition = 'transform 0.22s cubic-bezier(0.2, 0, 0.2, 1)';
    } else {
        targetImg.style.transition = 'none';
    }

    targetImg.style.transform = `translate(${ogTranslateX}px, ${ogTranslateY}px) scale(${ogScale})`;
    
    if (zoomText) {
        zoomText.textContent = Math.round(ogScale * 100) + '%';
    }

    if (zoomContainer) {
        if (ogScale > 1) {
            zoomContainer.style.cursor = isOgDragging ? 'grabbing' : 'grab';
        } else {
            zoomContainer.style.cursor = 'default';
        }
    }
}

function zoomOriginalImage(delta) {
    let newScale = ogScale + delta;
    if (newScale < 0.8) newScale = 0.8;
    if (newScale > 5.0) newScale = 5.0;
    
    ogScale = newScale;
    if (ogScale <= 1) {
        ogTranslateX = 0;
        ogTranslateY = 0;
    }
    updateOgImageTransform(true);
}

function resetOriginalImageZoom() {
    ogScale = 1;
    ogTranslateX = 0;
    ogTranslateY = 0;
    updateOgImageTransform(true);
}

function openOriginalImageModal(imgSrc) {
    if (!imgSrc) return;
    const modal = document.getElementById('originalImageModal');
    const targetImg = document.getElementById('originalImageViewImg');
    if (!modal || !targetImg) return;
    
    targetImg.src = imgSrc;
    resetOriginalImageZoom();
    
    modal.style.display = 'flex';
    modal.classList.add('show', 'active');
    
    initOgZoomEventsOnce();
}

function closeOriginalImageModal() {
    const modal = document.getElementById('originalImageModal');
    if (!modal) return;
    resetOriginalImageZoom();
    modal.style.display = 'none';
    modal.classList.remove('show', 'active');
}

function initOgZoomEventsOnce() {
    if (ogEventsInitialized) return;
    ogEventsInitialized = true;
    
    const container = document.getElementById('ogImageZoomContainer');
    if (!container) return;

    // 1. 마우스 휠 줌 (Mouse Wheel Zoom)
    container.addEventListener('wheel', function(e) {
        e.preventDefault();
        const delta = e.deltaY < 0 ? 0.18 : -0.18;
        zoomOriginalImage(delta);
    }, { passive: false });

    // 2. 더블클릭 토글 (Double Click Zoom)
    let lastTapTime = 0;
    container.addEventListener('dblclick', function(e) {
        e.preventDefault();
        if (ogScale > 1.2) {
            resetOriginalImageZoom();
        } else {
            ogScale = 2.5;
            ogTranslateX = 0;
            ogTranslateY = 0;
            updateOgImageTransform(true);
        }
    });

    // 3. 마우스 드래그 (Mouse Drag)
    container.addEventListener('mousedown', function(e) {
        if (e.button !== 0) return;
        if (ogScale <= 1) return;
        isOgDragging = true;
        ogStartX = e.clientX - ogTranslateX;
        ogStartY = e.clientY - ogTranslateY;
        updateOgImageTransform(false);
    });

    window.addEventListener('mousemove', function(e) {
        if (!isOgDragging) return;
        ogTranslateX = e.clientX - ogStartX;
        ogTranslateY = e.clientY - ogStartY;
        updateOgImageTransform(false);
    });

    window.addEventListener('mouseup', function() {
        if (isOgDragging) {
            isOgDragging = false;
            updateOgImageTransform(false);
        }
    });

    // 4. 모바일 터치 (Touch Pinch & Drag)
    container.addEventListener('touchstart', function(e) {
        if (e.touches.length === 1) {
            const currentTime = new Date().getTime();
            const tapLength = currentTime - lastTapTime;
            if (tapLength < 300 && tapLength > 0) {
                e.preventDefault();
                if (ogScale > 1.2) {
                    resetOriginalImageZoom();
                } else {
                    ogScale = 2.5;
                    ogTranslateX = 0;
                    ogTranslateY = 0;
                    updateOgImageTransform(true);
                }
                lastTapTime = 0;
                return;
            }
            lastTapTime = currentTime;

            if (ogScale > 1) {
                isOgDragging = true;
                ogStartX = e.touches[0].clientX - ogTranslateX;
                ogStartY = e.touches[0].clientY - ogTranslateY;
            }
        } else if (e.touches.length === 2) {
            isOgDragging = false;
            ogInitialPinchDistance = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            ogInitialScale = ogScale;
        }
    }, { passive: false });

    container.addEventListener('touchmove', function(e) {
        if (e.touches.length === 1 && isOgDragging && ogScale > 1) {
            e.preventDefault();
            ogTranslateX = e.touches[0].clientX - ogStartX;
            ogTranslateY = e.touches[0].clientY - ogStartY;
            updateOgImageTransform(false);
        } else if (e.touches.length === 2 && ogInitialPinchDistance) {
            e.preventDefault();
            const currentDist = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            const pinchFactor = currentDist / ogInitialPinchDistance;
            let newScale = ogInitialScale * pinchFactor;
            if (newScale < 0.8) newScale = 0.8;
            if (newScale > 5.0) newScale = 5.0;
            ogScale = newScale;
            updateOgImageTransform(false);
        }
    }, { passive: false });

    container.addEventListener('touchend', function(e) {
        if (e.touches.length < 2) {
            ogInitialPinchDistance = null;
        }
        if (e.touches.length === 0) {
            isOgDragging = false;
        }
    });

    // 5. Esc 키
    window.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('originalImageModal');
            if (modal && modal.style.display !== 'none') {
                closeOriginalImageModal();
            }
        }
    });
}

window.zoomOriginalImage = zoomOriginalImage;
window.resetOriginalImageZoom = resetOriginalImageZoom;
window.openOriginalImageModal = openOriginalImageModal;
window.closeOriginalImageModal = closeOriginalImageModal;

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(checkAndAutoOpenPost, 300);
    initFooterCoWinnerRotation();
});
