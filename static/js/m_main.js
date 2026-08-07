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

    // 모바일 커스텀 회차 드롭다운 토글 및 바깥 클릭 닫기
    const mCustomContestDropdown = document.getElementById('mCustomContestDropdown');
    if (mCustomContestDropdown) {
        const trigger = mCustomContestDropdown.querySelector('.custom-contest-trigger');
        if (trigger) {
            trigger.addEventListener('click', function(e) {
                e.stopPropagation();
                mCustomContestDropdown.classList.toggle('open');
            });
        }
        document.addEventListener('click', function(e) {
            if (!mCustomContestDropdown.contains(e.target)) {
                mCustomContestDropdown.classList.remove('open');
            }
        });
    }

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
function openMobileDetailModal(postData, isHallOfFame = false) {
    if (!window.isUserLoggedIn) {
        if (typeof showToast === 'function') {
            showToast('로그인이 필요한 서비스입니다. 먼저 로그인해주세요! 🐾', 'warning');
        } else {
            alert('로그인이 필요한 서비스입니다. 먼저 로그인해주세요! 🐾');
        }
        setTimeout(() => {
            window.location.href = '/auth/google';
        }, 400);
        return;
    }

    const detailModal = document.getElementById('mDetailModal');
    if (!detailModal) return;
    detailModal.style.display = '';

    postData.post_id = postData.post_id || postData.POST_ID || ((postData.CONTEST_ROUND || postData.contest_id) && (postData.ROUND_NO || postData.round_no) ? `${postData.CONTEST_ROUND || postData.contest_id}_${postData.ROUND_NO || postData.round_no}` : (postData.ROUND_NO || postData.round_no));
    postData.title = postData.title || postData.TITLE || '';
    postData.content = postData.content || postData.CONTS || postData.conts || '';
    window.currentMobileDetailPostId = postData.post_id;

    // 회차 마감 여부 판별
    const isClosedRound = isHallOfFame || 
                          postData.contest_stat === 'G001C002' || 
                          postData.CONTEST_STAT === 'G001C002' || 
                          postData.is_closed === true || 
                          postData.closed === true || 
                          postData.is_ended === true || 
                          postData.IS_ENDED === true;

    // 종료된 회차의 경우 원형 핑크 하트 버튼 숨김
    let mHeaderLikeBtn = document.getElementById('mDetailHeaderLikeBtn');
    if (mHeaderLikeBtn) {
        if (isClosedRound) {
            mHeaderLikeBtn.style.display = 'none';
        } else {
            mHeaderLikeBtn.style.display = 'inline-flex';
        }
    }

    // 모바일 출전 포기(삭제) 버튼 제어
    const mDeleteBtn = document.getElementById('mDetailDeleteBtn');
    if (mDeleteBtn) {
        const currentUserId = String(window.CURRENT_USER_ID || '').trim();
        const postOwnerId = String(postData.ENT_USER_ID || postData.user_id || '').trim();
        if (!isClosedRound && currentUserId && postOwnerId && (currentUserId === postOwnerId || currentUserId === 'admin')) {
            mDeleteBtn.style.display = 'inline-flex';
        } else {
            mDeleteBtn.style.display = 'none';
        }
    }

    const mPopupSrc = postData.popup_image_path || postData.IMAGE_PATH || postData.image_path || postData.media_url || 
        ((postData.file_path && postData.list_file_name) ? (postData.file_path.endsWith('/') ? postData.file_path : postData.file_path + '/') + postData.list_file_name : '');
    document.getElementById('mDetailImg').src = mPopupSrc;
    document.getElementById('mDetailAuthorImg').src = postData.PROFILE_URL || postData.user_profile || '/static/image/profile/default_profile.png';
    document.getElementById('mDetailAuthorNickname').textContent = postData.NK_NM || postData.user_nickname || '집사';
    
    const mPetTagEl = document.getElementById('mDetailPetTag');
    if (mPetTagEl) {
        let mKindNm = postData.KIND_NM || postData.pet_type || '반려동물';
        if (!/[🐕🐈🐹🦜🐇🦔🦎🐠🦦🐾🐶🐱🐰]/.test(mKindNm)) {
            let icon = '🐾';
            if (mKindNm.includes('강아지') || mKindNm.includes('개')) icon = '🐕';
            else if (mKindNm.includes('고양이')) icon = '🐈';
            else if (mKindNm.includes('햄스터')) icon = '🐹';
            else if (mKindNm.includes('앵무새') || mKindNm.includes('새')) icon = '🦜';
            else if (mKindNm.includes('토끼')) icon = '🐇';
            else if (mKindNm.includes('고슴도치')) icon = '🦔';
            else if (mKindNm.includes('파충류')) icon = '🦎';
            else if (mKindNm.includes('어류') || mKindNm.includes('관상어')) icon = '🐠';
            else if (mKindNm.includes('페럿')) icon = '🦦';
            mKindNm = `${icon} ${mKindNm}`;
        }
        const mPetNm = postData.PET_NM || postData.pet_name || '';
        if (mPetNm) {
            mPetTagEl.innerHTML = `<span style="color: #e11d48; font-weight: 800; white-space: nowrap;">${mKindNm}</span><span style="color: #6d28d9; font-weight: 700; margin-left: 0.5rem; white-space: nowrap;">${mPetNm}</span>`;
        } else {
            mPetTagEl.innerHTML = `<span style="color: #e11d48; font-weight: 800; white-space: nowrap;">${mKindNm}</span>`;
        }
    }
    document.getElementById('mDetailScoreNum').textContent = (postData.score || postData.SCORE || 0).toLocaleString();
    const mTitleEl = document.getElementById('mDetailTitle');
    if (mTitleEl) mTitleEl.textContent = postData.title || postData.TITLE || '';
    
    const mContentEl = document.getElementById('mDetailContent');
    if (mContentEl) mContentEl.textContent = postData.content || postData.CONTS || '';

    const mCreatedAtEl = document.getElementById('mDetailCreatedAt');
    if (mCreatedAtEl) {
        mCreatedAtEl.textContent = postData.created_at || postData.ENT_DT || postData.dt_ago || '';
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
    if (awardsData.length === 0 && (postData.award_cd || postData.AWARD_CD)) {
        const cd = postData.award_cd || postData.AWARD_CD;
        const nm = postData.award_nm || postData.AWARD_NM || '수상 메달';
        const part = postData.award_part || postData.AWARD_PART || (cd.startsWith('P001') ? 'G002P001' : 'G002P002');
        const img = postData.badge_img || postData.badge_image_path || postData.BADGE_IMAGE_PATH || `/static/image/badge/${cd}.png`;
        const rk = postData.ranking || postData.RANKING || postData.rank || postData.rank_candidate;
        awardsData = [{ award_cd: cd, award_nm: nm, award_part: part, badge_img: img, ranking: rk }];
    }

    if (awardsData.length > 0) {
        const sortedAwards = [...awardsData].sort((a, b) => {
            const partA = a.award_part || a.AWARD_PART || '';
            const partB = b.award_part || b.AWARD_PART || '';
            return partA.localeCompare(partB);
        });

        const kindNm = postData.KIND_NM || postData.pet_type || '';
        let petIconClass = 'fa-solid fa-paw';
        if (kindNm.includes('강아지') || kindNm.includes('개')) petIconClass = 'fa-solid fa-dog';
        else if (kindNm.includes('고양이')) petIconClass = 'fa-solid fa-cat';
        else if (kindNm.includes('햄스터') || kindNm.includes('소동물') || kindNm.includes('토끼') || kindNm.includes('고슴도치')) petIconClass = 'fa-solid fa-otter';
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

                if (awardCdStr.includes('P001A101') || awardNmStr.includes('슈퍼')) displayTitle = '슈퍼스타';
                else if (awardCdStr.includes('P001A102') || awardNmStr.includes('라이징')) displayTitle = '라이징스타';
                else if (awardCdStr.includes('P001A103') || awardNmStr.includes('브라이트')) displayTitle = '브라이트스타';
                else if (awardCdStr.includes('P002A901')) displayTitle = '패밀리스타 1위';
                else if (awardCdStr.includes('P002A902')) displayTitle = '패밀리스타 2위';
                else if (awardCdStr.includes('P002A903')) displayTitle = '패밀리스타 3위';
                else if (awRank) displayTitle = `패밀리스타 ${awRank}위`;

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

                if (awardCdStr.includes('P001A101') || awardNmStr.includes('슈퍼')) {
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: 0.38rem 0.75rem; font-size: 0.82rem; font-weight: 800; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '슈퍼스타');">👑 슈퍼스타</div>`;
                } else if (awardCdStr.includes('P001A102') || awardNmStr.includes('라이징')) {
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: 0.38rem 0.75rem; font-size: 0.82rem; font-weight: 800; background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(203,213,225,0.9)); color: #0f172a; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '라이징스타');">🪄 라이징스타</div>`;
                } else if (awardCdStr.includes('P001A103') || awardNmStr.includes('브라이트')) {
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: 0.38rem 0.75rem; font-size: 0.82rem; font-weight: 800; background: linear-gradient(135deg, rgba(255,237,213,0.95), rgba(251,146,60,0.9)); color: #431407; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '브라이트스타');">⭐ 브라이트스타</div>`;
                } else {
                    const titleText = awRank ? `패밀리스타 ${awRank}위` : '패밀리스타';
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: 0.38rem 0.75rem; font-size: 0.82rem; font-weight: 800; background: linear-gradient(135deg, rgba(243,232,255,0.95), rgba(192,132,252,0.9)); color: #3b0764; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '${titleText}');"><span class="pet-emoji-icon"><i class="${petIconClass}"></i></span> ${titleText}</div>`;
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
                else if (kindNm.includes('햄스터') || kindNm.includes('소동물') || kindNm.includes('토끼') || kindNm.includes('고슴도치')) petIconClass = 'fa-solid fa-otter';
                else if (kindNm.includes('거북이') || kindNm.includes('파충류') || kindNm.includes('도마뱀')) petIconClass = 'fa-solid fa-frog';
                else if (kindNm.includes('어류') || kindNm.includes('관상어') || kindNm.includes('물고기')) petIconClass = 'fa-solid fa-fish';
                else if (kindNm.includes('앵무새') || kindNm.includes('새') || kindNm.includes('조류')) petIconClass = 'fa-solid fa-crow';
                else if (kindNm.includes('말') || kindNm.includes('큰동물')) petIconClass = 'fa-solid fa-horse';

                const urlParams = new URLSearchParams(window.location.search);
                const currentPetType = urlParams.get('pet_type') || 'all';
                const isFamily = (currentPetType && currentPetType !== 'all');
                const catPrefix = isFamily ? '패밀리스타 ' : '전체 ';
                const prefix = catPrefix + (postData.is_co_rank ? '공동 ' : '');
                const rankTitle = `${prefix}${postData.rank_candidate}위 후보`;
                let bgStyle = '';
                let iconHtml = '';

                if (isFamily) {
                    iconHtml = `<span class="pet-emoji-icon"><i class="${petIconClass}"></i></span>`;
                    bgStyle = 'background: linear-gradient(135deg, rgba(243,232,255,0.92) 0%, rgba(192,132,252,0.9) 50%, rgba(147,51,234,0.92) 100%); color: #3b0764;';
                } else {
                    iconHtml = '<i class="fa-solid fa-medal"></i>';
                    if (postData.rank_candidate === 1) {
                        bgStyle = 'background: linear-gradient(135deg, rgba(254,240,138,0.95) 0%, rgba(245,158,11,0.92) 50%, rgba(217,119,6,0.95) 100%); color: #451a03;';
                    } else if (postData.rank_candidate === 2) {
                        bgStyle = 'background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(241,245,249,0.92) 60%, rgba(203,213,225,0.9) 100%); color: #0f172a;';
                    } else if (postData.rank_candidate === 3) {
                        bgStyle = 'background: linear-gradient(135deg, rgba(255,237,213,0.95) 0%, rgba(251,146,60,0.92) 60%, rgba(234,88,12,0.95) 100%); color: #431407;';
                    } else {
                        bgStyle = 'background: linear-gradient(135deg, rgba(243,232,255,0.92) 0%, rgba(192,132,252,0.9) 50%, rgba(147,51,234,0.92) 100%); color: #3b0764;';
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

    fetch(`/api/post/user_actions/${postData.post_id}`)
        .then(res => res.json())
        .then(data => {
            if (data && data.success && data.actions) {
                const mIsLiked = !!data.actions.is_liked;
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
                const mIsCommented = !!data.actions.is_commented;
                if (btnCommentPopup) {
                    if (mIsCommented) {
                        btnCommentPopup.classList.add('active');
                        const icon = btnCommentPopup.querySelector('i');
                        if (icon) icon.className = 'fa-solid fa-comment';
                    } else {
                        btnCommentPopup.classList.remove('active');
                        const icon = btnCommentPopup.querySelector('i');
                        if (icon) icon.className = 'fa-regular fa-comment';
                    }
                }
                if (data.actions.is_shared !== undefined) {
                    const mIsShared = !!data.actions.is_shared;
                    const btnSharePopup = document.getElementById('mDetailBtnShare');
                    if (btnSharePopup) btnSharePopup.classList.toggle('active', mIsShared);
                }
                const mBtnViewPopup = document.getElementById('mDetailBtnView');
                if (mBtnViewPopup) {
                    const isViewed = !!data.actions.is_viewed || true;
                    mBtnViewPopup.classList.toggle('active', isViewed);
                    const icon = mBtnViewPopup.querySelector('i');
                    if (icon) icon.className = isViewed ? 'fa-solid fa-eye' : 'fa-regular fa-eye';
                }
            }
        })
        .catch(err => console.error(err));

    window.currentMobileDetailPostId = postData.post_id;
    loadMobileComments(postData.post_id);

    // 모바일 상세 팝업 열릴 때 자동 조회수(+1) 이벤트 트리거
    if (postData.post_id) {
        triggerMobileEvent(postData.post_id, 'view');
    }


    const mCommentFormContainer = document.getElementById('mDetailCommentFormContainer');
    const mCommentScoreNotice = document.getElementById('mDetailCommentScoreNotice');
    const mShareIconBtn = document.getElementById('mDetailShareIconBtn');

    const mBtnViewPopup = document.getElementById('mDetailBtnView');
    const mBtnCommentPopup = document.getElementById('mDetailBtnComment');
    mBtnSharePopup = mBtnSharePopup || document.getElementById('mDetailBtnShare');

    if (isClosedRound) {
        if (mCommentFormContainer) mCommentFormContainer.style.display = 'none';
        if (mCommentScoreNotice) mCommentScoreNotice.style.display = 'none';
        if (mShareIconBtn) mShareIconBtn.style.display = 'none';
        [mBtnViewPopup, mBtnLikePopup, mBtnCommentPopup, mBtnSharePopup].forEach(el => {
            if (el) {
                el.style.display = 'flex';
                el.style.pointerEvents = 'none';
                el.style.cursor = 'default';
                el.onclick = null;
            }
        });
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

        if (typeof triggerEvent === 'function') {
            triggerEvent(postData.post_id, 'view');
        }
    }

    const mCleanId = String(postData.post_id);
    const mRawEntId = mCleanId.replace(/^\d+_/, '');
    const mCard = document.getElementById(`m-post-card-${mCleanId}`) || 
                  document.getElementById(`m-post-card-${mRawEntId}`) ||
                  document.querySelector(`[data-post-id="${mCleanId}"]`) ||
                  document.querySelector(`[data-ent-user-id="${mRawEntId}"]`) ||
                  document.querySelector(`[data-ent-user-id="${mCleanId}"]`);
    if (!isClosedRound) {
        if (mCard) {
            const mBtnView = mCard.querySelector('.btn-view');
            if (mBtnView) {
                mBtnView.classList.add('active');
                const icon = mBtnView.querySelector('i');
                if (icon) icon.className = 'fa-solid fa-eye';
            }
        }
        if (mBtnViewPopup) {
            mBtnViewPopup.classList.add('active');
            const icon = mBtnViewPopup.querySelector('i');
            if (icon) icon.className = 'fa-solid fa-eye';
        }
    } else {
        if (mCard) {
            const mBtnView = mCard.querySelector('.btn-view');
            if (mBtnView) {
                mBtnView.classList.remove('active');
                const icon = mBtnView.querySelector('i');
                if (icon) icon.className = 'fa-regular fa-eye';
            }
        }
        if (mBtnViewPopup) {
            mBtnViewPopup.classList.remove('active');
            const icon = mBtnViewPopup.querySelector('i');
            if (icon) icon.className = 'fa-regular fa-eye';
        }
    }

    detailModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeMobileDetailModal() {
    const detailModal = document.getElementById('mDetailModal');
    if (detailModal) {
        detailModal.classList.remove('active', 'show');
        detailModal.style.display = '';
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
                    <div style="display: flex; align-items: center; gap: 0.3rem; font-weight: 800; color: var(--text-primary);">
                        <img src="${c.user_profile || '/static/image/profile/default_profile.png'}" style="width: 16px; height: 16px; border-radius: 50%; object-fit: cover;">
                        <span>${escapeHtml(c.user_nickname || '집사')}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.4rem;">
                        <span style="font-size: 0.68rem; color: var(--text-muted);">${c.created_at || ''}</span>
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
        showMobileToast('댓글 삭제 중 오류가 발생했습니다.', 'error');
    });
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

    let shareUrl = '';
    if (contestRound && roundNo) {
        try {
            const res = await fetch(`/api/contest/share_url?contest_round=${contestRound}&round_no=${roundNo}`);
            const data = await res.json();
            if (data.success && data.share_url) {
                shareUrl = data.share_url;
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

    // 서버 DB 공유 수(+1) 및 점수 증가 이벤트 자동 트리거
    if (postId) {
        try {
            await triggerMobileEvent(postId, 'share');
        } catch (e) {
            console.error('triggerMobileEvent share error:', e);
        }
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
        try {
            await navigator.clipboard.writeText(shareUrl);
            if (typeof showToast === 'function') {
                showToast('🔗 전용 공유주소가 복사되었습니다!\n이 주소로 접근해 회원가입이나 로그인 시 공유점수 +10점이 적립됩니다.');
            } else {
                alert(`🔗 전용 공유주소가 복사되었습니다!\n${shareUrl}`);
            }
        } catch (err) {
            const tempInput = document.createElement('input');
            tempInput.value = shareUrl;
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand('copy');
            document.body.removeChild(tempInput);
            if (typeof showToast === 'function') {
                showToast('🔗 전용 공유주소가 복사되었습니다!\n이 주소로 접근해 회원가입이나 로그인 시 공유점수 +10점이 적립됩니다.');
            } else {
                alert(`🔗 전용 공유주소가 복사되었습니다!\n${shareUrl}`);
            }
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
        if (window.postsDataStore && window.postsDataStore[openPostId]) {
            openMobileDetailModal(window.postsDataStore[openPostId]);
        } else {
            fetch(`/api/post/detail/${openPostId}`)
                .then(res => res.json())
                .then(data => {
                    if (data.success && data.post) {
                        openMobileDetailModal(data.post);
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

    const feedGrid = document.querySelector('.m-feed-grid');
    if (feedGrid) {
        feedGrid.style.opacity = '0.45';
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
        const pKindClean = pKindRaw.replace(/[🐕🐈🐹🦜🐾]/g, '').trim();
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
        else if (pKindRaw.includes('햄스터') || pKindRaw.includes('소동물') || pKindRaw.includes('토끼')) chipIcon = 'fa-solid fa-otter';
        else if (pKindRaw.includes('새') || pKindRaw.includes('앵무새') || pKindRaw.includes('조류')) chipIcon = 'fa-solid fa-crow';
        else if (pKindRaw.includes('말') || pKindRaw.includes('큰동물')) chipIcon = 'fa-solid fa-horse';
        else if (pKindRaw.includes('어류') || pKindRaw.includes('관상어')) chipIcon = 'fa-solid fa-fish';

        let badgeHtml = '';
        if (p.awards && p.awards.length > 0) {
            let awardsHtml = '';
            p.awards.forEach(aw => {
                const awardCdStr = String(aw.award_cd || aw.AWARD_CD || '');
                const awardNmStr = String(aw.award_nm || aw.AWARD_NM || '');
                const awRank = aw.ranking || aw.RANKING;
                let badgeText = '수상작';
                let bgStyle = 'background: linear-gradient(135deg, rgba(243,232,255,0.95), rgba(192,132,252,0.9)); color: #3b0764;';
                if (awardCdStr.includes('P001A101') || awardNmStr.includes('슈퍼')) {
                    badgeText = '슈퍼스타';
                    bgStyle = '';
                } else if (awardCdStr.includes('P001A102') || awardNmStr.includes('라이징')) {
                    badgeText = '라이징스타';
                    bgStyle = 'background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(203,213,225,0.9)); color: #0f172a;';
                } else if (awardCdStr.includes('P001A103') || awardNmStr.includes('브라이트')) {
                    badgeText = '브라이트스타';
                    bgStyle = 'background: linear-gradient(135deg, rgba(255,237,213,0.95), rgba(251,146,60,0.9)); color: #431407;';
                } else {
                    badgeText = `패밀리스타${awRank ? ` ${awRank}위` : ''}`;
                }
                awardsHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: 0.15rem 0.42rem; font-size: 0.56rem; ${bgStyle}">${badgeText}</div>`;
            });
            badgeHtml = `<div style="position: absolute; top: 0.4rem; right: 0.4rem; display: flex; flex-direction: row; align-items: center; justify-content: flex-end; gap: 0.35rem; z-index: 10; pointer-events: none;">${awardsHtml}</div>`;
        } else {
            const isPostClosed = p.is_closed || p.closed || p.contest_stat === 'G001C002' || p.CONTEST_STAT === 'G001C002' || p.STATUS_CD === 'G001C002' || p.is_ended || p.IS_ENDED;
            const rkCand = p.rank_candidate || p.RANK_CANDIDATE || p.rank || p.ranking;
            const isCo = p.is_co_rank || p.IS_CO_RANK;
            if (rkCand && !isPostClosed) {
                const urlParams = new URLSearchParams(window.location.search);
                const currentPetType = urlParams.get('pet_type') || 'all';
                const isFamily = (currentPetType && currentPetType !== 'all');
                const catPrefix = isFamily ? '패밀리스타 ' : '전체 ';
                const prefix = catPrefix + (isCo ? '공동 ' : '');
                const rankTitle = `${prefix}${rkCand}위 후보`;
                
                let bgStyle = '';
                if (isFamily) {
                    bgStyle = 'background: linear-gradient(135deg, rgba(243,232,255,0.95), rgba(192,132,252,0.9)); color: #3b0764;';
                } else {
                    const rkNum = Number(rkCand);
                    if (rkNum === 1) {
                        bgStyle = 'background: linear-gradient(135deg, rgba(248,250,252,0.95), rgba(245,158,11,0.92)); color: #451a03;';
                    } else if (rkNum === 2) {
                        bgStyle = 'background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(203,213,225,0.9)); color: #0f172a;';
                    } else if (rkNum === 3) {
                        bgStyle = 'background: linear-gradient(135deg, rgba(255,237,213,0.95), rgba(251,146,60,0.9)); color: #431407;';
                    }
                }
                badgeHtml = `<div class="m-card-badge" style="font-size: 0.56rem; padding: 0.15rem 0.42rem; top: 0.4rem; left: 0.4rem; position: absolute; z-index: 10; ${bgStyle}">${rankTitle}</div>`;
            }
        }

        html += `
        <div class="m-feed-card" id="m-post-card-${entUserId || postId}" data-post-id="${postId}" data-ent-user-id="${entUserId}" onclick="openMobileDetailModal(${pPostJsonData})">
            <div class="m-card-thumb">
                <img src="${pImg}" alt="${pTitle}" loading="lazy">
                ${badgeHtml}
            </div>

            <div class="m-card-body">
                <!-- 1줄째: 프로필사진 + 작성자 닉네임 -->
                <div class="m-card-author">
                    <img src="${pAvatar}" alt="${pUserNm}" class="m-author-avatar">
                    <span class="m-author-name">${pUserNm}</span>
                </div>

                <!-- 2줄째: 동물아이콘 + 동물유형명 + 동물 닉네임 -->
                <div class="m-pet-tag">
                    <span class="m-pet-kind-text">${pKindRaw}</span>
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
                    <div class="m-btn-action btn-view ${p.actions && p.actions.is_viewed ? 'active' : ''}" title="조회수">
                        <i class="fa-${p.actions && p.actions.is_viewed ? 'solid' : 'regular'} fa-eye"></i> <span class="view-count">${pViewCount.toLocaleString()}</span>
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
    document.querySelectorAll('.custom-contest-option').forEach(opt => opt.classList.remove('selected'));
    if (el) el.classList.add('selected');

    const dropdown = document.getElementById('mCustomContestDropdown');
    if (dropdown) dropdown.classList.remove('open');

    const mCurrentContestId = document.getElementById('mCurrentContestId');
    if (mCurrentContestId) mCurrentContestId.value = contestId;

    fetchMobilePostsAjax({ contest_id: contestId });
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

async function triggerMobileEvent(postId, eventType) {
    if (!window.isUserLoggedIn) {
        if (typeof showToast === 'function') {
            showToast('로그인이 필요한 서비스입니다. 먼저 로그인해주세요! 🐾', 'warning');
        } else {
            alert('로그인이 필요한 서비스입니다. 먼저 로그인해주세요! 🐾');
        }
        return;
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

            const mLikeEl = document.getElementById('mDetailLikeCount');
            if (mLikeEl && finalLike !== undefined) mLikeEl.textContent = Number(finalLike).toLocaleString();

            const mViewEl = document.getElementById('mDetailViewCount');
            if (mViewEl && finalView !== undefined) mViewEl.textContent = Number(finalView).toLocaleString();

            const mCommentEl = document.getElementById('mDetailCommentCount');
            if (mCommentEl && finalComment !== undefined) mCommentEl.textContent = Number(finalComment).toLocaleString();

            const mShareEl = document.getElementById('mDetailShareCount');
            if (mShareEl && finalShare !== undefined) mShareEl.textContent = Number(finalShare).toLocaleString();

            if (eventType === 'share') {
                const mBtnSharePopup = document.getElementById('mDetailBtnShare');
                if (mBtnSharePopup) mBtnSharePopup.classList.add('active');
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
            if (typeof showToast === 'function') showToast(data.message || resData.message || '요청 처리 실패', 'warning');
        }
    } catch (err) {
        console.error('triggerMobileEvent error:', err);
    }
}
window.triggerMobileEvent = triggerMobileEvent;
