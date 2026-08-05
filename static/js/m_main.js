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

    postData.post_id = postData.post_id || postData.POST_ID || ((postData.CONTEST_ROUND || postData.contest_id) && (postData.ROUND_NO || postData.round_no) ? `${postData.CONTEST_ROUND || postData.contest_id}_${postData.ROUND_NO || postData.round_no}` : (postData.ROUND_NO || postData.round_no));
    postData.title = postData.title || postData.TITLE || '';
    postData.content = postData.content || postData.CONTS || postData.conts || '';
    window.currentMobileDetailPostId = postData.post_id;

    // 회차 마감 여부 판별
    const isClosedRound = isHallOfFame || 
                          postData.contest_stat === 'G001C002' || 
                          postData.CONTEST_STAT === 'G001C002' || 
                          postData.is_ended === true || 
                          postData.IS_ENDED === true;

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
            mPetTagEl.innerHTML = `<span style="color: #e11d48; font-weight: 800; white-space: nowrap;">${mKindNm}</span> <span style="color: #6d28d9; font-weight: 700; white-space: nowrap;">${mPetNm}</span>`;
        } else {
            mPetTagEl.innerHTML = `<span style="color: #e11d48; font-weight: 800; white-space: nowrap;">${mKindNm}</span>`;
        }
    }
    document.getElementById('mDetailScoreNum').textContent = (postData.score || 0).toLocaleString();
    document.getElementById('mDetailTitle').textContent = postData.title || '';
    document.getElementById('mDetailContent').textContent = postData.content || '';

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
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: 0.25rem 0.55rem; font-size: 0.65rem; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '슈퍼스타');">👑 슈퍼스타</div>`;
                } else if (awardCdStr.includes('P001A102') || awardNmStr.includes('라이징')) {
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: 0.25rem 0.55rem; font-size: 0.65rem; background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(203,213,225,0.9)); color: #0f172a; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '라이징스타');">🪄 라이징스타</div>`;
                } else if (awardCdStr.includes('P001A103') || awardNmStr.includes('브라이트')) {
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: 0.25rem 0.55rem; font-size: 0.65rem; background: linear-gradient(135deg, rgba(255,237,213,0.95), rgba(251,146,60,0.9)); color: #431407; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '브라이트스타');">⭐ 브라이트스타</div>`;
                } else {
                    const titleText = awRank ? `패밀리스타 ${awRank}위` : '패밀리스타';
                    rightHtml += `<div class="m-card-badge" style="position: relative; top: 0; left: 0; padding: 0.25rem 0.55rem; font-size: 0.65rem; background: linear-gradient(135deg, rgba(243,232,255,0.95), rgba(192,132,252,0.9)); color: #3b0764; cursor: pointer;" onclick="event.stopPropagation(); openBadgeZoomModal('${badgeImgSrc}', '${titleText}');"><span class="pet-emoji-icon"><i class="${petIconClass}"></i></span> ${titleText}</div>`;
                }
            });
            rightHtml += '</div>';
            mBadgeEl.innerHTML = rightHtml;
        }
    } else {
        if (mBadgeEl) {
            if (postData.rank_candidate) {
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
                    bgStyle = 'background: linear-gradient(135deg, rgba(243,232,255,0.4) 0%, rgba(192,132,252,0.38) 50%, rgba(147,51,234,0.42) 100%); color: #3b0764;';
                } else {
                    if (postData.rank_candidate === 1) {
                        iconHtml = '👑';
                        bgStyle = 'background: linear-gradient(135deg, rgba(254,240,138,0.38) 0%, rgba(245,158,11,0.42) 50%, rgba(217,119,6,0.45) 100%); color: #451a03;';
                    } else if (postData.rank_candidate === 2) {
                        iconHtml = '🪄';
                        bgStyle = 'background: linear-gradient(135deg, rgba(255,255,255,0.45) 0%, rgba(241,245,249,0.38) 60%, rgba(203,213,225,0.35) 100%); color: #0f172a;';
                    } else if (postData.rank_candidate === 3) {
                        iconHtml = '⭐';
                        bgStyle = 'background: linear-gradient(135deg, rgba(255,237,213,0.4) 0%, rgba(251,146,60,0.38) 60%, rgba(234,88,12,0.42) 100%); color: #431407;';
                    } else {
                        iconHtml = '🏆';
                        bgStyle = 'background: linear-gradient(135deg, rgba(243,232,255,0.4) 0%, rgba(192,132,252,0.38) 50%, rgba(147,51,234,0.42) 100%); color: #3b0764;';
                    }
                }
                mBadgeEl.innerHTML = `<div class="m-card-badge" style="font-size: 0.65rem; padding: 0.25rem 0.55rem; margin: 0; position: relative; top: 0; left: 0; font-weight: 800; ${bgStyle}">${iconHtml} ${rankTitle}</div>`;
            } else {
                mBadgeEl.innerHTML = '';
            }
        }
    }

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

    const mIsLiked = !!((postData.actions && postData.actions.is_liked) || postData.is_liked);
    const mBtnLikePopup = document.getElementById('mDetailBtnLike');
    const mHeartIcon = document.getElementById('mDetailHeartIcon');
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
            }
        })
        .catch(err => console.error(err));

    window.currentMobileDetailPostId = postData.post_id;
    loadMobileComments(postData.post_id);

    // 회차 종료/마감 여부 판별
    const isClosedRound = isHallOfFame || 
                          postData.contest_stat === 'G001C002' || 
                          postData.CONTEST_STAT === 'G001C002' || 
                          postData.is_ended === true || 
                          postData.IS_ENDED === true;

    const mCommentFormContainer = document.getElementById('mDetailCommentFormContainer');
    const mCommentScoreNotice = document.getElementById('mDetailCommentScoreNotice');

    const mBtnViewPopup = document.getElementById('mDetailBtnView');
    const mBtnCommentPopup = document.getElementById('mDetailBtnComment');

    if (isClosedRound) {
        if (mCommentFormContainer) mCommentFormContainer.style.display = 'none';
        if (mCommentScoreNotice) mCommentScoreNotice.style.display = 'none';
        [mBtnViewPopup, mBtnLikePopup, mBtnCommentPopup].forEach(el => {
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
        [mBtnViewPopup, mBtnLikePopup, mBtnCommentPopup].forEach(el => {
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

            const mCleanId = String(mPostId);
            const mRawEntId = mCleanId.replace(/^\d+_/, '');
            const card = document.getElementById(`m-post-card-${mCleanId}`) || 
                         document.getElementById(`m-post-card-${mRawEntId}`) ||
                         document.querySelector(`[data-post-id="${mCleanId}"]`) ||
                         document.querySelector(`[data-ent-user-id="${mRawEntId}"]`) ||
                         document.querySelector(`[data-ent-user-id="${mCleanId}"]`);

            if (card) {
                const btnCardComment = card.querySelector('.btn-comment');
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

async function copyPostShareUrl(contestRound, roundNo, shareSn) {
    let shareUrl = '';
    if (contestRound && roundNo && shareSn) {
        shareUrl = `${window.location.origin}/share?contest_round=${contestRound}&round_no=${roundNo}&share_sn=${shareSn}`;
    } else if (contestRound && roundNo) {
        try {
            const res = await fetch(`/api/contest/share_url?contest_round=${contestRound}&round_no=${roundNo}`);
            const data = await res.json();
            if (data.success && data.share_url) {
                shareUrl = data.share_url;
            }
        } catch (e) {
            console.error('copyPostShareUrl error:', e);
        }
    }

    if (!shareUrl) {
        shareUrl = window.location.href;
    }

    try {
        await navigator.clipboard.writeText(shareUrl);
        if (typeof showToast === 'function') {
            showToast('🔗 전용 공유주소가 클립보드에 복사되었습니다!\n이 주소로 접근해 회원가입 시 공유점수 +1점이 적립됩니다.');
        } else {
            alert('🔗 전용 공유주소가 복사되었습니다!');
        }
    } catch (err) {
        const tempInput = document.createElement('input');
        tempInput.value = shareUrl;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        if (typeof showToast === 'function') {
            showToast('🔗 전용 공유주소가 복사되었습니다!\n이 주소로 접근해 회원가입 시 공유점수 +1점이 적립됩니다.');
        } else {
            alert('🔗 전용 공유주소가 복사되었습니다!');
        }
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
window.handleShareClick = handleShareClick;
