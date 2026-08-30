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
 * 동영상 재생 중 '출전작 이미지 보기' 버튼 클릭 시 동영상 일시정지/숨김 후 대표 이미지 표시
 */
function showPostImage(type) {
    let showBtnId = 'detailShowImgBtn';
    let replayBtnId = 'detailYtbReplayBtn';
    let containerId = 'detailYtbContainer';
    let imgId = 'detailImg';
    let playerKey = 'pcYtbPlayer';

    if (type === 'mobile') {
        showBtnId = 'mDetailShowImgBtn';
        replayBtnId = 'mDetailYtbReplayBtn';
        containerId = 'mDetailYtbContainer';
        imgId = 'mDetailImg';
        playerKey = 'mYtbPlayer';
    } else if (type === 'preview_pc') {
        showBtnId = 'previewShowImgBtn';
        replayBtnId = 'previewYtbReplayBtn';
        containerId = 'previewYtbContainer';
        imgId = 'previewModalImg';
        playerKey = 'previewYtbPlayer';
    } else if (type === 'preview_mobile') {
        showBtnId = 'mPreviewShowImgBtn';
        replayBtnId = 'mPreviewYtbReplayBtn';
        containerId = 'mPreviewYtbContainer';
        imgId = 'mPreviewModalImg';
        playerKey = 'mPreviewYtbPlayer';
    }

    const showBtn = document.getElementById(showBtnId);
    if (showBtn) showBtn.style.display = 'none';

    const imgEl = document.getElementById(imgId);
    if (imgEl) {
        imgEl.style.opacity = '1';
        imgEl.style.pointerEvents = 'auto';
        imgEl.style.zIndex = '35';
    }

    const container = document.getElementById(containerId);
    if (container) {
        container.style.display = 'none';
        container.style.zIndex = '5';
    }

    const player = window[playerKey];
    if (player && typeof player.pauseVideo === 'function') {
        try { player.pauseVideo(); } catch(e) {}
    }

    const replayBtn = document.getElementById(replayBtnId);
    if (replayBtn) replayBtn.style.display = 'flex';
}
window.showPostImage = showPostImage;

/**
 * 모바일 전용 유튜브 다시보기 버튼 클릭 핸들러
 */
function replayMobileYtbVideo() {
    const mImgEl = document.getElementById('mDetailImg');
    const mReplayBtn = document.getElementById('mDetailYtbReplayBtn');
    const mShowBtn = document.getElementById('mDetailShowImgBtn');
    const container = document.getElementById('mDetailYtbContainer');

    if (mImgEl) {
        mImgEl.style.opacity = '0';
        mImgEl.style.pointerEvents = 'none';
    }
    if (mReplayBtn) mReplayBtn.style.display = 'none';
    if (mShowBtn) mShowBtn.style.display = 'flex';

    const player = window.mYtbPlayer;
    if (container) container.style.display = 'block';

    if (player && typeof player.seekTo === 'function') {
        try {
            player.seekTo(0, true);
            player.playVideo();
            return;
        } catch(e) {}
    }

    if (container && window.currentMYtbVideoId) {
        setupYouTubePlayerWithEnding('mDetailYtbContainer', 'mDetailImg', window.currentMYtbVideoId, 'mYtbFadeTimer', 'mYtbPlayer', 'mDetailYtbReplayBtn');
    }
}
window.replayMobileYtbVideo = replayMobileYtbVideo;

function replayMobilePreviewYtbVideo() {
    const mImgEl = document.getElementById('mPreviewModalImg');
    const mReplayBtn = document.getElementById('mPreviewYtbReplayBtn');
    const mShowBtn = document.getElementById('mPreviewShowImgBtn');
    const container = document.getElementById('mPreviewYtbContainer');
    const mYtbVal = (document.getElementById('mUploadSnsYtb')?.value || '').trim();
    const vId = (typeof getYouTubeVideoId === 'function') ? getYouTubeVideoId(mYtbVal) : null;

    if (mImgEl) {
        mImgEl.style.opacity = '0';
        mImgEl.style.pointerEvents = 'none';
    }
    if (mReplayBtn) mReplayBtn.style.display = 'none';
    if (mShowBtn) mShowBtn.style.display = 'flex';

    const player = window.mPreviewYtbPlayer;
    if (container) container.style.display = 'block';

    if (player && typeof player.seekTo === 'function') {
        try {
            player.seekTo(0, true);
            player.playVideo();
            return;
        } catch(e) {}
    }

    if (container && vId) {
        setupYouTubePlayerWithEnding('mPreviewYtbContainer', 'mPreviewModalImg', vId, 'mPreviewYtbFadeTimer', 'mPreviewYtbPlayer', 'mPreviewYtbReplayBtn');
    }
}
window.replayMobilePreviewYtbVideo = replayMobilePreviewYtbVideo;

/**
 * 모바일 전용 YouTube 동영상 재생 [동영상 바로 재생 -> 완료 시 대표 이미지 페이드인 & 다시보기 버튼 표시] 헬퍼
 */
function setupYouTubePlayerWithEnding(containerId, imgId, videoId, fadeTimerKey, playerKey, replayBtnId) {
    const container = document.getElementById(containerId);
    const imgEl = document.getElementById(imgId);
    const replayBtn = replayBtnId ? document.getElementById(replayBtnId) : null;

    const showImgBtnMap = {
        'detailYtbReplayBtn': 'detailShowImgBtn',
        'mDetailYtbReplayBtn': 'mDetailShowImgBtn',
        'previewYtbReplayBtn': 'previewShowImgBtn',
        'mPreviewYtbReplayBtn': 'mPreviewShowImgBtn'
    };
    const showImgBtnId = showImgBtnMap[replayBtnId] || '';
    const showImgBtn = showImgBtnId ? document.getElementById(showImgBtnId) : null;

    if (replayBtn) replayBtn.style.display = 'none';

    if (!container) return;

    if (window[fadeTimerKey]) {
        clearTimeout(window[fadeTimerKey]);
        window[fadeTimerKey] = null;
    }
    if (window[playerKey] && typeof window[playerKey].destroy === 'function') {
        try { window[playerKey].destroy(); } catch(e) {}
        window[playerKey] = null;
    }

    const hideImg = () => {
        if (imgEl) {
            imgEl.style.opacity = '0';
            imgEl.style.pointerEvents = 'none';
            imgEl.style.zIndex = '5';
        }
        if (container) {
            container.style.display = 'block';
            container.style.zIndex = '30';
        }
        if (replayBtn) replayBtn.style.display = 'none';
        if (showImgBtn) showImgBtn.style.display = 'flex';
    };

    const showImg = () => {
        if (imgEl) {
            imgEl.style.opacity = '1';
            imgEl.style.pointerEvents = 'auto';
            imgEl.style.zIndex = '35';
        }
        if (container) {
            container.style.display = 'none';
            container.style.zIndex = '5';
        }
        if (showImgBtn) showImgBtn.style.display = 'none';
    };

    if (!videoId) {
        container.style.display = 'none';
        container.innerHTML = '';
        showImg();
        if (replayBtn) replayBtn.style.display = 'none';
        return;
    }

    container.style.display = 'block';
    container.style.zIndex = '30';
    hideImg();
    const iframeId = containerId + '_iframe';
    const curOrigin = (typeof window !== 'undefined' && window.location && window.location.origin) ? window.location.origin : '';

    const renderDirectIframe = () => {
        container.innerHTML = `<iframe id="${iframeId}" src="https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&playsinline=1&enablejsapi=1&rel=0&controls=1&fs=1&modestbranding=1&origin=${encodeURIComponent(curOrigin)}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen style="width: 100%; height: 100%; border: none;" onerror="const img=document.getElementById('${imgId}');if(img){img.style.opacity='1';img.style.pointerEvents='auto';img.style.zIndex='35';}const c=document.getElementById('${containerId}');if(c){c.style.display='none';c.style.zIndex='5';}"></iframe>`;
        hideImg();
    };

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
                    'controls': 1,
                    'fs': 1,
                    'modestbranding': 1,
                    'origin': curOrigin
                },
                events: {
                    'onReady': (event) => {
                        hideImg();
                        try { event.target.mute(); } catch(e) {}
                        try { event.target.playVideo(); } catch(e) {}
                    },
                    'onStateChange': (event) => {
                        // YT.PlayerState.ENDED = 0 (동영상 1회 재생 완료 시 대표 이미지 복구 및 우측 하단 재생버튼 표시)
                        if (event.data === 0 || (window.YT && window.YT.PlayerState && event.data === window.YT.PlayerState.ENDED)) {
                            showImg();
                            if (replayBtn) replayBtn.style.display = 'flex';
                        }
                    },
                    'onError': (event) => {
                        // 구글 403 에러 또는 퍼가기 제한 영상 시 대표 출전작 이미지로 즉시 자동 복구
                        showImg();
                        if (container) container.style.display = 'none';
                    }
                }
            });
        } catch(e) {
            renderDirectIframe();
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
            } else if (attempts > 20) {
                clearInterval(timer);
                renderDirectIframe();
            }
        }, 100);
    }
}

/**
 * 모바일 전용 일자시간 상대시간(방금 전, N초 전, N분 전, N시간 전, N일 전, N달 전, N년 전) 포맷팅
 */
function formatTimeAgo(dateInput) {
    if (!dateInput) return '방금 전';

    if (dateInput instanceof Date) {
        if (isNaN(dateInput.getTime())) return '방금 전';
        return _calculateTimeAgoMobile(dateInput);
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

    return _calculateTimeAgoMobile(date);
}

function _calculateTimeAgoMobile(date) {
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

document.addEventListener('DOMContentLoaded', function() {
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

    // 모바일 커스텀 회차 드롭다운 토글 및 바깥 클릭 닫기 (다중 드롭다운 지원)
    document.querySelectorAll('.custom-contest-dropdown').forEach(dd => {
        const trigger = dd.querySelector('.custom-contest-trigger');
        if (trigger) {
            trigger.addEventListener('click', function(e) {
                e.stopPropagation();
                document.querySelectorAll('.custom-contest-dropdown').forEach(other => {
                    if (other !== dd) other.classList.remove('open');
                });
                dd.classList.toggle('open');
            });
        }
    });
    document.addEventListener('click', function(e) {
        document.querySelectorAll('.custom-contest-dropdown').forEach(dd => {
            if (!dd.contains(e.target)) {
                dd.classList.remove('open');
            }
        });
    });

    // 모바일 커스텀 정렬 드롭다운 토글 및 바깥 클릭 닫기
    const mCustomSortDropdown = document.getElementById('mCustomSortDropdown');
    if (mCustomSortDropdown) {
        const trigger = mCustomSortDropdown.querySelector('.custom-sort-trigger');
        if (trigger) {
            trigger.addEventListener('click', function(e) {
                e.stopPropagation();
                mCustomSortDropdown.classList.toggle('open');
            });
        }
        document.addEventListener('click', function(e) {
            if (!mCustomSortDropdown.contains(e.target)) {
                mCustomSortDropdown.classList.remove('open');
            }
        });
    }

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
                    alert('🎉 출전 등록이 성공적으로 완료되었습니다! 🐾');
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

// 모바일 상세보기 모달 스크롤 100% 최상단 리셋 헬퍼
function resetMobileModalScroll() {
    const detailModal = document.getElementById('mDetailModal');
    if (!detailModal) return;
    detailModal.scrollTop = 0;
    const targets = [
        detailModal.querySelector('.m-modal-sheet'),
        detailModal.querySelector('.m-modal-scroll-body'),
        document.getElementById('mDetailCommentList'),
        document.querySelector('.m-modal-scroll-body')
    ];
    targets.forEach(el => {
        if (el) {
            el.scrollTop = 0;
        }
    });
}

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
window.checkCurrentLoginCookie = checkCurrentLoginCookie;

/**
 * 모바일 전용 현재 시점 로그인 상태 엄격 체크 헬퍼
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
            const mModal = document.getElementById('googleAuthModal') || document.getElementById('mAuthModal');
            if (mModal) {
                mModal.style.display = 'flex';
                mModal.style.zIndex = '999999';
                mModal.classList.add('show', 'active');
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
 * 모바일 카드 클릭 전용 세션 체킹 래퍼 함수 (서버 세션 100% 검증 후 출전작 팝업 열기)
 */
async function handleMobileCardClick(postData, isHallOfFame = false) {
    if (!ensureLoggedIn()) return false;
    const isAlive = await verifyServerSessionAsync();
    if (!isAlive) {
        if (typeof openGoogleAuthModal === 'function') openGoogleAuthModal();
        return false;
    }
    openMobileDetailModal(postData, isHallOfFame);
}
window.handleMobileCardClick = handleMobileCardClick;

/**
 * 모바일 서버 측 세션 타임아웃 실시간 검증 헬퍼
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

    if (typeof closeMobileDetailModal === 'function') closeMobileDetailModal();
    if (typeof closeDetailModal === 'function') closeDetailModal();

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

// 멀티 탭 동기화: 다른 탭에서 로그아웃 발생 시 즉시 모바일 상태 동기화
window.addEventListener('storage', (e) => {
    if (e.key === 'pawstar_auth_event' || e.key === 'pawstar_logged_out') {
        if (localStorage.getItem('pawstar_logged_out') === 'true' || (e.newValue && e.newValue.startsWith('logout_'))) {
            window.isUserLoggedIn = false;
            window.CURRENT_USER_ID = '';
            if (typeof closeMobileDetailModal === 'function') closeMobileDetailModal();
        }
    }
});

// 3. 모바일 전용 게시물 상세보기 모달 open
async function openMobileDetailModal(postData, isHallOfFame = false) {
    if (!ensureLoggedIn()) {
        return;
    }
    const isServerSessionAlive = await verifyServerSessionAsync();
    if (!isServerSessionAlive) {
        return;
    }

    const detailModal = document.getElementById('mDetailModal');
    if (!detailModal) return;
    detailModal.style.display = '';

    // 모바일 팝업 및 내부 스크롤 컨테이너 최상단 스크롤 초기화
    resetMobileModalScroll();

    postData.post_id = postData.post_id || postData.POST_ID || ((postData.CONTEST_ROUND || postData.contest_id) && (postData.ROUND_NO || postData.round_no) ? `${postData.CONTEST_ROUND || postData.contest_id}_${postData.ROUND_NO || postData.round_no}` : (postData.ROUND_NO || postData.round_no));
    postData.title = postData.title || postData.TITLE || '';
    postData.content = postData.content || postData.CONTS || postData.conts || '';
    window.currentMobileDetailPostId = postData.post_id;
    window.currentMobileDetailPostData = postData;

    // 회차 마감 여부 판별 (회차 번호 비교 및 온갖 마감 키 값 종합 검증)
    const postRoundNum = parseInt(postData.CONTEST_ROUND || postData.contest_round || postData.contest_id || (String(postData.post_id || '').split('_')[0]) || '0', 10);
    const activeRoundNum = parseInt(window.CURRENT_CONTEST_ROUND || window.ACTIVE_CONTEST_ROUND || (document.getElementById('currentActiveRound') ? document.getElementById('currentActiveRound').value : '0') || '0', 10);

    const isClosedRound = isHallOfFame || 
                          postData.contest_stat === 'G001C002' || 
                          postData.CONTEST_STAT === 'G001C002' || 
                          postData.STATUS_CD === 'G001C002' ||
                          postData.status_cd === 'G001C002' ||
                          postData.is_closed === true || 
                          postData.closed === true || 
                          postData.is_ended === true || 
                          postData.IS_ENDED === true ||
                          (postRoundNum > 0 && activeRoundNum > 0 && postRoundNum < activeRoundNum);

    // 종료된 회차의 경우 원형 핑크 하트 버튼 숨김
    let mHeaderLikeBtn = document.getElementById('mDetailHeaderLikeBtn');
    if (mHeaderLikeBtn) {
        if (isClosedRound) {
            mHeaderLikeBtn.style.display = 'none';
        } else {
            mHeaderLikeBtn.style.display = 'inline-flex';
        }
    }

    // 모바일 출전 포기(삭제) 버튼 제어 (지난 회차는 "삭제", 진행중 회차는 "출전 포기")
    const mDeleteBtn = document.getElementById('mDetailDeleteBtn');
    if (mDeleteBtn) {
        const currentUserId = String(window.CURRENT_USER_ID || '').trim();
        const postOwnerId = String(postData.ENT_USER_ID || postData.user_id || '').trim();
        if (currentUserId && postOwnerId && (currentUserId === postOwnerId || currentUserId === 'admin')) {
            mDeleteBtn.style.display = 'inline-flex';
            if (isClosedRound) {
                mDeleteBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i> 삭제';
            } else {
                mDeleteBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i> 출전 포기';
            }
        } else {
            mDeleteBtn.style.display = 'none';
        }
    }

    const mPopupSrc = postData.popup_image_path || postData.IMAGE_PATH || postData.image_path || postData.media_url || 
        ((postData.file_path && postData.list_file_name) ? (postData.file_path.endsWith('/') ? postData.file_path : postData.file_path + '/') + postData.list_file_name : '');
    const mImgEl = document.getElementById('mDetailImg');
    if (mImgEl) {
        mImgEl.style.opacity = '0';
        mImgEl.style.transition = 'opacity 0.2s ease-in-out';
        mImgEl.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>';
        if (mPopupSrc) {
            const tempImg = new Image();
            tempImg.onload = () => {
                mImgEl.src = mPopupSrc;
                mImgEl.style.opacity = '1';
            };
            tempImg.src = mPopupSrc;
            if (tempImg.complete) {
                mImgEl.src = mPopupSrc;
                mImgEl.style.opacity = '1';
            }
        }
    }

    // SNS_YTB 컬럼값이 있을 경우 유튜브 동영상 임베드 및 자동 재생 (재생 완료 시 대표 이미지 페이드인 복구 & 다시보기 버튼 표시)
    const rawYtbMobile = (postData.SNS_YTB || postData.sns_ytb || '').trim();
    const mYtbId = getYouTubeVideoId(rawYtbMobile);
    window.currentMYtbVideoId = mYtbId;
    setupYouTubePlayerWithEnding('mDetailYtbContainer', 'mDetailImg', mYtbId, 'mYtbFadeTimer', 'mYtbPlayer', 'mDetailYtbReplayBtn', 'mDetailYtbCountdown', 'mDetailYtbCountNum');
    document.getElementById('mDetailAuthorImg').src = postData.PROFILE_URL || postData.user_profile || '/static/image/profile/default_profile.png';
    document.getElementById('mDetailAuthorNickname').textContent = postData.NK_NM || postData.user_nickname || '집사';
    
    // 모바일 작성자 SNS 링크 동적 생성 (저장된 주소가 있는 아이콘들만 나란히 표시)
    const mSnsContainer = document.getElementById('mDetailAuthorSnsLinks');
    if (mSnsContainer) {
        mSnsContainer.innerHTML = '';
        const rawInst = (postData.SNS_INST || postData.sns_inst || '').trim();
        const rawYtb = (postData.SNS_YTB || postData.sns_ytb || '').trim();
        const rawFsb = (postData.SNS_FSB || postData.sns_fsb || '').trim();
        const rawBlg = (postData.SNS_BLG || postData.sns_blg || '').trim();

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
                aBtn.style.width = '32px';
                aBtn.style.height = '32px';
                aBtn.style.fontSize = '0.88rem';
                aBtn.style.display = 'inline-flex';
                aBtn.style.alignItems = 'center';
                aBtn.style.justifyContent = 'center';
                aBtn.style.padding = '0';
                aBtn.style.lineHeight = '1';
                aBtn.style.flexShrink = '0';
                aBtn.innerHTML = `<i class="${item.icon}"></i>`;
                mSnsContainer.appendChild(aBtn);
            }
        });
    }
    
    // 대회 정보 (제 N회 & 실제 대회명 분리 뱃지) 바인딩
    const mContestBadge = document.getElementById('mDetailContestBadge');
    if (mContestBadge) {
        let rawRound = postData.CONTEST_ROUND || postData.contest_round || postData.contest_id;
        if (!rawRound && postData.post_id && String(postData.post_id).includes('_')) {
            rawRound = String(postData.post_id).split('_')[0];
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
        
        let contestTitle = postData.CONTEST_TITLE || postData.contest_title || postData.THEME_NM || postData.theme_nm || postData.CONTEST_NM || postData.contest_nm || postData.theme_title || '';
        
        if (!contestTitle) {
            const pageContestEl = document.querySelector('.hero-title') || document.querySelector('.selected-text') || document.getElementById('selectedContestTitle');
            if (pageContestEl) {
                let fullTxt = pageContestEl.innerText || pageContestEl.textContent || '';
                contestTitle = fullTxt.replace(/제\s*\d+\s*회/g, '').trim();
            }
        }
        if (!contestTitle) contestTitle = '포스타 콘테스트';
        const badgeStyle = isClosedRound 
            ? 'color: #475569; background: #f1f5f9; border: 1.5px solid #cbd5e1; box-shadow: 0 2px 6px rgba(100, 116, 139, 0.12);' 
            : 'color: #db2777; background: #fce7f3; border: 1.5px solid #fbcfe8; box-shadow: 0 2px 6px rgba(219, 39, 119, 0.12);';

        mContestBadge.innerHTML = `
            <span style="font-size: 0.75rem; font-weight: 800; ${badgeStyle} padding: 0.22rem 0.65rem; border-radius: 14px; display: inline-flex; align-items: center; justify-content: center; gap: 0.25rem; flex-shrink: 0;">
                <span style="display: inline-block; transform: translateY(-1px);">제 ${roundNo}회</span>
            </span>
            <span style="font-size: 0.8rem; font-weight: 800; background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.02em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; filter: drop-shadow(0 1px 2px rgba(124, 58, 237, 0.12));">
                ${contestTitle}
            </span>
        `;
    }

    const mPetTagEl = document.getElementById('mDetailPetTag');
    if (mPetTagEl) {
        let rawKind = postData.KIND_NM || postData.pet_type || '반려동물';
        const cleanKind = rawKind.replace(/[🐕🐈🐹🦜🐇🦔🦎🐠🦦🐾🐶🐱🐰🐟🐢🐴🐷☎️]/g, '').trim();
        
        let faIcon = 'fa-solid fa-paw';
        if (cleanKind.includes('강아지') || cleanKind.includes('개')) faIcon = 'fa-solid fa-dog';
        else if (cleanKind.includes('고양이')) faIcon = 'fa-solid fa-cat';
        else if (cleanKind.includes('햄스터') || cleanKind.includes('소동물') || cleanKind.includes('토끼') || cleanKind.includes('고슴도치') || cleanKind.includes('작은동물')) faIcon = 'fa-solid fa-otter';
        else if (cleanKind.includes('거북이') || cleanKind.includes('파충류') || cleanKind.includes('도마뱀')) faIcon = 'fa-solid fa-frog';
        else if (cleanKind.includes('어류') || cleanKind.includes('관상어') || cleanKind.includes('물고기')) faIcon = 'fa-solid fa-fish';
        else if (cleanKind.includes('앵무새') || cleanKind.includes('새') || cleanKind.includes('조류')) faIcon = 'fa-solid fa-crow';
        else if (cleanKind.includes('말') || cleanKind.includes('큰동물')) faIcon = 'fa-solid fa-horse';

        const mPetNm = postData.PET_NM || postData.pet_name || '';
        const kindHtml = `<span style="background: #ffe4e6; color: #e11d48; padding: 0.18rem 0.6rem; border-radius: 12px; font-size: 0.74rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.25rem; box-shadow: 0 2px 5px rgba(225, 29, 72, 0.08); flex-shrink: 0;"><i class="${faIcon}"></i> ${cleanKind}</span>`;
        if (mPetNm) {
            mPetTagEl.innerHTML = `${kindHtml}<span style="background: #f3e8ff; color: #7c3aed; padding: 0.18rem 0.6rem; border-radius: 12px; font-size: 0.74rem; font-weight: 700; margin-left: 0.3rem; display: inline-flex; align-items: center; gap: 0.2rem; box-shadow: 0 2px 5px rgba(124, 58, 237, 0.08); max-width: 180px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-shrink: 1;" title="${escapeHtml(mPetNm)}"><span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; display: inline-block; max-width: 100%;">${escapeHtml(mPetNm)}</span></span>`;
        } else {
            mPetTagEl.innerHTML = kindHtml;
        }
    }
    document.getElementById('mDetailScoreNum').textContent = (postData.score || postData.SCORE || 0).toLocaleString();
    const mTitleEl = document.getElementById('mDetailTitle');
    const titleText = (postData.title || postData.TITLE || '').trim();
    let contentText = (postData.content || postData.CONTS || '').trim();

    if (postData.is_post_deleted || titleText === '출전자에 의해 삭제된 출전작입니다' || titleText.includes('삭제된 출전작')) {
        contentText = '';
    }

    if (mTitleEl) {
        mTitleEl.textContent = titleText;
        mTitleEl.style.display = titleText ? 'block' : 'none';
        mTitleEl.style.marginBottom = contentText ? '0.5rem' : '0';
    }
    
    const mContentEl = document.getElementById('mDetailContent');
    const mContentBox = document.getElementById('mDetailContentBox');
    if (mContentEl) {
        mContentEl.textContent = contentText;
        mContentEl.style.display = contentText ? 'block' : 'none';
    }
    if (mContentBox) {
        mContentBox.style.display = (titleText || contentText) ? 'block' : 'none';
    }

    const mCreatedAtEl = document.getElementById('mDetailCreatedAt');
    if (mCreatedAtEl) {
        mCreatedAtEl.textContent = formatTimeAgo(postData.created_at || postData.ENT_DT || postData.dt_ago || '');
    }

    // 4요소 실시간 액션 수치 팝업 세팅
    const viewCnt = postData.view_count || postData.VW_CNT || 0;
    const likeCnt = postData.like_count || postData.LIKE_CNT || 0;
    const commentCnt = postData.comment_count || postData.CMT_CNT || 0;
    const shareCnt = postData.share_count || postData.SHARE_CNT || 0;

    const mValView = document.getElementById('mDetailViewCount');
    if (mValView) mValView.textContent = Number(viewCnt).toLocaleString();
    const mValLike = document.getElementById('mDetailLikeCount');
    if (mValLike) mValLike.textContent = Number(likeCnt).toLocaleString();
    const mValComment = document.getElementById('mDetailCommentCount');
    if (mValComment) mValComment.textContent = Number(commentCnt).toLocaleString();
    const mValShare = document.getElementById('mDetailShareCount');
    if (mValShare) mValShare.textContent = Number(shareCnt).toLocaleString();

    // 모바일 팝업 랭킹 / 수상 배지 채우기 (오직 실물 메달/배지 이미지들만 전체부문 -> 품종부문 순서로 가로 나란히 표시)
    const mMedalsLeftEl = document.getElementById('mDetailMedalsLeft');
    const mBadgeEl = document.getElementById('mDetailRankBadge');

    if (mMedalsLeftEl) mMedalsLeftEl.innerHTML = '';

    let awardsData = (postData.awards && postData.awards.length > 0) ? postData.awards : [];
    if (awardsData.length === 0) {
        const cd = postData.award_cd || postData.AWARD_CD;
        let rk = postData.ranking || postData.RANKING || postData.rank || postData.final_rank || postData.AWARD_RANK || postData.rank_no;
        if (!rk && (isHallOfFame || postData.is_closed) && postData.round_no && (postData.round_no == 1 || postData.round_no == 2 || postData.round_no == 3)) {
            rk = Number(postData.round_no);
        }

        if (cd) {
            const nm = postData.award_nm || postData.AWARD_NM || '수상 메달';
            const part = postData.award_part || postData.AWARD_PART || (cd.startsWith('P001') ? 'G002P001' : 'G002P002');
            const img = postData.badge_img || postData.badge_image_path || postData.BADGE_IMAGE_PATH || `/static/image/badge/${cd}.png`;
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

        const kindNm = postData.KIND_NM || postData.pet_type || '';
        let petIconClass = 'fa-solid fa-paw';
        if (kindNm.includes('강아지') || kindNm.includes('개')) petIconClass = 'fa-solid fa-dog';
        else if (kindNm.includes('고양이')) petIconClass = 'fa-solid fa-cat';
        else if (kindNm.includes('햄스터') || kindNm.includes('소동물') || kindNm.includes('토끼') || kindNm.includes('고슴도치') || kindNm.includes('작은동물')) petIconClass = 'fa-solid fa-otter';
        else if (kindNm.includes('거북이') || kindNm.includes('파충류') || kindNm.includes('도마뱀')) petIconClass = 'fa-solid fa-frog';
        else if (kindNm.includes('어류') || kindNm.includes('관상어') || kindNm.includes('물고기')) petIconClass = 'fa-solid fa-fish';
        else if (kindNm.includes('앵무새') || kindNm.includes('새') || kindNm.includes('조류')) petIconClass = 'fa-solid fa-crow';
        else if (kindNm.includes('말') || kindNm.includes('큰동물')) petIconClass = 'fa-solid fa-horse';

        if (mMedalsLeftEl) {
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
                    leftHtml += `<img src="${badgeImgSrc}" class="hall-medal-effect badge-zoomable-img" data-badge-src="${badgeImgSrc}" data-badge-title="${displayTitle}" style="width: 48px; height: 48px; object-fit: contain; flex-shrink: 0; pointer-events: auto; cursor: pointer;" alt="${displayTitle}">`;
                }
            });
            mMedalsLeftEl.innerHTML = leftHtml;
        }

        if (mBadgeEl) {
            mBadgeEl.style.justifyContent = 'flex-end';
            mBadgeEl.style.right = '0.5rem';
            mBadgeEl.style.left = 'auto';

            let rightHtml = '<div style="display: flex; align-items: center; justify-content: flex-end; gap: 0.3rem; flex-wrap: wrap;">';
            sortedAwards.forEach(aw => {
                const awardCdStr = String(aw.award_cd || aw.AWARD_CD || '');
                const awardNmStr = String(aw.award_nm || aw.AWARD_NM || '');
                const badgeImgSrc = aw.badge_img || aw.badge_image_path || aw.BADGE_IMAGE_PATH || (awardCdStr ? `/static/image/badge/${awardCdStr}.png` : '');
                const awRank = aw.ranking || aw.RANKING;

                if (awardCdStr.includes('P001A101') || (!awardCdStr && awardNmStr.includes('슈퍼'))) {
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: calc(0.38rem + 1px) 0.75rem calc(0.38rem - 1px) 0.75rem; font-size: 0.82rem; font-weight: 800; background: linear-gradient(135deg, rgba(254,249,195,0.95), rgba(253,224,71,0.9)); color: #713f12; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '슈퍼스타');"><i class="fa-solid fa-star"></i> 슈퍼스타</div>`;
                } else if (awardCdStr.includes('P001A102') || (!awardCdStr && awardNmStr.includes('브라이트'))) {
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: calc(0.38rem + 1px) 0.75rem calc(0.38rem - 1px) 0.75rem; font-size: 0.82rem; font-weight: 800; background: linear-gradient(135deg, rgba(240,249,255,0.95), rgba(125,211,252,0.9)); color: #0369a1; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '브라이트스타');"><i class="fa-solid fa-star"></i> 브라이트스타</div>`;
                } else if (awardCdStr.includes('P001A103') || (!awardCdStr && awardNmStr.includes('라이징'))) {
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: calc(0.38rem + 1px) 0.75rem calc(0.38rem - 1px) 0.75rem; font-size: 0.82rem; font-weight: 800; background: linear-gradient(135deg, rgba(247,254,231,0.95), rgba(163,230,53,0.9)); color: #3f6212; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '라이징스타');"><i class="fa-solid fa-star"></i> 라이징스타</div>`;
                } else {
                    const titleText = awRank ? `패밀리 ${awRank}위` : '패밀리';
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: calc(0.38rem + 1px) 0.75rem calc(0.38rem - 1px) 0.75rem; font-size: 0.82rem; font-weight: 800; background: linear-gradient(135deg, rgba(243,232,255,0.95), rgba(192,132,252,0.9)); color: #3b0764; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '${titleText}');"><span class="pet-emoji-icon"><i class="${petIconClass}"></i></span> ${titleText}</div>`;
                }
            });
            rightHtml += '</div>';
            mBadgeEl.innerHTML = rightHtml;
        }
    } else {
        if (mBadgeEl) {
            if (postData.rank_candidate && !isClosedRound) {
                mBadgeEl.style.justifyContent = 'flex-start';
                mBadgeEl.style.left = '0.5rem';
                mBadgeEl.style.right = 'auto';

                const kindNm = postData.KIND_NM || postData.pet_type || '';
                let petIconClass = 'fa-solid fa-paw';
                if (kindNm.includes('강아지') || kindNm.includes('개')) petIconClass = 'fa-solid fa-dog';
                else if (kindNm.includes('고양이')) petIconClass = 'fa-solid fa-cat';
                else if (kindNm.includes('햄스터') || kindNm.includes('소동물') || kindNm.includes('토끼') || kindNm.includes('고슴도치') || kindNm.includes('작은동물')) petIconClass = 'fa-solid fa-otter';
                else if (kindNm.includes('거북이') || kindNm.includes('파충류') || kindNm.includes('도마뱀')) petIconClass = 'fa-solid fa-frog';
                else if (kindNm.includes('어류') || kindNm.includes('관상어') || kindNm.includes('물고기')) petIconClass = 'fa-solid fa-fish';
                else if (kindNm.includes('앵무새') || kindNm.includes('새') || kindNm.includes('조류')) petIconClass = 'fa-solid fa-crow';
                else if (kindNm.includes('말') || kindNm.includes('큰동물')) petIconClass = 'fa-solid fa-horse';

                const urlParams = new URLSearchParams(window.location.search);
                const currentPetType = urlParams.get('pet_type') || 'all';
                const isFamily = (currentPetType && currentPetType !== 'all');
                const catPrefix = isFamily ? '패밀리 ' : '전체 ';
                const prefix = catPrefix + (postData.is_co_rank ? '공동 ' : '');
                const rankTitle = `${prefix}${postData.rank_candidate}위 후보`;
                let bgStyle = '';
                let iconHtml = '';

                if (isFamily) {
                    iconHtml = `<span class="pet-emoji-icon"><i class="${petIconClass}"></i></span>`;
                    bgStyle = 'background: linear-gradient(135deg, rgba(243,232,255,0.92) 0%, rgba(192,132,252,0.9) 50%, rgba(147,51,234,0.92) 100%); color: #3b0764;';
                } else {
                    iconHtml = '<i class="fa-solid fa-medal"></i>';
                    if (postData.rank_candidate == 1) {
                        bgStyle = 'background: linear-gradient(135deg, #fef9c3 0%, #fef08a 50%, #fde047 100%); color: #713f12; box-shadow: 0 4px 14px rgba(253, 224, 71, 0.45);';
                    } else if (postData.rank_candidate == 2) {
                        bgStyle = 'background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #bae6fd 100%); color: #0369a1; box-shadow: 0 4px 14px rgba(125, 211, 252, 0.45);';
                    } else if (postData.rank_candidate == 3) {
                        bgStyle = 'background: linear-gradient(135deg, #f7fee7 0%, #ecfccb 50%, #d9f99d 100%); color: #3f6212; box-shadow: 0 4px 14px rgba(163, 230, 53, 0.45);';
                    } else {
                        bgStyle = 'background: linear-gradient(135deg, #fde047 0%, #eab308 50%, #ca8a04 100%); color: #713f12;';
                    }
                }
                mBadgeEl.innerHTML = `<div class="m-card-badge" style="font-size: 0.82rem; padding: 0.38rem 0.75rem; margin: 0; position: relative; top: 0; left: 0; font-weight: 800; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25); ${bgStyle}">${iconHtml} ${rankTitle}</div>`;
            } else {
                mBadgeEl.innerHTML = '';
            }
        }
    }

    const isCommented = (postData.actions && postData.actions.is_commented) || postData.is_commented || false;
    window.currentMobileDetailPost = postData;
    window.currentMobileDetailPostData = postData;
    window.currentMobileDetailPostId = postData.post_id;
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

    const mIsLiked = !!((postData.actions && postData.actions.is_liked) || postData.is_liked);
    const mBtnLikePopup = document.getElementById('mDetailBtnLike');
    const mHeartIcon = document.getElementById('mDetailHeartIcon');
    mHeaderLikeBtn = mHeaderLikeBtn || document.getElementById('mDetailHeaderLikeBtn');
    const mHeaderHeartIcon = document.getElementById('mDetailHeaderHeartIcon');
    if (mBtnLikePopup) {
        const icon = mBtnLikePopup.querySelector('i');
        if (mIsLiked) {
            mBtnLikePopup.classList.add('active');
            if (icon) icon.className = 'fa-solid fa-heart';
        } else {
            mBtnLikePopup.classList.remove('active');
            if (icon) icon.className = 'fa-regular fa-heart';
        }
    }
    
    let mBtnSharePopup = document.getElementById('mDetailBtnShare');
    if (mBtnSharePopup) mBtnSharePopup.classList.remove('active');

    if (mHeartIcon) {
        mHeartIcon.className = mIsLiked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
        mHeartIcon.style.color = mIsLiked ? '#e11d48' : '';
    }
    if (mHeaderHeartIcon) {
        mHeaderHeartIcon.className = mIsLiked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
        mHeaderHeartIcon.style.color = '#e11d48';
    }
    if (mHeaderLikeBtn) {
        mHeaderLikeBtn.classList.toggle('active', mIsLiked);
    }

    // 모바일 상세 팝업 열릴 때 본인 게시물 및 조회 상태 확인
    const mCurUserId = String(window.currentUserId || window.CURRENT_USER_ID || '').trim();
    const mPostOwnerId = String(postData.ENT_USER_ID || postData.user_id || postData.USER_ID || postData.ent_user_id || '').trim();
    const isMinePost = !!(mCurUserId && mPostOwnerId && mCurUserId === mPostOwnerId);

    fetch(`/api/post/user_actions/${postData.post_id}`)
        .then(res => res.json())
        .then(data => {
            if (data && data.success && data.actions) {
                const mIsLiked = !!data.actions.is_liked;
                if (mBtnLikePopup) mBtnLikePopup.classList.toggle('active', mIsLiked);
                if (mHeartIcon) {
                    mHeartIcon.className = mIsLiked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
                    mHeartIcon.style.color = mIsLiked ? '#e11d48' : '';
                }
                if (mHeaderHeartIcon) {
                    mHeaderHeartIcon.className = mIsLiked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
                    mHeaderHeartIcon.style.color = '#e11d48';
                }
                if (mHeaderLikeBtn) mHeaderLikeBtn.classList.toggle('active', mIsLiked);
                
                if (data.actions.is_commented !== undefined) {
                    const btnCommentPopup = document.getElementById('mDetailBtnComment');
                    if (btnCommentPopup) {
                        btnCommentPopup.classList.toggle('active', !!data.actions.is_commented);
                        const icon = btnCommentPopup.querySelector('i');
                        if (icon) icon.className = data.actions.is_commented ? 'fa-solid fa-comment' : 'fa-regular fa-comment';
                    }
                }
                if (data.actions.is_shared !== undefined) {
                    const mIsShared = !!data.actions.is_shared;
                    const btnSharePopup = document.getElementById('mDetailBtnShare');
                    if (btnSharePopup) btnSharePopup.classList.toggle('active', mIsShared);
                }
                const mBtnViewPopup = document.getElementById('mDetailBtnView');
                if (mBtnViewPopup) {
                    const mIsViewAct = !isMinePost && (data.actions.is_viewed === true || data.actions.is_viewed === undefined || !isClosedRound);
                    mBtnViewPopup.classList.toggle('active', mIsViewAct);
                    const icon = mBtnViewPopup.querySelector('i');
                    if (icon) icon.className = mIsViewAct ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
                }
            }
        })
        .catch(err => console.error(err));

    // 참가번호 뱃지 바인딩 (모바일 이미지 좌측 하단)
    const mEntryNoEl = document.getElementById('mDetailEntryNoText');
    const mEntryNoBadge = document.getElementById('mDetailEntryNoBadge');
    const mRoundNoVal = postData.ROUND_NO || postData.round_no || (postData.post_id && String(postData.post_id).includes('_') ? String(postData.post_id).split('_')[1] : null);
    if (mEntryNoBadge && mEntryNoEl) {
        if (mRoundNoVal) {
            mEntryNoEl.textContent = `참가 ${mRoundNoVal}번`;
            mEntryNoBadge.style.display = 'inline-flex';
        } else {
            mEntryNoBadge.style.display = 'none';
        }
    }

    window.currentMobileDetailPostId = postData.post_id;
    loadMobileComments(postData.post_id);

    // 모바일 상세 팝업 열릴 때 자동 조회수(+1) 이벤트 트리거 (단, 진행 중 회차 + 본인 게시물이 아닐 때만)
    if (!isClosedRound && postData.post_id && !isMinePost) {
        triggerMobileEvent(postData.post_id, 'view');
    }


    const mCommentFormContainer = document.getElementById('mDetailCommentFormContainer');
    const mCommentScoreNotice = document.getElementById('mDetailCommentScoreNotice');
    const mShareIconBtn = document.getElementById('mDetailShareIconBtn');

    const mBtnViewPopup = document.getElementById('mDetailBtnView');
    if (mBtnViewPopup) {
        const mIsInitViewAct = !isMinePost && (!isClosedRound || !!(postData.is_viewed || (postData.actions && postData.actions.is_viewed)));
        mBtnViewPopup.classList.toggle('active', mIsInitViewAct);
        const icon = mBtnViewPopup.querySelector('i');
        if (icon) icon.className = mIsInitViewAct ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
    }
    const mBtnCommentPopup = document.getElementById('mDetailBtnComment');
    mBtnSharePopup = mBtnSharePopup || document.getElementById('mDetailBtnShare');

    if (isClosedRound) {
        if (mCommentFormContainer) mCommentFormContainer.style.display = 'none';
        if (mCommentScoreNotice) mCommentScoreNotice.style.display = 'none';
        if (mShareIconBtn) {
            mShareIconBtn.style.display = 'inline-flex';
            mShareIconBtn.style.pointerEvents = 'auto';
            mShareIconBtn.style.cursor = 'pointer';
            mShareIconBtn.onclick = function(e) {
                if (e) e.stopPropagation();
                handleShareClick();
            };
        }
        [mBtnViewPopup, mBtnLikePopup, mBtnCommentPopup].forEach(el => {
            if (el) {
                el.style.display = 'flex';
                el.style.pointerEvents = 'none';
                el.style.cursor = 'default';
                el.onclick = null;
            }
        });
        if (mBtnSharePopup) {
            mBtnSharePopup.style.display = 'flex';
            mBtnSharePopup.style.pointerEvents = 'auto';
            mBtnSharePopup.style.cursor = 'pointer';
            mBtnSharePopup.onclick = function(e) {
                if (e) e.stopPropagation();
                handleShareClick();
            };
        }
    } else {
        if (mCommentFormContainer) mCommentFormContainer.style.display = 'flex';
        if (mCommentScoreNotice) mCommentScoreNotice.style.display = '';
        if (mShareIconBtn) mShareIconBtn.style.display = 'inline-flex';
        [mBtnViewPopup, mBtnLikePopup, mBtnCommentPopup, mBtnSharePopup].forEach(el => {
            if (el) {
                el.style.display = 'flex';
                el.style.pointerEvents = '';
                el.style.cursor = '';
            }
        });
    }

    const mCleanId = String(postData.post_id);
    const mRawEntId = mCleanId.replace(/^\d+_/, '');
    const mCard = document.getElementById(`m-post-card-${mCleanId}`) || 
                  document.getElementById(`m-post-card-${mRawEntId}`) ||
                  document.querySelector(`[data-post-id="${mCleanId}"]`) ||
                  document.querySelector(`[data-ent-user-id="${mRawEntId}"]`) ||
                  document.querySelector(`[data-ent-user-id="${mCleanId}"]`);

    const isUserLoggedIn = !!(window.isUserLoggedIn || window.CURRENT_USER_ID || window.currentUserId);
    const isViewed = !!(postData.is_viewed || (postData.actions && postData.actions.is_viewed) || (mCard && mCard.querySelector('.btn-view.active')));
    const isViewAct = isUserLoggedIn && !isMinePost && (!isClosedRound || isViewed);
    if (mCard) {
        const mBtnView = mCard.querySelector('.btn-view');
        if (mBtnView) {
            mBtnView.classList.toggle('active', isViewAct);
            const icon = mBtnView.querySelector('i');
            if (icon) icon.className = isViewAct ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
        }
    }
    if (mBtnViewPopup) {
        mBtnViewPopup.classList.toggle('active', isViewAct);
        const icon = mBtnViewPopup.querySelector('i');
        if (icon) icon.className = isViewAct ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
    }

    detailModal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // 팝업 active 활성화 틱 및 애니메이션 후 스크롤 100% 최상단 보정
    resetMobileModalScroll();
    requestAnimationFrame(() => {
        resetMobileModalScroll();
        setTimeout(resetMobileModalScroll, 0);
        setTimeout(resetMobileModalScroll, 50);
        setTimeout(resetMobileModalScroll, 150);
    });
}

function closeMobileDetailModal() {
    if (window.mYtbFadeTimer) {
        clearTimeout(window.mYtbFadeTimer);
        window.mYtbFadeTimer = null;
    }
    if (window.mYtbFadeTimer_loop) {
        clearTimeout(window.mYtbFadeTimer_loop);
        window.mYtbFadeTimer_loop = null;
    }
    if (window.mYtbPlayer && typeof window.mYtbPlayer.destroy === 'function') {
        try { window.mYtbPlayer.destroy(); } catch(e) {}
        window.mYtbPlayer = null;
    }
    const mShowBtn = document.getElementById('mDetailShowImgBtn');
    if (mShowBtn) mShowBtn.style.display = 'none';
    const detailModal = document.getElementById('mDetailModal');
    if (detailModal) {
        detailModal.classList.remove('active', 'show');
        detailModal.style.display = '';
        resetMobileModalScroll();
        document.body.style.overflow = '';
    }
    const mImgEl = document.getElementById('mDetailImg');
    if (mImgEl) {
        mImgEl.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>';
        mImgEl.style.opacity = '1';
        mImgEl.style.pointerEvents = 'auto';
    }
    const mReplayBtn = document.getElementById('mDetailYtbReplayBtn');
    if (mReplayBtn) mReplayBtn.style.display = 'none';
    const mCountdownEl = document.getElementById('mDetailYtbCountdown');
    if (mCountdownEl) mCountdownEl.style.display = 'none';
    if (window.mYtbFadeTimer_countInterval) {
        clearInterval(window.mYtbFadeTimer_countInterval);
        window.mYtbFadeTimer_countInterval = null;
    }
    const mYtbContainer = document.getElementById('mDetailYtbContainer');
    if (mYtbContainer) {
        mYtbContainer.innerHTML = '';
        mYtbContainer.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const mDetailModal = document.getElementById('mDetailModal');
    if (mDetailModal) {
        let isPointerDownOnBackdrop = false;
        const handlePointerDown = (e) => {
            isPointerDownOnBackdrop = (e.target === mDetailModal || e.target.classList.contains('m-modal-backdrop'));
        };
        mDetailModal.addEventListener('mousedown', handlePointerDown);
        mDetailModal.addEventListener('touchstart', handlePointerDown, { passive: true });
        mDetailModal.addEventListener('click', function(e) {
            if ((e.target === mDetailModal || e.target.classList.contains('m-modal-backdrop')) && isPointerDownOnBackdrop) {
                closeMobileDetailModal();
            }
            isPointerDownOnBackdrop = false;
        });
    }
});

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
    const mCommentEl = document.getElementById('mDetailCommentCount');
    const countVal = comments ? comments.length : 0;
    if (headerCountEl) headerCountEl.textContent = `(${countVal})`;
    if (mCommentEl) mCommentEl.textContent = Number(countVal).toLocaleString();
    
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
    
    const rawCurrentId = String(window.CURRENT_USER_ID || '');
    const currentUserId = rawCurrentId.split('_post_')[0];
    const currentNickname = window.CURRENT_USER_NICKNAME;

    listEl.innerHTML = comments.map(c => {
        const rawCUserId = String(c.user_id || c.USER_ID || c.CMT_USER_ID || '');
        const cUserId = rawCUserId.split('_post_')[0];
        const cNickname = c.user_nickname || c.NK_NM;
        const isMine = c.is_mine === true || (currentUserId && cUserId && cUserId === currentUserId) || (currentNickname && cNickname && cNickname === currentNickname);

        const deleteBtnHtml = isMine ? `
            <button onclick="deleteMobileDetailComment('${c.CMT_USER_ID || c.user_id || c.USER_ID}')" style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); color: #ef4444; font-size: 0.68rem; cursor: pointer; padding: 0.1rem 0.35rem; border-radius: 5px; font-weight: 700; transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.2rem;" title="댓글 삭제">
                <i class="fa-solid fa-trash-can" style="font-size: 0.62rem;"></i> 삭제
            </button>
        ` : '';

        return `
            <div style="background: #f8fafc; border: 1px solid var(--border-light); border-radius: 10px; padding: 0.4rem 0.6rem; font-size: 0.78rem; display: flex; flex-direction: column; gap: 0.15rem;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <a href="${cUserId ? `/profile?user_id=${encodeURIComponent(cUserId)}` : 'javascript:void(0)'}" style="display: flex; align-items: center; gap: 0.3rem; font-weight: 800; color: var(--text-primary); text-decoration: none; cursor: ${cUserId ? 'pointer' : 'default'}; transition: opacity 0.2s;" ${cUserId ? `title="${escapeHtml(cNickname || '집사')} 님의 프로필 보기"` : ''} onmouseover="if('${cUserId}') this.style.opacity='0.75'" onmouseout="this.style.opacity='1'">
                        <img src="${c.user_profile || '/static/image/profile/default_profile.png'}" style="width: 16px; height: 16px; border-radius: 50%; object-fit: cover;">
                        <span>${escapeHtml(c.user_nickname || '집사')}</span>
                    </a>
                    <div style="display: flex; align-items: center; gap: 0.4rem;">
                        <span style="font-size: 0.68rem; color: var(--text-muted);">${formatTimeAgo(c.created_at || c.ENT_DT || c.CMT_DT || '')}</span>
                        ${deleteBtnHtml}
                    </div>
                </div>
                <div style="color: var(--text-secondary); font-weight: 500; word-break: break-all; padding-left: 1.2rem;">
                    ${escapeHtml(c.content)}
                </div>
            </div>
        `;
    }).join('');
}

function deleteMobileDetailComment(cmtUserId) {
    if (!window.currentMobileDetailPostId) return;
    if (!confirm('작성하신 댓글을 삭제하시겠습니까?')) return;

    fetch(`/api/comments/${window.currentMobileDetailPostId}/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cmt_user_id: cmtUserId })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            showMobileToast(data.message || '댓글 삭제 실패', 'warning');
            return;
        }
        showMobileToast('댓글이 삭제되었습니다.', 'info');
        loadMobileComments(window.currentMobileDetailPostId);
        
        // 차감된 수치 및 점수 UI 실시간 반영
        const finalScore = Number(data.score !== undefined ? data.score : (data.new_score !== undefined ? data.new_score : (data.event_res ? data.event_res.score : 0)));
        const finalView = (data.view_count !== undefined ? data.view_count : (data.event_res ? data.event_res.view_count : undefined));
        const finalLike = (data.like_count !== undefined ? data.like_count : (data.event_res ? data.event_res.like_count : undefined));
        const finalComment = (data.comment_count !== undefined ? data.comment_count : (data.event_res ? data.event_res.comment_count : undefined));

        const mPostId = window.currentMobileDetailPostId;
        
        window.currentMobileDetailPostIsCommented = false;
        if (window.currentMobileDetailPost) {
            window.currentMobileDetailPost.is_commented = false;
            if (window.currentMobileDetailPost.actions) window.currentMobileDetailPost.actions.is_commented = false;
        }

        const mBtnCommentPopup = document.getElementById('mDetailBtnComment');
        if (mBtnCommentPopup) {
            mBtnCommentPopup.classList.remove('active');
            const icon = mBtnCommentPopup.querySelector('i');
            if (icon) icon.className = 'fa-regular fa-comment';
        }

        if (mPostId) {
            const mScoreEl = document.getElementById('mDetailScoreNum');
            if (mScoreEl && finalScore !== undefined) {
                mScoreEl.textContent = finalScore.toLocaleString();
            }

            const mCommentEl = document.getElementById('mDetailCommentCount');
            if (mCommentEl && finalComment !== undefined) {
                mCommentEl.textContent = Number(finalComment || 0).toLocaleString();
            }

            const mViewEl = document.getElementById('mDetailViewCount');
            if (mViewEl && finalView !== undefined) {
                mViewEl.textContent = Number(finalView || 0).toLocaleString();
            }

            const mLikeEl = document.getElementById('mDetailLikeCount');
            if (mLikeEl && finalLike !== undefined) {
                mLikeEl.textContent = Number(finalLike || 0).toLocaleString();
            }

            const cleanId = String(mPostId);
            const rawEntId = cleanId.replace(/^\d+_/, '');
            const card = document.getElementById(`m-post-card-${cleanId}`) || 
                         document.getElementById(`m-post-card-${rawEntId}`) ||
                         document.querySelector(`[data-post-id="${cleanId}"]`) ||
                         document.querySelector(`[data-ent-user-id="${rawEntId}"]`) ||
                         document.querySelector(`[data-ent-user-id="${cleanId}"]`);
                         
            if (card) {
                const btnCardComment = card.querySelector('.m-btn-comment') || card.querySelector('.btn-comment');
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
            }
        }
    })
    .catch(err => {
        console.error('댓글 삭제 오류:', err);
        showMobileToast('댓글 삭제 중 오류가 발생했습니다.', 'error');
    });
}

function submitMobileDetailComment() {
    const inputEl = document.getElementById('mDetailCommentInput');
    if (!inputEl || !window.currentMobileDetailPostId) return;

    if (window.currentMobileDetailPostData) {
        const entUserId = window.currentMobileDetailPostData.ENT_USER_ID || window.currentMobileDetailPostData.user_id;
        if (window.currentUserId && entUserId && String(window.currentUserId) === String(entUserId)) {
            if (typeof showToast === 'function') showToast('💡 본인이 등록한 게시물에는 댓글을 남기실 수 없습니다. 🐾', 'warning');
            else alert('💡 본인이 등록한 게시물에는 댓글을 남기실 수 없습니다. 🐾');
            return;
        }
    }
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
            if (typeof showToast === 'function') {
                showToast(data.message || '댓글 작성 실패', 'warning');
            } else {
                alert(data.message || '댓글 작성 실패');
            }
            if (data.require_login) {
                const mAuthModal = document.getElementById('mAuthModal');
                if (mAuthModal) mAuthModal.classList.add('active');
            }
            return;
        }
        
        inputEl.value = '';
        alert('한줄 댓글 작성 완료! (+10점 반영)');
        
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
        
        // 서버 DB에서 최종 재계산된 3요소 및 SCORE 데이터 활용
        const finalScore = Number(data.score !== undefined ? data.score : (data.new_score !== undefined ? data.new_score : (data.event_res ? data.event_res.score : 0)));
        const finalView = (data.view_count !== undefined ? data.view_count : (data.event_res ? data.event_res.view_count : undefined));
        const finalLike = (data.like_count !== undefined ? data.like_count : (data.event_res ? data.event_res.like_count : undefined));
        const finalComment = (data.comment_count !== undefined ? data.comment_count : (data.event_res ? data.event_res.comment_count : undefined));

        const mPostId = window.currentMobileDetailPostId;
        if (mPostId) {
            const mScoreEl = document.getElementById('mDetailScoreNum');
            if (mScoreEl && finalScore) {
                mScoreEl.textContent = finalScore.toLocaleString();
            }

            const mCommentEl = document.getElementById('mDetailCommentCount');
            if (mCommentEl && finalComment !== undefined) {
                mCommentEl.textContent = Number(finalComment || 0).toLocaleString();
            }

            const mLikeEl = document.getElementById('mDetailLikeCount');
            if (mLikeEl && finalLike !== undefined) {
                mLikeEl.textContent = Number(finalLike || 0).toLocaleString();
            }

            const mViewEl = document.getElementById('mDetailViewCount');
            if (mViewEl && finalView !== undefined) {
                mViewEl.textContent = Number(finalView || 0).toLocaleString();
            }

            const mCleanId = String(mPostId);
            const mRawEntId = mCleanId.replace(/^\d+_/, '');
            const card = document.getElementById(`m-post-card-${mCleanId}`) || 
                         document.getElementById(`m-post-card-${mRawEntId}`) ||
                         document.querySelector(`[data-post-id="${mCleanId}"]`) ||
                         document.querySelector(`[data-ent-user-id="${mRawEntId}"]`) ||
                         document.querySelector(`[data-ent-user-id="${mCleanId}"]`);

            if (card) {
                const btnCardComment = card.querySelector('.btn-comment') || card.querySelector('.m-btn-comment');
                if (btnCardComment) {
                    btnCardComment.classList.add('active');
                    const icon = btnCardComment.querySelector('i');
                    if (icon) icon.className = 'fa-solid fa-comment';
                }

                const cardComment = card.querySelector('.comment-count');
                if (cardComment && finalComment !== undefined) {
                    cardComment.textContent = Number(finalComment || 0).toLocaleString();
                }
                const cardScore = card.querySelector('.m-card-score, .score-num');
                if (cardScore && finalScore) {
                    cardScore.textContent = `⭐ ${finalScore.toLocaleString()}`;
                }
            }
        }

        loadMobileComments(window.currentMobileDetailPostId);
    })
    .catch(err => {
        console.error('모바일 댓글 작성 오류:', err);
    });
}

async function deleteMobileCurrentPost() {
    const postId = window.currentMobileDetailPostId;
    if (!postId) {
        if (typeof showToast === 'function') showToast('게시물 정보를 찾을 수 없습니다.', 'error');
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
            if (typeof showToast === 'function') showToast('🗑️ 출전이 성공적으로 포기(삭제)되었습니다.');
            closeMobileDetailModal();
            const cardEl = document.getElementById(`m-post-card-${postId}`);
            if (cardEl) {
                cardEl.remove();
            } else {
                setTimeout(() => location.reload(), 500);
            }
        } else {
            if (typeof showToast === 'function') showToast(result.message || '출전 포기 처리 중 오류가 발생했습니다.', 'error');
        }
    } catch (e) {
        console.error('deleteMobileCurrentPost error:', e);
        if (typeof showToast === 'function') showToast('서버 통신 중 오류가 발생했습니다.', 'error');
    }
}

window.openMobileDetailModal = openMobileDetailModal;
window.closeMobileDetailModal = closeMobileDetailModal;
window.deleteMobileCurrentPost = deleteMobileCurrentPost;
if (typeof window.openBadgeZoomModal === 'function') {
    window.openBadgeZoomModal = window.openBadgeZoomModal;
}

async function copyPostShareUrl(contestRound, roundNo, shareSn, targetPostId) {
    if (contestRound === 'None' || contestRound === 'undefined' || contestRound === 'null') contestRound = null;
    if (roundNo === 'None' || roundNo === 'undefined' || roundNo === 'null') roundNo = null;
    if (shareSn === 'None' || shareSn === 'undefined' || shareSn === 'null') shareSn = null;

    const postId = targetPostId || window.currentMobileDetailPostId;

    if (!contestRound || !roundNo) {
        if (window.currentMobileDetailPostData) {
            const p = window.currentMobileDetailPostData;
            contestRound = p.contest_id || p.CONTEST_ROUND || contestRound;
            roundNo = p.round_no || p.ROUND_NO || roundNo;
            shareSn = p.share_sn || p.SHARE_SN || shareSn;
        }
        if ((!contestRound || !roundNo) && postId) {
            const parts = String(postId).split('_');
            if (parts.length >= 2) {
                contestRound = parts[0];
                roundNo = parts[1];
            }
        }
    }

    let isClosedContest = false;
    if (window.currentMobileDetailPostData) {
        const p = window.currentMobileDetailPostData;
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

    // 모바일 브라우저 Web Share API 시도 (카카오톡, 메시지 등 직접 공유 기능)
    let webShareDone = false;
    if (navigator.share && /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent)) {
        try {
            await navigator.share({
                title: 'Paw Star - 펫 랭킹 콘테스트',
                text: '귀여운 반려동물에게 투표해주세요! 🐾',
                url: shareUrl
            });
            webShareDone = true;
        } catch (err) {
            console.log('Web share skipped or user cancelled, fallback to clipboard:', err);
        }
    }

    if (!webShareDone) {
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
}

async function handleShareClick() {
    const postId = window.currentMobileDetailPostId;
    if (window.currentMobileDetailPostData) {
        const p = window.currentMobileDetailPostData;
        const cRound = p.contest_id || p.CONTEST_ROUND;
        const rNo = p.round_no || p.ROUND_NO;
        const sSn = p.share_sn || p.SHARE_SN;
        await copyPostShareUrl(cRound, rNo, sSn, postId);
    } else {
        await copyPostShareUrl(null, null, null, postId);
    }
}

async function handleShareClickForCard(postId, contestRound, roundNo, shareSn) {
    await copyPostShareUrl(contestRound, roundNo, shareSn, postId);
}

window.copyPostShareUrl = copyPostShareUrl;
window.handleShareClick = handleShareClick;
window.handleShareClickForCard = handleShareClickForCard;

// 모바일 URL 쿼리 파라미터 open_post 감지 시 자동 팝업 오픈
function checkAndAutoOpenMobilePost() {
    const urlParams = new URLSearchParams(window.location.search);
    const openPostId = urlParams.get('open_post');
    if (openPostId) {
        const isHOFPage = window.location.pathname.includes('hall-of-fame');
        if (window.postsDataStore && window.postsDataStore[openPostId]) {
            openMobileDetailModal(window.postsDataStore[openPostId], isHOFPage);
        } else {
            fetch(`/api/post/detail/${openPostId}`)
                .then(res => res.json())
                .then(data => {
                    if (data.success && data.post) {
                        openMobileDetailModal(data.post, isHOFPage);
                    }
                })
                .catch(err => console.error('모바일 자동 포스트 팝업 실패:', err));
        }
        const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
        window.history.replaceState({ path: cleanUrl }, '', cleanUrl);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(checkAndAutoOpenMobilePost, 300);
});

// ==========================================
// 🚀 모바일 비동기 (AJAX) 필터 & 피드 실시간 갱신 시스템
// ==========================================

let mobileFilterState = {
    contest_id: document.getElementById('mCurrentContestId') ? document.getElementById('mCurrentContestId').value : '1',
    sort: document.getElementById('mCurrentSort') ? document.getElementById('mCurrentSort').value : 'latest',
    pet_type: document.getElementById('mCurrentPetType') ? document.getElementById('mCurrentPetType').value : 'all',
    q: document.getElementById('mSearchInput') ? document.getElementById('mSearchInput').value : ''
};

function formatTimeAgo(dateStr) {
    if (!dateStr) return '';
    try {
        const rawStr = dateStr.toString().trim();
        const past = new Date(rawStr.replace(/-/g, '/').split('.')[0]);
        if (isNaN(past.getTime())) return rawStr.substring(0, 10);

        const now = new Date();
        const diffSec = Math.floor((now - past) / 1000);
        if (diffSec < 0 || diffSec < 60) return '방금 전';

        const diffMin = Math.floor(diffSec / 60);
        if (diffMin < 60) return `${diffMin}분 전`;

        const diffHour = Math.floor(diffMin / 60);
        if (diffHour < 24) return `${diffHour}시간 전`;

        const diffDay = Math.floor(diffHour / 24);
        if (diffDay < 30) return `${diffDay}일 전`;

        const diffMonth = Math.floor(diffDay / 30);
        if (diffMonth < 12) return `${diffMonth}개월 전`;

        return `${Math.floor(diffMonth / 12)}년 전`;
    } catch (e) {
        return (dateStr || '').toString().substring(0, 10);
    }
}

async function fetchMobilePostsAjax(params = {}) {
    if (params.contest_id !== undefined) mobileFilterState.contest_id = params.contest_id;
    if (params.sort !== undefined) mobileFilterState.sort = params.sort;
    if (params.pet_type !== undefined) mobileFilterState.pet_type = params.pet_type;
    if (params.q !== undefined) mobileFilterState.q = params.q;

    const newUrl = `/m/?contest_id=${mobileFilterState.contest_id}&sort=${mobileFilterState.sort}&pet_type=${encodeURIComponent(mobileFilterState.pet_type)}&q=${encodeURIComponent(mobileFilterState.q)}`;
    window.history.pushState(mobileFilterState, '', newUrl);

    await loadMobileFeed();
}

async function loadMobileFeed() {
    const feedGrid = document.querySelector('.m-feed-grid');
    if (feedGrid) {
        feedGrid.style.opacity = '0.5';
        feedGrid.style.transition = 'opacity 0.2s ease';
    }

    try {
        const apiUrl = `/api/m/posts?contest_id=${mobileFilterState.contest_id}&sort=${mobileFilterState.sort}&pet_type=${encodeURIComponent(mobileFilterState.pet_type)}&q=${encodeURIComponent(mobileFilterState.q)}`;
        const res = await fetch(apiUrl);
        const data = await res.json();

        if (data.success && feedGrid) {
            renderMobileFeedGrid(data.posts);
        }
    } catch (err) {
        console.error('모바일 AJAX 피드 로드 실패:', err);
    } finally {
        if (feedGrid) {
            feedGrid.style.opacity = '1';
        }
    }
}

function renderMobileFeedGrid(posts) {
    const feedGrid = document.querySelector('.m-feed-grid');
    if (!feedGrid) return;

    if (!posts || posts.length === 0) {
        feedGrid.innerHTML = `
            <div style="grid-column: 1 / -1; padding: 4rem 1rem; text-align: center; color: #64748b; background: #ffffff; border-radius: 16px; margin: 0 0.85rem;">
                <i class="fa-solid fa-paw" style="font-size: 2.8rem; color: #cbd5e1; margin-bottom: 1rem;"></i>
                <p style="font-size: 0.95rem; font-weight: 800; color: #334155;">조건에 맞는 참가 작품이 없습니다.</p>
                <p style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.4rem;">다른 검색어나 필터를 선택해 보세요!</p>
            </div>
        `;
        return;
    }

    let html = '';
    posts.forEach(p => {
        const postId = p.post_id || p.ENT_USER_ID;
        const entUserId = p.ENT_USER_ID;
        const pImg = (p.PHT_PATH && p.PHT_FILE1) ? `${p.PHT_PATH}/${p.PHT_FILE1}` : (p.IMAGE_PATH || p.image_path || p.media_url || '');
        const pTitle = p.TITLE || p.title || '';
        const pKindRaw = p.KIND_NM || p.pet_type || '반려동물';
        const pKindClean = pKindRaw.replace(/🐕 |🐈 |🐹 |🦜 |🐟 |🐢 |🐴 |🐾 /g, '');
        const pUserNm = p.NK_NM || p.user_nickname || p.USER_NM || p.user_name || '출전자';
        const pAvatar = p.USER_AVATAR || p.user_avatar || p.PROFILE_URL || p.user_profile || '/static/image/profile/default_profile.png';
        const pConts = p.CONTS || p.description || '';
        const pScore = p.TOTAL_SCORE || p.total_score || p.score || 0;
        const pHeartCount = p.HEART_COUNT || p.heart_count || p.like_count || 0;
        const pCommentCount = p.COMMENT_COUNT || p.comment_count || 0;
        const pShareScore = p.SHARE_SCORE || p.share_score || 0;
        const pViewCount = p.VIEW_COUNT || p.view_count || 0;
        const pDtRaw = p.REG_DT || p.created_at || p.ENT_DT || '';
        const pDtAgo = formatTimeAgo(pDtRaw);
        const pPostJsonData = JSON.stringify(p).replace(/"/g, '&quot;');

        const pPetNm = p.PET_NM || p.pet_name || '';

        let chipIcon = 'fa-solid fa-paw';
        if (pKindRaw.includes('강아지') || pKindRaw.includes('개')) chipIcon = 'fa-solid fa-dog';
        else if (pKindRaw.includes('고양이')) chipIcon = 'fa-solid fa-cat';
        else if (pKindRaw.includes('거북이') || pKindRaw.includes('파충류') || pKindRaw.includes('도마뱀')) chipIcon = 'fa-solid fa-frog';
        else if (pKindRaw.includes('햄스터') || pKindRaw.includes('소동물') || pKindRaw.includes('토끼') || pKindRaw.includes('고슴도치')) chipIcon = 'fa-solid fa-otter';
        else if (pKindRaw.includes('새') || pKindRaw.includes('앵무새') || pKindRaw.includes('조류')) chipIcon = 'fa-solid fa-crow';
        else if (pKindRaw.includes('말') || pKindRaw.includes('큰동물')) chipIcon = 'fa-solid fa-horse';
        else if (pKindRaw.includes('어류') || pKindRaw.includes('관상어') || pKindRaw.includes('물고기')) chipIcon = 'fa-solid fa-fish';

        let badgeHtml = '';
        if (p.awards && p.awards.length > 0) {
            let awardsHtml = '';
            p.awards.forEach(aw => {
                const awardCdStr = String(aw.award_cd || aw.AWARD_CD || '');
                const awardNmStr = String(aw.award_nm || aw.AWARD_NM || '');
                const awRank = aw.ranking || aw.RANKING;
                let badgeText = '수상작';
                let bgStyle = 'background: linear-gradient(135deg, rgba(243,232,255,0.95), rgba(192,132,252,0.9)); color: #3b0764;';
                if (awardCdStr.includes('P001A101') || (!awardCdStr && awardNmStr.includes('슈퍼'))) {
                    badgeText = '슈퍼스타';
                    bgStyle = 'background: linear-gradient(135deg, rgba(254,249,195,0.95), rgba(253,224,71,0.9)); color: #713f12;';
                } else if (awardCdStr.includes('P001A102') || (!awardCdStr && awardNmStr.includes('브라이트'))) {
                    badgeText = '브라이트스타';
                    bgStyle = 'background: linear-gradient(135deg, rgba(240,249,255,0.95), rgba(125,211,252,0.9)); color: #0369a1;';
                } else if (awardCdStr.includes('P001A103') || (!awardCdStr && awardNmStr.includes('라이징'))) {
                    badgeText = '라이징스타';
                    bgStyle = 'background: linear-gradient(135deg, rgba(247,254,231,0.95), rgba(163,230,53,0.9)); color: #3f6212;';
                } else {
                    badgeText = `<i class="${chipIcon}" style="margin-right: 0.25rem;"></i> 패밀리${awRank ? ` ${awRank}위` : ''}`;
                }
                awardsHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: 0.15rem 0.42rem; font-size: 0.56rem; ${bgStyle}">${badgeText}</div>`;
            });
            badgeHtml = `<div class="award-badges-overlay" style="position: absolute; top: 0.4rem; right: 0.4rem; left: auto; display: flex; flex-direction: row; align-items: center; justify-content: flex-end; gap: 0.35rem; z-index: 10; pointer-events: none;">${awardsHtml}</div>`;
        } else {
            const isPostClosed = p.is_closed || p.closed || p.contest_stat === 'G001C002' || p.CONTEST_STAT === 'G001C002' || p.STATUS_CD === 'G001C002' || p.is_ended || p.IS_ENDED;
            const rkCand = p.rank_candidate || p.RANK_CANDIDATE || p.rank || p.ranking;
            const isCo = p.is_co_rank || p.IS_CO_RANK;
            if (rkCand && !isPostClosed) {
                const urlParams = new URLSearchParams(window.location.search);
                const currentPetType = urlParams.get('pet_type') || 'all';
                const isFamily = (currentPetType && currentPetType !== 'all');
                const catPrefix = isFamily ? '패밀리 ' : '전체 ';
                const prefix = catPrefix + (isCo ? '공동 ' : '');
                const rankTitle = `${prefix}${rkCand}위 후보`;
                
                let bgStyle = '';
                if (isFamily) {
                    bgStyle = 'background: linear-gradient(135deg, rgba(243,232,255,0.95), rgba(192,132,252,0.9)); color: #3b0764;';
                } else {
                    const rkNum = Number(rkCand);
                    if (rkNum === 1) {
                        bgStyle = 'background: linear-gradient(135deg, rgba(254,249,195,0.95), rgba(253,224,71,0.9)); color: #713f12;';
                    } else if (rkNum === 2) {
                        bgStyle = 'background: linear-gradient(135deg, rgba(240,249,255,0.95), rgba(125,211,252,0.9)); color: #0369a1;';
                    } else if (rkNum === 3) {
                        bgStyle = 'background: linear-gradient(135deg, rgba(247,254,231,0.95), rgba(163,230,53,0.9)); color: #3f6212;';
                    }
                }
                badgeHtml = `<div class="m-card-badge" style="font-size: 0.56rem; padding: 0.15rem 0.42rem; top: 0.4rem; left: 0.4rem; position: absolute; z-index: 10; ${bgStyle}">${rankTitle}</div>`;
            }
        }

        const mCurUserId = String(window.currentUserId || '').trim();
        const pEntUserId = String(entUserId || p.ENT_USER_ID || p.user_id || '').trim();
        const isMine = !!(mCurUserId && pEntUserId && mCurUserId === pEntUserId);
        const isViewActive = !isMine && !!(p.actions && p.actions.is_viewed);

        const rawInst = (p.SNS_INST || p.sns_inst || '').trim();
        const rawYtb = (p.SNS_YTB || p.sns_ytb || '').trim();
        const rawFsb = (p.SNS_FSB || p.sns_fsb || '').trim();
        const rawBlg = (p.SNS_BLG || p.sns_blg || '').trim();

        const formatSnsUrl = (url) => {
            if (!url) return '';
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                return 'https://' + url;
            }
            return url;
        };

        const instLink = formatSnsUrl(rawInst);
        const ytbLink = formatSnsUrl(rawYtb);
        const fsbLink = formatSnsUrl(rawFsb);
        const blgLink = formatSnsUrl(rawBlg);

        let snsOverlapHtml = '';
        if (instLink || ytbLink || fsbLink || blgLink) {
            let count = 0;
            snsOverlapHtml += `<div class="sns-overlap-group" style="margin-left: 0.25rem; flex-shrink: 0;" onclick="event.stopPropagation();">`;
            if (instLink) {
                count++;
                snsOverlapHtml += `<a href="${instLink}" target="_blank" rel="noopener noreferrer" title="Instagram" class="sns-overlap-item instagram" style="z-index: 4; ${count > 1 ? 'margin-left: -6px;' : ''}"><i class="fa-brands fa-instagram"></i></a>`;
            }
            if (ytbLink) {
                count++;
                snsOverlapHtml += `<a href="${ytbLink}" target="_blank" rel="noopener noreferrer" title="YouTube" class="sns-overlap-item youtube" style="z-index: 3; ${count > 1 ? 'margin-left: -6px;' : ''}"><i class="fa-brands fa-youtube"></i></a>`;
            }
            if (fsbLink) {
                count++;
                snsOverlapHtml += `<a href="${fsbLink}" target="_blank" rel="noopener noreferrer" title="Facebook" class="sns-overlap-item facebook" style="z-index: 2; ${count > 1 ? 'margin-left: -6px;' : ''}"><i class="fa-brands fa-facebook-f"></i></a>`;
            }
            if (blgLink) {
                count++;
                snsOverlapHtml += `<a href="${blgLink}" target="_blank" rel="noopener noreferrer" title="Blog" class="sns-overlap-item blog" style="z-index: 1; ${count > 1 ? 'margin-left: -6px;' : ''}"><i class="fa-solid fa-blog"></i></a>`;
            }
            snsOverlapHtml += `</div>`;
        }

        html += `
        <div class="m-feed-card" id="m-post-card-${entUserId || postId}" data-post-id="${postId}" data-ent-user-id="${entUserId}" onclick="openMobileDetailModal(${pPostJsonData})">
            <div class="m-card-thumb">
                <img src="${pImg}" alt="${pTitle}" loading="lazy">
                ${badgeHtml}
            </div>

            <div class="m-card-body">
                <!-- 1줄째: 프로필사진 + 작성자 닉네임 + 소셜 겹침 아이콘 -->
                <div class="m-card-author" style="display: flex; align-items: center; min-width: 0; width: 100%;">
                    <img src="${pAvatar}" alt="${pUserNm}" class="m-author-avatar">
                    <span class="m-author-name" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0;">${pUserNm}</span>
                    ${snsOverlapHtml}
                </div>

                <!-- 2줄째: 동물아이콘 + 동물유형명 + 동물 닉네임 -->
                <div class="m-pet-tag">
                    <span class="m-pet-kind-text" style="display: inline-flex; align-items: center; gap: 0.25rem;"><i class="${chipIcon}" style="color: #e11d48;"></i> ${pKindClean}</span>
                    ${pPetNm ? `<span class="m-pet-name-text">${pPetNm}</span>` : ''}
                </div>

                <!-- 3줄째: 게시글 제목 -->
                <h3 class="m-post-title">${pTitle}</h3>

                <div class="m-card-meta-divider">
                    <span class="m-post-date">${pDtAgo}</span>
                    <div class="m-card-total-score">
                        <i class="fa-solid fa-star"></i> <span class="score-num">${pScore.toLocaleString()}</span> 점
                    </div>
                </div>

                <div class="m-card-actions" onclick="event.stopPropagation();">
                    <div class="m-btn-action btn-view ${isViewActive ? 'active' : ''}" title="조회수">
                        <i class="fa-${isViewActive ? 'solid' : 'regular'} fa-eye"></i> <span class="view-count">${pViewCount.toLocaleString()}</span>
                    </div>
                    <div class="m-btn-action btn-like ${p.actions && p.actions.is_liked ? 'active' : ''}" title="좋아요 수">
                        <i class="fa-${p.actions && p.actions.is_liked ? 'solid' : 'regular'} fa-heart" ${p.actions && p.actions.is_liked ? 'style="color: #e11d48;"' : ''}></i> <span class="like-count">${pHeartCount.toLocaleString()}</span>
                    </div>
                    <div class="m-btn-action btn-comment ${p.actions && p.actions.is_commented ? 'active' : ''}" title="댓글 수">
                        <i class="fa-${p.actions && p.actions.is_commented ? 'solid' : 'regular'} fa-comment"></i> <span class="comment-count">${pCommentCount.toLocaleString()}</span>
                    </div>
                    <div class="m-btn-action btn-share ${p.actions && p.actions.is_shared ? 'active' : ''}" title="공유가입 수" onclick="event.stopPropagation(); handleShareClickForCard('${postId}', '${p.contest_id || p.CONTEST_ROUND}', '${p.round_no || p.ROUND_NO}', '${p.share_sn || p.SHARE_SN}');">
                        <i class="fa-solid fa-share-nodes"></i> <span class="share-count">${pShareScore.toLocaleString()}</span>
                    </div>
                </div>
            </div>
        </div>
        `;
    });

    feedGrid.innerHTML = html;
}

function selectMobileContestOption(el, contestId) {
    if (!contestId) return;

    try {
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('contest_id', contestId);
        window.location.href = currentUrl.toString();
    } catch (e) {
        window.location.href = '/m/?contest_id=' + encodeURIComponent(contestId);
    }
}

function handleMobileSearchSubmit(e) {
    if (e) e.preventDefault();
    const input = document.getElementById('mSearchInput');
    const qVal = input ? input.value : '';
    fetchMobilePostsAjax({ q: qVal });
}

function selectMobileSortOption(el, sortVal) {
    document.querySelectorAll('.custom-sort-option').forEach(opt => opt.classList.remove('selected'));
    if (el) el.classList.add('selected');

    const dropdown = document.getElementById('mCustomSortDropdown');
    if (dropdown) dropdown.classList.remove('open');

    const labelEl = document.getElementById('mSortTriggerLabel');
    if (labelEl) {
        if (sortVal === 'score') {
            labelEl.innerHTML = '<i class="fa-solid fa-arrow-up-wide-short"></i> 높은점수순';
        } else if (sortVal === 'low_score') {
            labelEl.innerHTML = '<i class="fa-solid fa-arrow-down-wide-short"></i> 낮은점수순';
        } else {
            labelEl.innerHTML = '<i class="fa-solid fa-clock"></i> 최신등록순';
        }
    }

    const mCurrentSort = document.getElementById('mCurrentSort');
    if (mCurrentSort) mCurrentSort.value = sortVal;

    fetchMobilePostsAjax({ sort: sortVal });
}

function selectMobilePetType(e, petTypeVal) {
    if (e) e.preventDefault();

    const chipGroup = document.getElementById('mPetTypeChipGroup');
    if (chipGroup) {
        chipGroup.querySelectorAll('.m-chip').forEach(chip => {
            chip.classList.remove('active');
            if (chip.getAttribute('data-pet-type') === petTypeVal) {
                chip.classList.add('active');
            }
        });
    }

    const mCurrentPetType = document.getElementById('mCurrentPetType');
    if (mCurrentPetType) mCurrentPetType.value = petTypeVal;

    fetchMobilePostsAjax({ pet_type: petTypeVal });
}

window.selectMobileContestOption = selectMobileContestOption;
window.handleMobileSearchSubmit = handleMobileSearchSubmit;
window.selectMobileSortOption = selectMobileSortOption;
window.selectMobilePetType = selectMobilePetType;
window.fetchMobilePostsAjax = fetchMobilePostsAjax;

function showMobileToast(message) {
    if (!message) return;
    alert(message);
}
window.showMobileToast = showMobileToast;

async function triggerMobileEvent(postId, eventType) {
    const mToast = (msg) => {
        alert(msg);
    };

    if (!window.isUserLoggedIn) {
        if (typeof openGoogleAuthModal === 'function') {
            openGoogleAuthModal();
        } else {
            mToast('로그인이 필요한 서비스입니다. 먼저 로그인해주세요! 🐾', 'warning');
        }
        return;
    }

    const postData = window.currentMobileDetailPostData || window.currentMobileDetailPost;
    if (postData) {
        const entUserId = String(postData.ENT_USER_ID || postData.user_id || '').trim();
        const mUserId = String(window.currentUserId || window.CURRENT_USER_ID || '').trim();
        if (mUserId && entUserId && mUserId === entUserId) {
            if (eventType === 'like' || eventType === 'unlike' || eventType === 'toggle_like') {
                mToast('본인의 게시물은 평가에 반영할 수 없습니다.', 'warning');
                return;
            }
        }
    }

    try {
        const res = await fetch('/api/post/event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                post_id: postId,
                event_type: eventType
            })
        });

        if (!res.ok) {
            const errText = await res.text();
            console.error('triggerMobileEvent HTTP error:', res.status, errText);
            if (typeof showToast === 'function') showToast('서버 오류가 발생했습니다.', 'warning');
            return;
        }

        const resData = await res.json();
        const data = (resData && resData.data) ? resData.data : resData;
        const isSuccess = resData.success && (data.success !== false);

        if (isSuccess) {
            const finalScore = Number(data.score !== undefined ? data.score : (data.new_score !== undefined ? data.new_score : (data.event_res ? data.event_res.score : 0)));
            const finalLike = (data.like_count !== undefined ? data.like_count : (data.event_res ? data.event_res.like_count : undefined));
            const finalView = (data.view_count !== undefined ? data.view_count : (data.event_res ? data.event_res.view_count : undefined));
            const finalComment = (data.comment_count !== undefined ? data.comment_count : (data.event_res ? data.event_res.comment_count : undefined));
            const finalShare = (data.share_count !== undefined ? data.share_count : (data.share_score !== undefined ? data.share_score : (data.event_res ? data.event_res.share_count : undefined)));
            
            const mScoreEl = document.getElementById('mDetailScoreNum');
            if (mScoreEl && finalScore) mScoreEl.textContent = finalScore.toLocaleString();

            const mLandingScoreEl = document.getElementById('mShareLandingScoreNum');
            if (mLandingScoreEl && finalScore) mLandingScoreEl.textContent = finalScore.toLocaleString();

            const mLikeEl = document.getElementById('mDetailLikeCount');
            if (mLikeEl && finalLike !== undefined) mLikeEl.textContent = Number(finalLike).toLocaleString();

            const mLandingLikeEl = document.getElementById('mShareLandingLikeCnt');
            if (mLandingLikeEl && finalLike !== undefined) mLandingLikeEl.textContent = Number(finalLike).toLocaleString();

            const mViewEl = document.getElementById('mDetailViewCount');
            if (mViewEl && finalView !== undefined) mViewEl.textContent = Number(finalView).toLocaleString();

            const mBtnViewPopup = document.getElementById('mDetailBtnView');
            if (mBtnViewPopup && finalView !== undefined) {
                const mCurUserId = String(window.currentUserId || window.CURRENT_USER_ID || '').trim();
                const mPostOwnerId = String((window.currentMobileDetailPostData || {}).ENT_USER_ID || (window.currentMobileDetailPostData || {}).user_id || (window.currentMobileDetailPostData || {}).USER_ID || (window.currentMobileDetailPostData || {}).ent_user_id || '').trim();
                const isMinePost = !!(mCurUserId && mPostOwnerId && mCurUserId === mPostOwnerId);
                const mIsViewAct = !isMinePost;
                mBtnViewPopup.classList.toggle('active', mIsViewAct);
                const icon = mBtnViewPopup.querySelector('i');
                if (icon) icon.className = mIsViewAct ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
            }

            const mLandingViewEl = document.getElementById('mShareLandingViewCnt');
            if (mLandingViewEl && finalView !== undefined) mLandingViewEl.textContent = Number(finalView).toLocaleString();

            const mCommentEl = document.getElementById('mDetailCommentCount');
            if (mCommentEl && finalComment !== undefined) mCommentEl.textContent = Number(finalComment).toLocaleString();

            const mLandingCmtEl = document.getElementById('mShareLandingCmtCnt');
            if (mLandingCmtEl && finalComment !== undefined) mLandingCmtEl.textContent = Number(finalComment).toLocaleString();

            const mShareEl = document.getElementById('mDetailShareCount');
            if (mShareEl && finalShare !== undefined) mShareEl.textContent = Number(finalShare).toLocaleString();

            const mLandingShareEl = document.getElementById('mShareLandingShareCnt');
            if (mLandingShareEl && finalShare !== undefined) mLandingShareEl.textContent = Number(finalShare).toLocaleString();

            if (eventType === 'share') {
                const mBtnSharePopup = document.getElementById('mDetailBtnShare');
                if (mBtnSharePopup) mBtnSharePopup.classList.add('active');

                const mLandingShareBtn = document.getElementById('mShareLandingShareBtn');
                if (mLandingShareBtn) {
                    mLandingShareBtn.classList.add('active');
                    mLandingShareBtn.style.background = '#ecfdf5';
                    mLandingShareBtn.style.border = '1.5px solid #34d399';
                    mLandingShareBtn.style.color = '#059669';
                    const icon = mLandingShareBtn.querySelector('i');
                    if (icon) icon.style.color = '#059669';
                    const span = mLandingShareBtn.querySelector('span');
                    if (span) span.style.color = '#059669';
                }
            }

            if (eventType === 'like') {
                const mBtnLikePopup = document.getElementById('mDetailBtnLike');
                const mHeartIcon = document.getElementById('mDetailHeartIcon');
                const mHeaderLikeBtn = document.getElementById('mDetailHeaderLikeBtn');
                const mHeaderHeartIcon = document.getElementById('mDetailHeaderHeartIcon');
                const isLiked = data.is_liked !== undefined ? data.is_liked : true;

                if (mBtnLikePopup && mHeartIcon) {
                    if (isLiked) {
                        mBtnLikePopup.classList.add('active');
                        mHeartIcon.className = 'fa-solid fa-heart';
                        mHeartIcon.style.color = '#e11d48';
                    } else {
                        mBtnLikePopup.classList.remove('active');
                        mHeartIcon.className = 'fa-regular fa-heart';
                        mHeartIcon.style.color = '';
                    }
                }

                if (mHeaderLikeBtn && mHeaderHeartIcon) {
                    mHeaderLikeBtn.classList.toggle('active', isLiked);
                    mHeaderHeartIcon.className = isLiked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
                    mHeaderHeartIcon.style.color = '#e11d48';
                }
            }

            const cleanId = String(postId);
            const rawEntId = cleanId.replace(/^\d+_/, '');
            const card = document.getElementById(`m-post-card-${cleanId}`) || 
                         document.getElementById(`m-post-card-${rawEntId}`) ||
                         document.querySelector(`[data-post-id="${cleanId}"]`) ||
                         document.querySelector(`[data-ent-user-id="${rawEntId}"]`) ||
                         document.querySelector(`[data-ent-user-id="${cleanId}"]`);

            if (card) {
                if (eventType === 'like') {
                    const btnCardLike = card.querySelector('.btn-like') || card.querySelector('.m-btn-action.btn-like');
                    if (btnCardLike) {
                        const isLiked = data.is_liked !== undefined ? data.is_liked : true;
                        btnCardLike.classList.toggle('active', isLiked);
                        const icon = btnCardLike.querySelector('i');
                        if (icon) {
                            icon.className = isLiked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
                            if (isLiked) icon.style.color = '#e11d48';
                            else icon.style.color = '';
                        }
                    }
                }

                if (eventType === 'share') {
                    const btnCardShare = card.querySelector('.btn-share') || card.querySelector('.m-btn-action.btn-share');
                    if (btnCardShare) {
                        btnCardShare.classList.add('active');
                    }
                }

                const cardLike = card.querySelector('.like-count');
                if (cardLike && finalLike !== undefined) {
                    cardLike.textContent = Number(finalLike).toLocaleString();
                }

                const cardView = card.querySelector('.view-count');
                if (cardView && finalView !== undefined) {
                    cardView.textContent = Number(finalView).toLocaleString();
                }

                const cardComment = card.querySelector('.comment-count');
                if (cardComment && finalComment !== undefined) {
                    cardComment.textContent = Number(finalComment).toLocaleString();
                }

                const cardShare = card.querySelector('.share-count');
                if (cardShare && finalShare !== undefined) {
                    cardShare.textContent = Number(finalShare).toLocaleString();
                }

                const cardScore = card.querySelector('.m-card-score, .score-num');
                if (cardScore && finalScore) {
                    cardScore.textContent = finalScore.toLocaleString();
                }
            }
        } else {
            if (resData.is_ended || data.is_ended) {
                return;
            }
            if (typeof showToast === 'function') showToast(data.message || resData.message || '요청 처리 실패', 'warning');
        }
    } catch (err) {
        console.error('triggerMobileEvent error:', err);
    }
}
window.triggerMobileEvent = triggerMobileEvent;

// 모바일 포스트 ID 기반 상세 팝업 오픈 헬퍼 함수
async function openPostById(postId, isHallOfFame = false) {
    if (!postId) return;
    if (!ensureLoggedIn()) return;
    const isServerSessionAlive = await verifyServerSessionAsync();
    if (!isServerSessionAlive) return;
    if (window.postsDataStore && window.postsDataStore[postId]) {
        openMobileDetailModal(window.postsDataStore[postId], isHallOfFame);
    } else {
        fetch(`/api/post/detail/${postId}`)
            .then(res => res.json())
            .then(data => {
                if (data.success && data.post) {
                    openMobileDetailModal(data.post, isHallOfFame);
                } else if (typeof showToast === 'function') {
                    showToast('해당 출전작 정보를 불러올 수 없습니다.', 'warning');
                } else {
                    alert('해당 출전작 정보를 불러올 수 없습니다.');
                }
            })
            .catch(err => console.error('모바일 출전작 팝업 로드 실패:', err));
    }
}
window.openPostById = openPostById;

// 모바일 푸터 공동 순위 슬롯 자동 순차 페이드 로테이션 (3.5초 간격 전환)
function initMobileFooterCoWinnerRotation() {
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

let mOgScale = 1;
let mOgTranslateX = 0;
let mOgTranslateY = 0;
let isMOgDragging = false;
let mOgStartX = 0;
let mOgStartY = 0;
let mOgInitialPinchDistance = null;
let mOgInitialScale = 1;
let mOgEventsInitialized = false;

function updateMOgImageTransform(animated = false) {
    const targetImg = document.getElementById('originalImageViewImg');
    const zoomText = document.getElementById('ogZoomPercent');
    const zoomContainer = document.getElementById('ogImageZoomContainer');
    
    if (!targetImg) return;
    
    if (animated) {
        targetImg.style.transition = 'transform 0.22s cubic-bezier(0.2, 0, 0.2, 1)';
    } else {
        targetImg.style.transition = 'none';
    }

    targetImg.style.transform = `translate(${mOgTranslateX}px, ${mOgTranslateY}px) scale(${mOgScale})`;
    
    if (zoomText) {
        zoomText.textContent = Math.round(mOgScale * 100) + '%';
    }

    if (zoomContainer) {
        if (mOgScale > 1) {
            zoomContainer.style.cursor = isMOgDragging ? 'grabbing' : 'grab';
        } else {
            zoomContainer.style.cursor = 'default';
        }
    }
}

function zoomOriginalImage(delta) {
    let newScale = mOgScale + delta;
    if (newScale < 0.8) newScale = 0.8;
    if (newScale > 5.0) newScale = 5.0;
    
    mOgScale = newScale;
    if (mOgScale <= 1) {
        mOgTranslateX = 0;
        mOgTranslateY = 0;
    }
    updateMOgImageTransform(true);
}

function resetOriginalImageZoom() {
    mOgScale = 1;
    mOgTranslateX = 0;
    mOgTranslateY = 0;
    updateMOgImageTransform(true);
}

function openOriginalImageModal(imgSrc) {
    if (!imgSrc || typeof imgSrc !== 'string' || imgSrc.includes('data:image/svg')) return;
    const modal = document.getElementById('originalImageModal');
    const targetImg = document.getElementById('originalImageViewImg');
    if (!modal || !targetImg) return;
    
    targetImg.src = imgSrc;
    resetOriginalImageZoom();
    
    modal.style.display = 'flex';
    modal.classList.add('show', 'active');
    
    initMOgZoomEventsOnce();
}

function closeOriginalImageModal() {
    const modal = document.getElementById('originalImageModal');
    if (!modal) return;
    resetOriginalImageZoom();
    modal.style.display = 'none';
    modal.classList.remove('show', 'active');
}

function initMOgZoomEventsOnce() {
    if (mOgEventsInitialized) return;
    mOgEventsInitialized = true;
    
    const container = document.getElementById('ogImageZoomContainer');
    if (!container) return;

    // 1. 마우스 휠 줌 (Mouse Wheel Zoom)
    container.addEventListener('wheel', function(e) {
        e.preventDefault();
        const delta = e.deltaY < 0 ? 0.18 : -0.18;
        zoomOriginalImage(delta);
    }, { passive: false });

    // 2. 더블클릭/더블터치 토글 (Double Click/Tap Zoom)
    let lastTapTime = 0;
    container.addEventListener('dblclick', function(e) {
        e.preventDefault();
        if (mOgScale > 1.2) {
            resetOriginalImageZoom();
        } else {
            mOgScale = 2.5;
            mOgTranslateX = 0;
            mOgTranslateY = 0;
            updateMOgImageTransform(true);
        }
    });

    // 3. 마우스 드래그 (Mouse Drag)
    container.addEventListener('mousedown', function(e) {
        if (e.button !== 0) return;
        if (mOgScale <= 1) return;
        isMOgDragging = true;
        mOgStartX = e.clientX - mOgTranslateX;
        mOgStartY = e.clientY - mOgTranslateY;
        updateMOgImageTransform(false);
    });

    window.addEventListener('mousemove', function(e) {
        if (!isMOgDragging) return;
        mOgTranslateX = e.clientX - mOgStartX;
        mOgTranslateY = e.clientY - mOgStartY;
        updateMOgImageTransform(false);
    });

    window.addEventListener('mouseup', function() {
        if (isMOgDragging) {
            isMOgDragging = false;
            updateMOgImageTransform(false);
        }
    });

    // 4. 모바일 터치 (Touch Pinch & Drag)
    container.addEventListener('touchstart', function(e) {
        if (e.touches.length === 1) {
            const currentTime = new Date().getTime();
            const tapLength = currentTime - lastTapTime;
            if (tapLength < 300 && tapLength > 0) {
                e.preventDefault();
                if (mOgScale > 1.2) {
                    resetOriginalImageZoom();
                } else {
                    mOgScale = 2.5;
                    mOgTranslateX = 0;
                    mOgTranslateY = 0;
                    updateMOgImageTransform(true);
                }
                lastTapTime = 0;
                return;
            }
            lastTapTime = currentTime;

            if (mOgScale > 1) {
                isMOgDragging = true;
                mOgStartX = e.touches[0].clientX - mOgTranslateX;
                mOgStartY = e.touches[0].clientY - mOgTranslateY;
            }
        } else if (e.touches.length === 2) {
            isMOgDragging = false;
            mOgInitialPinchDistance = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            mOgInitialScale = mOgScale;
        }
    }, { passive: false });

    container.addEventListener('touchmove', function(e) {
        if (e.touches.length === 1 && isMOgDragging && mOgScale > 1) {
            e.preventDefault();
            mOgTranslateX = e.touches[0].clientX - mOgStartX;
            mOgTranslateY = e.touches[0].clientY - mOgStartY;
            updateMOgImageTransform(false);
        } else if (e.touches.length === 2 && mOgInitialPinchDistance) {
            e.preventDefault();
            const currentDist = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            const pinchFactor = currentDist / mOgInitialPinchDistance;
            let newScale = mOgInitialScale * pinchFactor;
            if (newScale < 0.8) newScale = 0.8;
            if (newScale > 5.0) newScale = 5.0;
            mOgScale = newScale;
            updateMOgImageTransform(false);
        }
    }, { passive: false });

    container.addEventListener('touchend', function(e) {
        if (e.touches.length < 2) {
            mOgInitialPinchDistance = null;
        }
        if (e.touches.length === 0) {
            isMOgDragging = false;
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
    setTimeout(initMobileFooterCoWinnerRotation, 300);
});
