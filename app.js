// ==========================================================================
// Rathcharot & ChangPhapNganSop Presentation Controller
// Canva-Style Auto-Scaling Engine & Slide Navigation
// ==========================================================================

const COVER_HERO_STORAGE_KEY = 'rathcharot_cover_heroes_v3';
const ADMIN_SESSION_TOKEN_KEY = 'rathcharot_admin_token';
const ADMIN_CARD_EDITS_KEY = 'rathcharot_card_edits_v3';
const ADMIN_DELETED_KEY = 'rathcharot_deleted_photos_v3';
const ADMIN_CUSTOM_UPLOADS_KEY = 'rathcharot_custom_uploads_v3';
const DEFAULT_COVER_HEROES = {};
const DEFAULT_CARD_TEXTS = {};

let currentSlideIndex = 0;
let slides = [];
let lightboxCurrentImages = [];
let lightboxCurrentIndex = 0;
let lightboxCurrentCatId = '';

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

function initApp() {
  slides = Array.from(document.querySelectorAll('.slide'));
  captureDefaultCoverHeroes();
  captureDefaultCardTexts();
  syncAdminSessionClass();
  
  // Support direct slide linking via ?slide=X or #slide=X
  const params = new URLSearchParams(window.location.search);
  const slideParam = params.get('slide');
  const hashMatch = window.location.hash.match(/slide[=-]?(\d+)/i);
  let initialSlide = 0;
  if (slideParam !== null) {
    initialSlide = parseInt(slideParam, 10);
  } else if (hashMatch) {
    initialSlide = parseInt(hashMatch[1], 10);
  }
  updateSlideView(isNaN(initialSlide) ? 0 : Math.max(0, Math.min(initialSlide, slides.length - 1)));
  
  setupEventListeners();
  setupKeyboardNav();
  setupTouchNav();
  initThumbnailStrips();
  initCoverMenuHub();
  initAdminControls();
  applySavedAdminData();
  buildGalleryModal();
  refreshAllCategoryCounters();
  
  // Canva-style Auto-scaling on load & resize
  fitStageToScreen();
  window.addEventListener('resize', fitStageToScreen);
  window.addEventListener('orientationchange', () => {
    setTimeout(fitStageToScreen, 150);
  });
}

// --------------------------------------------------------------------------
// Canva-Style Fixed Aspect Ratio Auto-Scaling Engine (with Mobile Native Mode)
// --------------------------------------------------------------------------
function fitStageToScreen() {
  const stage = document.querySelector('.presentation-stage');
  const container = document.querySelector('.viewport-container');
  if (!stage || !container) return;

  // In continuous catalog scroll mode, disable fixed scale and let it flow
  if (document.body.classList.contains('catalog-mode')) {
    stage.style.transform = 'none';
    stage.style.width = '100%';
    stage.style.maxWidth = '1200px';
    stage.style.height = 'auto';
    return;
  }

  // Mobile check: Align breakpoint with CSS @media (max-width: 1100px), (orientation: portrait)
  const isMobile = window.innerWidth <= 1100 || window.matchMedia('(orientation: portrait)').matches;
  if (isMobile) {
    document.body.classList.add('mobile-layout');
    stage.style.transform = 'none';
    stage.style.width = '100%';
    stage.style.height = '100%';
    stage.style.maxWidth = '100%';
    return;
  } else {
    document.body.classList.remove('mobile-layout');
  }

  // Base canvas dimension (16:9 ratio) for Desktop Widescreen
  const baseWidth = 1440;
  const baseHeight = 810;

  // Available container space (excluding container padding)
  const availableWidth = container.clientWidth - 16;
  const availableHeight = container.clientHeight - 16;

  if (availableWidth <= 0 || availableHeight <= 0) return;

  // Compute exact uniform scale factor to contain the entire slide
  const scale = Math.min(availableWidth / baseWidth, availableHeight / baseHeight);

  stage.style.width = `${baseWidth}px`;
  stage.style.height = `${baseHeight}px`;
  stage.style.transform = `scale(${scale})`;
  stage.style.transformOrigin = 'center center';
}

// --------------------------------------------------------------------------
// Slide Navigation
// --------------------------------------------------------------------------
function updateSlideView(index, options = {}) {
  if (index < 0) index = 0;
  if (index >= slides.length) index = slides.length - 1;
  currentSlideIndex = index;

  slides.forEach((slide, idx) => {
    slide.classList.toggle('active', idx === currentSlideIndex);
  });

  // Update header nav pills
  document.querySelectorAll('.nav-pill').forEach(pill => {
    const targetIdx = parseInt(pill.dataset.slide, 10);
    pill.classList.toggle('active', targetIdx === currentSlideIndex);
  });

  // Update mobile drawer nav items
  document.querySelectorAll('.drawer-nav-item').forEach(item => {
    const targetIdx = parseInt(item.dataset.slide, 10);
    item.classList.toggle('active', targetIdx === currentSlideIndex);
  });

  // Update counter
  const counterEl = document.getElementById('slideCounter');
  if (counterEl) {
    const currentNum = String(currentSlideIndex + 1).padStart(2, '0');
    const totalNum = String(slides.length).padStart(2, '0');
    counterEl.textContent = `${currentNum} / ${totalNum}`;
  }

  // Scroll active nav pill into view cleanly within the nav container
  const activePill = document.querySelector('.nav-pill.active');
  const navContainer = document.querySelector('.header-center-nav');
  if (activePill && navContainer) {
    const pillLeft = activePill.offsetLeft;
    const pillWidth = activePill.offsetWidth;
    const containerWidth = navContainer.clientWidth;
    navContainer.scrollTo({
      left: pillLeft - (containerWidth / 2) + (pillWidth / 2),
      behavior: 'smooth'
    });
  }

  // If in catalog scroll mode, scroll to the target slide
  if (document.body.classList.contains('catalog-mode')) {
    slides[currentSlideIndex].scrollIntoView({ behavior: 'smooth', block: 'start' });
  } else {
    // Re-verify scale fitting
    fitStageToScreen();
  }

  if (options && options.autoExpand) {
    openSlideLightbox(currentSlideIndex);
  }
}

function openSlideLightbox(slideIndex) {
  const slide = slides[slideIndex];
  if (!slide || slideIndex === 0) {
    closeLightbox();
    return;
  }
  const catId = slide.dataset.categoryId;
  const catData = catId ? CATALOG_CATEGORIES.find(c => c.id === catId) : null;
  if (catData && Array.isArray(catData.images) && catData.images.length > 0) {
    const orderedImages = getOrderedImagesForCategory(catId, slide);
    lightboxCurrentCatId = catId;
    openLightbox(orderedImages, 0, catData.title, catId);
  } else {
    closeLightbox();
  }
}

function nextSlide() {
  if (currentSlideIndex < slides.length - 1) {
    updateSlideView(currentSlideIndex + 1);
  }
}

function prevSlide() {
  if (currentSlideIndex > 0) {
    updateSlideView(currentSlideIndex - 1);
  }
}

// --------------------------------------------------------------------------
// Keyboard & Touch
// --------------------------------------------------------------------------
function setupKeyboardNav() {
  window.addEventListener('keydown', (e) => {
    const adminLoginModal = document.getElementById('adminLoginModal');
    const adminUploadModal = document.getElementById('adminUploadModal');
    const adminEditModal = document.getElementById('adminEditModal');
    const coverPickerModal = document.getElementById('coverPickerModal');
    const lightboxModal = document.getElementById('lightboxModal');
    const galleryModal = document.getElementById('galleryModal');
    const qrModal = document.getElementById('qrModal');

    if (adminLoginModal && adminLoginModal.classList.contains('active')) {
      if (e.key === 'Escape') closeAdminLoginModal();
      return;
    }

    if (adminUploadModal && adminUploadModal.classList.contains('active')) {
      if (e.key === 'Escape') closeAdminUploadModal();
      return;
    }

    if (adminEditModal && adminEditModal.classList.contains('active')) {
      if (e.key === 'Escape') closeAdminEditModal();
      return;
    }

    if (coverPickerModal && coverPickerModal.classList.contains('active')) {
      if (e.key === 'Escape') closeCoverPickerModal();
      return;
    }

    // If Lightbox is open
    if (lightboxModal && lightboxModal.classList.contains('active')) {
      if (e.key === 'Escape') closeLightbox();
      if (e.key === 'ArrowRight') nextLightboxImage();
      if (e.key === 'ArrowLeft') prevLightboxImage();
      return;
    }

    // If Gallery Modal is open
    if (galleryModal && galleryModal.classList.contains('active')) {
      if (e.key === 'Escape') closeGalleryModal();
      return;
    }

    // If QR Modal is open
    if (qrModal && qrModal.classList.contains('active')) {
      if (e.key === 'Escape') closeQrModal();
      return;
    }

    // Normal slide navigation
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
      e.preventDefault();
      nextSlide();
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      e.preventDefault();
      prevSlide();
    } else if (e.key === 'Home') {
      e.preventDefault();
      updateSlideView(0);
    } else if (e.key === 'End') {
      e.preventDefault();
      updateSlideView(slides.length - 1);
    } else if (e.key.toLowerCase() === 'f') {
      toggleFullscreen();
    }
  });
}

function setupTouchNav() {
  // Main viewport touch navigation
  let touchStartX = 0;
  let touchEndX = 0;
  let touchStartY = 0;
  let touchEndY = 0;

  const targetArea = document.querySelector('.viewport-container') || document.body;
  if (targetArea) {
    targetArea.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    targetArea.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      touchEndY = e.changedTouches[0].screenY;
      const diffX = touchEndX - touchStartX;
      const diffY = touchEndY - touchStartY;
      if (Math.abs(diffX) > 45 && Math.abs(diffX) > Math.abs(diffY)) {
        const lightboxModal = document.getElementById('lightboxModal');
        if (lightboxModal && lightboxModal.classList.contains('active')) {
          return; // Lightbox has its own dedicated touch engine below
        }
        if (diffX < 0) nextSlide();
        else prevSlide();
      }
    }, { passive: true });
  }

  // Dedicated High-Performance Lightbox Touch & Swipe Engine
  const lbModal = document.getElementById('lightboxModal');
  if (lbModal) {
    let lbTouchStartX = 0;
    let lbTouchStartY = 0;
    let lbStartTime = 0;
    let lbIsSwiping = false;

    lbModal.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        lbTouchStartX = e.touches[0].clientX;
        lbTouchStartY = e.touches[0].clientY;
        lbStartTime = Date.now();
        lbIsSwiping = false;
      }
    }, { passive: true });

    lbModal.addEventListener('touchmove', (e) => {
      if (e.touches.length === 1) {
        const dx = e.touches[0].clientX - lbTouchStartX;
        const dy = e.touches[0].clientY - lbTouchStartY;
        if (Math.abs(dx) > 12 && Math.abs(dx) > Math.abs(dy)) {
          lbIsSwiping = true;
        }
      }
    }, { passive: true });

    lbModal.addEventListener('touchend', (e) => {
      const endX = e.changedTouches[0].clientX;
      const endY = e.changedTouches[0].clientY;
      const diffX = endX - lbTouchStartX;
      const diffY = endY - lbTouchStartY;
      const dt = Date.now() - lbStartTime;

      // Horizontal swipe: threshold 35px or quick flick
      if (Math.abs(diffX) > 35 && Math.abs(diffX) > Math.abs(diffY)) {
        if (diffX < 0) {
          nextLightboxImage();
        } else {
          prevLightboxImage();
        }
        return;
      }

      // Deliberate downward swipe to close (> 90px downwards in < 400ms)
      if (diffY > 90 && Math.abs(diffY) > Math.abs(diffX) * 1.5 && dt < 400) {
        closeLightbox();
      }
    }, { passive: true });
  }
}

// --------------------------------------------------------------------------
// Event Listeners for UI Controls
// --------------------------------------------------------------------------
function setupEventListeners() {
  // Navigation buttons
  document.getElementById('btnNext')?.addEventListener('click', nextSlide);
  document.getElementById('btnPrev')?.addEventListener('click', prevSlide);
  document.getElementById('btnFirst')?.addEventListener('click', () => updateSlideView(0));
  document.getElementById('btnLast')?.addEventListener('click', () => updateSlideView(slides.length - 1));

  // Nav pills in header
  document.querySelectorAll('.nav-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      const idx = parseInt(pill.dataset.slide, 10);
      updateSlideView(idx, { autoExpand: true });
    });
  });

  // Brand click -> Slide 0
  document.querySelector('.brand-badge')?.addEventListener('click', () => {
    closeLightbox();
    updateSlideView(0);
  });

  // Fullscreen button
  document.getElementById('btnFullscreen')?.addEventListener('click', toggleFullscreen);

  // View Mode button (Presentation vs Catalog Scroll)
  document.getElementById('btnViewMode')?.addEventListener('click', toggleViewMode);

  // Gallery button in header
  document.getElementById('btnOpenGallery')?.addEventListener('click', () => openGalleryModal());

  // Print button
  document.getElementById('btnPrint')?.addEventListener('click', () => window.print());

  // QR Modal buttons
  document.getElementById('btnOpenQr')?.addEventListener('click', () => openQrModal('ช่างภาพงานศพ.com'));

  // Mobile Drawer Menu
  const btnHamburger = document.getElementById('btnHamburger');
  const btnDrawerClose = document.getElementById('btnDrawerClose');
  const drawerOverlay = document.getElementById('mobileDrawerOverlay');
  const drawer = document.getElementById('mobileDrawer');

  function openDrawer() {
    drawerOverlay?.classList.add('active');
    drawer?.classList.add('active');
  }

  function closeDrawer() {
    drawerOverlay?.classList.remove('active');
    drawer?.classList.remove('active');
  }

  btnHamburger?.addEventListener('click', openDrawer);
  btnDrawerClose?.addEventListener('click', closeDrawer);
  drawerOverlay?.addEventListener('click', (e) => {
    if (e.target === drawerOverlay) closeDrawer();
  });

  // Drawer slide items
  document.querySelectorAll('.drawer-nav-item').forEach(item => {
    item.addEventListener('click', () => {
      const idx = parseInt(item.dataset.slide, 10);
      closeDrawer();
      updateSlideView(idx, { autoExpand: true });
    });
  });

  // Drawer quick actions
  document.getElementById('btnDrawerGallery')?.addEventListener('click', () => {
    closeDrawer();
    openGalleryModal('all');
  });

  document.getElementById('btnDrawerQr')?.addEventListener('click', () => {
    closeDrawer();
    openQrModal('ช่างภาพงานศพ.com');
  });
}

// --------------------------------------------------------------------------
// In-Slide Thumbnail Switching & Hero Zoom
// --------------------------------------------------------------------------
function initThumbnailStrips() {
  document.querySelectorAll('.slide').forEach(slide => {
    const heroImg = slide.querySelector('.hero-img');
    const heroFrame = slide.querySelector('.hero-image-frame');
    const thumbItems = slide.querySelectorAll('.slide-thumb-item');
    const catId = slide.dataset.categoryId;

    if (!heroImg || thumbItems.length === 0) return;

    const catData = CATALOG_CATEGORIES.find(c => c.id === catId);

    thumbItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.stopPropagation();
        const targetSrc = item.dataset.src;
        const targetFilename = item.dataset.filename;

        // Animate hero change
        heroImg.style.opacity = '0.3';
        setTimeout(() => {
          heroImg.src = targetSrc;
          heroImg.alt = targetFilename || '';
          heroImg.style.opacity = '1';
        }, 150);

        thumbItems.forEach(t => t.classList.remove('active'));
        item.classList.add('active');
      });
    });

    // Clicking hero frame opens Lightbox for this category
    heroFrame?.addEventListener('click', () => {
      if (catData) {
        const activeSrc = heroImg.getAttribute('src');
        const activeIdx = catData.images.findIndex(
          img => img.encoded_path === activeSrc || img.rel_path === activeSrc || (activeSrc && activeSrc.endsWith('/' + img.filename))
        );
        openLightbox(catData.images, activeIdx >= 0 ? activeIdx : 0, catData.title, catId);
      }
    });

    // "View All In Category" button
    const btnAll = slide.querySelector('.btn-open-folder-gallery');
    btnAll?.addEventListener('click', () => {
      openGalleryModal(catId);
    });
  });
}

// --------------------------------------------------------------------------
// Fullscreen & View Mode
// --------------------------------------------------------------------------
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {});
  } else {
    document.exitFullscreen().catch(() => {});
  }
}

function toggleViewMode() {
  const isCatalog = document.body.classList.toggle('catalog-mode');
  const btn = document.getElementById('btnViewMode');
  if (btn) {
    btn.innerHTML = isCatalog 
      ? '📽️ <span>โหมดสไลด์</span>' 
      : '📜 <span>โหมดเลื่อนอ่าน</span>';
  }
  fitStageToScreen();
  if (!isCatalog) {
    updateSlideView(currentSlideIndex);
  }
}

// --------------------------------------------------------------------------
// Lightbox Modal
// --------------------------------------------------------------------------
let lightboxLastSwitchTime = 0;
const LIGHTBOX_THROTTLE_MS = 60; // 60ms throttle protects against double-tap jitter while preserving 60fps response

function preloadLightboxNeighbors() {
  if (!lightboxCurrentImages || lightboxCurrentImages.length === 0) return;
  const len = lightboxCurrentImages.length;
  // Preload next 3 images and previous 2 images into browser cache memory
  const offsets = [1, 2, 3, -1, -2];
  offsets.forEach(offset => {
    const idx = (lightboxCurrentIndex + offset + len) % len;
    const item = lightboxCurrentImages[idx];
    if (item) {
      const src = item.encoded_path || item.rel_path;
      if (src) {
        const pre = new Image();
        pre.src = src;
      }
    }
  });
}

function renderLightboxFrame() {
  if (!lightboxCurrentImages || lightboxCurrentImages.length === 0) return;
  const cur = lightboxCurrentImages[lightboxCurrentIndex];
  const img = document.getElementById('lightboxImg');
  const caption = document.getElementById('lightboxCaption');
  const label = `${lightboxCurrentIndex + 1}/${lightboxCurrentImages.length}`;
  if (img && cur) {
    const nextSrc = cur.encoded_path || cur.rel_path;
    if (img.getAttribute('src') !== nextSrc) {
      img.style.opacity = '0.88';
      img.src = nextSrc;
      img.alt = label;
      requestAnimationFrame(() => {
        img.style.opacity = '1';
      });
    }
  }
  if (caption) {
    caption.textContent = label;
  }
  preloadLightboxNeighbors();
}

function openLightbox(imagesList, startIndex = 0, _title = '', catId = '') {
  if (!Array.isArray(imagesList) || imagesList.length === 0) return;
  lightboxCurrentImages = imagesList;
  lightboxCurrentIndex = startIndex;
  lightboxCurrentCatId = catId || imagesList[startIndex]?.catId || '';

  const modal = document.getElementById('lightboxModal');
  const img = document.getElementById('lightboxImg');
  if (!modal || !img) return;

  renderLightboxFrame();
  modal.classList.add('active');
  preloadLightboxNeighbors();
}

function closeLightbox() {
  document.getElementById('lightboxModal')?.classList.remove('active');
}

function nextLightboxImage() {
  if (!lightboxCurrentImages || lightboxCurrentImages.length === 0) return;
  const now = Date.now();
  if (now - lightboxLastSwitchTime < LIGHTBOX_THROTTLE_MS) return;
  lightboxLastSwitchTime = now;

  lightboxCurrentIndex = (lightboxCurrentIndex + 1) % lightboxCurrentImages.length;
  renderLightboxFrame();
}

function prevLightboxImage() {
  if (!lightboxCurrentImages || lightboxCurrentImages.length === 0) return;
  const now = Date.now();
  if (now - lightboxLastSwitchTime < LIGHTBOX_THROTTLE_MS) return;
  lightboxLastSwitchTime = now;

  lightboxCurrentIndex = (lightboxCurrentIndex - 1 + lightboxCurrentImages.length) % lightboxCurrentImages.length;
  renderLightboxFrame();
}

// --------------------------------------------------------------------------
// Full Photo Gallery Modal (Organized by Folder & Crash-Proof Chunked Engine)
// --------------------------------------------------------------------------
let currentGalleryCat = 'all';
let currentGalleryPage = 1;
const GALLERY_PAGE_SIZE = 16; // 16 images per chunk protects iOS/Mobile WebKit from Jetsam OOM crashes!

function buildGalleryModal() {
  const tabsContainer = document.getElementById('galleryTabs');
  if (!tabsContainer) return;

  let tabsHtml = `<button class="gallery-tab-btn active" data-cat="all">ทั้งหมด (${CATALOG_CATEGORIES.reduce((acc, c) => acc + c.images.length, 0)} ภาพ)</button>`;
  CATALOG_CATEGORIES.forEach(cat => {
    tabsHtml += `<button class="gallery-tab-btn" data-cat="${cat.id}">${cat.title} (${cat.images.length})</button>`;
  });
  tabsContainer.innerHTML = tabsHtml;

  tabsContainer.querySelectorAll('.gallery-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      tabsContainer.querySelectorAll('.gallery-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderGalleryGrid(btn.dataset.cat, false);
    });
  });

  // Note: We deliberately DO NOT render images into the DOM on page load!
  // This keeps initial page weight feather-light on mobile and prevents memory bloat.
}

function renderGalleryGrid(selectedCatId, isAppend = false) {
  const gridContainer = document.getElementById('galleryGrid');
  if (!gridContainer) return;

  if (!isAppend) {
    currentGalleryCat = selectedCatId;
    currentGalleryPage = 1;
    gridContainer.innerHTML = '';
  }

  let allImagesForCat = [];
  if (selectedCatId === 'all') {
    CATALOG_CATEGORIES.forEach(cat => {
      cat.images.forEach(img => {
        allImagesForCat.push({ ...img, catTitle: cat.title, catId: cat.id });
      });
    });
  } else {
    const cat = CATALOG_CATEGORIES.find(c => c.id === selectedCatId);
    if (cat) {
      allImagesForCat = cat.images.map(img => ({ ...img, catTitle: cat.title, catId: cat.id }));
    }
  }

  // Remove existing Load More button if present
  const existingLoadMore = document.getElementById('btnGalleryLoadMoreWrap');
  if (existingLoadMore) existingLoadMore.remove();

  const total = allImagesForCat.length;
  const startIndex = isAppend ? (currentGalleryPage - 1) * GALLERY_PAGE_SIZE : 0;
  const endIndex = Math.min(total, currentGalleryPage * GALLERY_PAGE_SIZE);

  const newCards = allImagesForCat.slice(startIndex, endIndex);

  newCards.forEach((img, idxOffset) => {
    const globalIdx = startIndex + idxOffset;
    const card = document.createElement('div');
    card.className = 'gallery-card';
    card.dataset.idx = globalIdx;
    card.title = img.filename;
    card.innerHTML = `
      <img src="${img.encoded_path}" alt="${img.filename}" loading="lazy" decoding="async" />
      <div class="gallery-card-admin-bar admin-only">
        <button type="button" class="gallery-admin-btn" data-action="set-hero" title="ตั้งเป็นภาพหลักของหมวด">⭐ ภาพหลัก</button>
        <button type="button" class="gallery-admin-btn danger" data-action="delete" title="ลบภาพนี้">🗑️ ลบ</button>
      </div>
      <span class="gallery-card-zoom-icon">🔍</span>
      <div class="gallery-card-badge">${img.catTitle || ''} • ภาพที่ ${globalIdx + 1}</div>
    `;
    const btnSetHero = card.querySelector('[data-action="set-hero"]');
    btnSetHero?.addEventListener('click', (e) => {
      e.stopPropagation();
      const targetSlideIdx = getSlideIndexByCategoryId(img.catId);
      selectCoverHeroImage(img.catId, targetSlideIdx, img.encoded_path);
      renderGalleryGrid(currentGalleryCat, false);
    });
    const btnDel = card.querySelector('[data-action="delete"]');
    btnDel?.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteCatalogPhoto(img.catId, img.filename, img.rel_path, img.encoded_path);
    });
    card.addEventListener('click', () => {
      openLightbox(allImagesForCat, globalIdx, allImagesForCat[globalIdx]?.catTitle || 'คลังภาพผลงาน', img.catId);
    });
    gridContainer.appendChild(card);
  });

  // If more photos remain in this category, show luxury "Load More" button
  if (endIndex < total) {
    const remaining = total - endIndex;
    const loadMoreWrap = document.createElement('div');
    loadMoreWrap.id = 'btnGalleryLoadMoreWrap';
    loadMoreWrap.style.cssText = 'grid-column: 1 / -1; text-align: center; padding: 24px 0 32px 0;';
    loadMoreWrap.innerHTML = `
      <button class="btn-icon btn-icon-gold" id="btnGalleryLoadMore" style="padding: 12px 28px; font-size: 0.95rem; margin: 0 auto; box-shadow: 0 6px 20px rgba(0,0,0,0.8); cursor: pointer;">
        📥 โหลดภาพเพิ่มเติม (แสดงแล้ว ${endIndex}/${total} ภาพ • เหลืออีก ${remaining} ภาพ)
      </button>
    `;
    gridContainer.appendChild(loadMoreWrap);

    document.getElementById('btnGalleryLoadMore')?.addEventListener('click', () => {
      currentGalleryPage++;
      renderGalleryGrid(selectedCatId, true);
    });
  }
}

function openGalleryModal(catId = 'all') {
  const modal = document.getElementById('galleryModal');
  if (!modal) return;
  modal.classList.add('active');

  const tabs = document.querySelectorAll('.gallery-tab-btn');
  tabs.forEach(tab => {
    const isTarget = tab.dataset.cat === catId;
    tab.classList.toggle('active', isTarget);
    if (isTarget) {
      tab.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    }
  });

  renderGalleryGrid(catId, false);
}

function closeGalleryModal() {
  const modal = document.getElementById('galleryModal');
  if (!modal) return;
  modal.classList.remove('active');

  // Immediately release heavy images from memory to free mobile WebKit RAM!
  setTimeout(() => {
    const gridContainer = document.getElementById('galleryGrid');
    if (gridContainer && !modal.classList.contains('active')) {
      gridContainer.innerHTML = '';
    }
  }, 350);
}

// --------------------------------------------------------------------------
// QR Code Quick Scan Modal
// --------------------------------------------------------------------------
function openQrModal(focusSite = 'ช่างภาพงานศพ.com') {
  const modal = document.getElementById('qrModal');
  if (!modal) return;
  modal.classList.add('active');
}

function closeQrModal() {
  document.getElementById('qrModal')?.classList.remove('active');
}

// --------------------------------------------------------------------------
// Home Menu Hub Visual Cards & Cover Image Selector
// --------------------------------------------------------------------------
function captureDefaultCoverHeroes() {
  document.querySelectorAll('.cover-menu-card[data-cover-cat]').forEach(card => {
    const catId = card.dataset.coverCat;
    const bgImg = card.querySelector('.cover-card-bg-img');
    if (catId && bgImg) {
      DEFAULT_COVER_HEROES[catId] = bgImg.getAttribute('src');
    }
  });
}

function getCoverHeroOverrides() {
  try {
    const raw = localStorage.getItem(COVER_HERO_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
}

function saveCoverHeroOverrides(map) {
  try {
    localStorage.setItem(COVER_HERO_STORAGE_KEY, JSON.stringify(map));
  } catch (e) {
    // Ignore storage quota errors in restricted environments
  }
}

function findMatchingImageIndex(images, targetSrc) {
  if (!Array.isArray(images) || !targetSrc) return -1;
  return images.findIndex(img =>
    img.encoded_path === targetSrc ||
    img.rel_path === targetSrc ||
    targetSrc.endsWith('/' + img.filename)
  );
}

function getActiveCoverSrcForCategory(catId) {
  const overrides = getCoverHeroOverrides();
  if (overrides[catId]) return overrides[catId];
  const cardImg = document.querySelector(`.cover-menu-card[data-cover-cat="${catId}"] .cover-card-bg-img`);
  return cardImg ? cardImg.getAttribute('src') : (DEFAULT_COVER_HEROES[catId] || '');
}

function getOrderedImagesForCategory(catId, _slideEl) {
  const catData = CATALOG_CATEGORIES.find(c => c.id === catId);
  if (!catData || !Array.isArray(catData.images) || catData.images.length === 0) return [];
  const activeSrc = getActiveCoverSrcForCategory(catId);
  const idx = findMatchingImageIndex(catData.images, activeSrc);
  if (idx <= 0) return catData.images;
  return [catData.images[idx], ...catData.images.filter((_, i) => i !== idx)];
}

function applyCoverHeroForCategory(catId, encodedPath) {
  if (!catId || !encodedPath) return;

  // 1. Update Home Hub visual card background
  const card = document.querySelector(`.cover-menu-card[data-cover-cat="${catId}"]`);
  const cardImg = card?.querySelector('.cover-card-bg-img');
  if (cardImg) {
    cardImg.src = encodedPath;
  }

  // 2. Update corresponding category slide Hero image & active thumbnail state
  const targetSlide = document.querySelector(`section.slide[data-category-id="${catId}"]`);
  if (targetSlide && targetSlide.dataset.slideIndex !== '0') {
    const heroImg = targetSlide.querySelector('.hero-img');
    if (heroImg) {
      heroImg.src = encodedPath;
    }
    const thumbs = targetSlide.querySelectorAll('.slide-thumb-item');
    thumbs.forEach(t => {
      const tSrc = t.dataset.src || '';
      const isMatch = tSrc === encodedPath || encodedPath.endsWith(tSrc) || tSrc.endsWith(encodedPath);
      t.classList.toggle('active', isMatch);
    });
  }
}

function getSlideIndexByCategoryId(catId) {
  const el = document.querySelector(`section.slide[data-category-id="${catId}"]:not([data-slide-index="0"])`);
  return el ? parseInt(el.dataset.slideIndex, 10) : 0;
}

function captureDefaultCardTexts() {
  document.querySelectorAll('.cover-menu-card[data-cover-cat]').forEach(card => {
    const catId = card.dataset.coverCat;
    const titleEl = card.querySelector('.card-title');
    const descEl = card.querySelector('.card-desc');
    if (catId && titleEl && descEl) {
      DEFAULT_CARD_TEXTS[catId] = {
        title: titleEl.textContent.trim(),
        desc: descEl.textContent.trim()
      };
    }
  });
}

function readJsonStorage(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (e) {
    return fallback;
  }
}

function writeJsonStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    // Ignore storage quota errors
  }
}

function isAdminMode() {
  return !!sessionStorage.getItem(ADMIN_SESSION_TOKEN_KEY);
}

function syncAdminSessionClass() {
  document.body.classList.toggle('admin-mode', isAdminMode());
}

function setAdminMode(active, token = '') {
  if (active && token) {
    sessionStorage.setItem(ADMIN_SESSION_TOKEN_KEY, token);
  } else {
    sessionStorage.removeItem(ADMIN_SESSION_TOKEN_KEY);
  }
  syncAdminSessionClass();
}

function applySavedAdminData() {
  // 1. Apply static custom uploads (for Vercel/static fallback)
  const customUploads = readJsonStorage(ADMIN_CUSTOM_UPLOADS_KEY, []);
  if (Array.isArray(customUploads)) {
    customUploads.forEach(item => {
      const cat = CATALOG_CATEGORIES.find(c => c.id === item.catId);
      if (cat && item.image && !cat.images.some(im => im.filename === item.image.filename)) {
        cat.images.push(item.image);
      }
    });
  }

  // 2. Filter locally deleted photos (for Vercel/static fallback)
  const deletedKeys = readJsonStorage(ADMIN_DELETED_KEY, []);
  if (Array.isArray(deletedKeys) && deletedKeys.length > 0) {
    CATALOG_CATEGORIES.forEach(cat => {
      for (let i = cat.images.length - 1; i >= 0; i--) {
        const key = `${cat.id}::${cat.images[i].filename}`;
        if (deletedKeys.includes(key)) {
          cat.images.splice(i, 1);
        }
      }
    });
  }

  // 3. Apply saved card titles/descriptions
  const edits = readJsonStorage(ADMIN_CARD_EDITS_KEY, {});
  Object.entries(edits).forEach(([catId, val]) => {
    applyCardTextEdit(catId, val?.title, val?.desc);
  });

  // 4. Apply saved cover hero images
  applySavedCoverHeroes();
}

function applyCardTextEdit(catId, title, desc) {
  const card = document.querySelector(`.cover-menu-card[data-cover-cat="${catId}"]`);
  if (!card) return;
  const titleEl = card.querySelector('.card-title');
  const descEl = card.querySelector('.card-desc');
  if (titleEl && title) titleEl.textContent = title;
  if (descEl && desc) descEl.textContent = desc;
}

function refreshAllCategoryCounters() {
  const totalPhotos = CATALOG_CATEGORIES.reduce((acc, c) => acc + (c.images ? c.images.length : 0), 0);

  const coverGalleryBtn = document.querySelector('section.slide[data-slide-index="0"] button[onclick*="openGalleryModal"]');
  if (coverGalleryBtn) {
    coverGalleryBtn.textContent = `🖼️ เปิดคลังภาพผลงาน (${totalPhotos} ภาพ)`;
  }

  const drawerGalleryBtn = document.getElementById('btnDrawerGallery');
  if (drawerGalleryBtn) {
    drawerGalleryBtn.textContent = `🖼️ เปิดคลังภาพผลงาน (${totalPhotos} ภาพ)`;
  }

  CATALOG_CATEGORIES.forEach(cat => {
    const count = cat.images ? cat.images.length : 0;
    const cardCount = document.querySelector(`.cover-menu-card[data-cover-cat="${cat.id}"] .cover-card-count`);
    if (cardCount) {
      cardCount.textContent = `${count} ภาพ`;
    }
    const slideEl = document.querySelector(`section.slide[data-category-id="${cat.id}"]:not([data-slide-index="0"])`);
    if (slideEl) {
      const pill = slideEl.querySelector('.photo-count-pill');
      if (pill) {
        pill.textContent = pill.textContent.replace(/\d+/, String(count));
      }
    }
  });
}

function applySavedCoverHeroes() {
  const overrides = getCoverHeroOverrides();
  Object.entries(overrides).forEach(([catId, path]) => {
    const catData = CATALOG_CATEGORIES.find(c => c.id === catId);
    if (catData && findMatchingImageIndex(catData.images, path) >= 0) {
      applyCoverHeroForCategory(catId, path);
    }
  });
}

function initCoverMenuHub() {
  document.querySelectorAll('.cover-menu-card[data-cover-cat]').forEach(card => {
    const catId = card.dataset.coverCat;
    const slideIdx = parseInt(card.dataset.coverSlide, 10);
    const pickBtn = card.querySelector('.btn-cover-pick');
    if (pickBtn && !card.querySelector('.cover-card-admin-btns')) {
      const wrap = document.createElement('div');
      wrap.className = 'cover-card-admin-btns admin-only';
      const editBtn = document.createElement('button');
      editBtn.type = 'button';
      editBtn.className = 'btn-cover-edit';
      editBtn.textContent = '✏️ แก้ไข';
      editBtn.title = 'แก้ไขชื่อและคำอธิบายเมนู';
      editBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!isAdminMode()) return;
        openAdminEditModal(catId, slideIdx);
      });
      pickBtn.parentNode.insertBefore(wrap, pickBtn);
      wrap.appendChild(editBtn);
      wrap.appendChild(pickBtn);
    }
  });

  document.querySelectorAll('.btn-cover-pick').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (!isAdminMode()) return;
      const catId = btn.dataset.pickCat;
      const slideIdx = parseInt(btn.dataset.pickSlide, 10);
      openCoverPickerModal(catId, slideIdx);
    });
  });

  const pickerOverlay = document.getElementById('coverPickerModal');
  pickerOverlay?.addEventListener('click', (e) => {
    if (e.target === pickerOverlay) closeCoverPickerModal();
  });
}

function closeDrawerOverlay() {
  document.getElementById('mobileDrawerOverlay')?.classList.remove('active');
  document.getElementById('mobileDrawer')?.classList.remove('active');
}

function initAdminControls() {
  document.getElementById('btnDrawerAdminLogin')?.addEventListener('click', () => {
    closeDrawerOverlay();
    openAdminLoginModal();
  });

  document.getElementById('btnDrawerAdminUpload')?.addEventListener('click', () => {
    closeDrawerOverlay();
    openAdminUploadModal();
  });
  document.getElementById('btnHomeAdminUpload')?.addEventListener('click', () => openAdminUploadModal());
  document.getElementById('btnGalleryUpload')?.addEventListener('click', () => openAdminUploadModal());

  document.getElementById('btnDrawerAdminManage')?.addEventListener('click', () => {
    closeDrawerOverlay();
    openGalleryModal('all');
  });
  document.getElementById('btnHomeAdminGallery')?.addEventListener('click', () => openGalleryModal('all'));

  document.getElementById('btnDrawerAdminLogout')?.addEventListener('click', () => {
    closeDrawerOverlay();
    logoutAdmin();
  });
  document.getElementById('btnHomeAdminLogout')?.addEventListener('click', () => logoutAdmin());

  document.getElementById('btnLbSetHero')?.addEventListener('click', (e) => {
    e.stopPropagation();
    if (!isAdminMode() || lightboxCurrentImages.length === 0) return;
    const cur = lightboxCurrentImages[lightboxCurrentIndex];
    const catId = cur?.catId || lightboxCurrentCatId;
    if (!catId || !cur) return;
    const slideIdx = getSlideIndexByCategoryId(catId);
    selectCoverHeroImage(catId, slideIdx, cur.encoded_path || cur.rel_path);
  });

  document.getElementById('btnLbDeletePhoto')?.addEventListener('click', (e) => {
    e.stopPropagation();
    if (!isAdminMode() || lightboxCurrentImages.length === 0) return;
    const cur = lightboxCurrentImages[lightboxCurrentIndex];
    const catId = cur?.catId || lightboxCurrentCatId;
    if (!catId || !cur) return;
    deleteCatalogPhoto(catId, cur.filename, cur.rel_path, cur.encoded_path);
  });

  document.getElementById('adminLoginForm')?.addEventListener('submit', handleAdminLoginSubmit);
  document.getElementById('btnAdminUploadSubmit')?.addEventListener('click', handleAdminUploadSubmit);
  document.getElementById('adminUploadFiles')?.addEventListener('change', handleAdminUploadFilePreview);
  document.getElementById('adminEditForm')?.addEventListener('submit', handleAdminEditSubmit);
  document.getElementById('btnAdminEditReset')?.addEventListener('click', handleAdminEditReset);

  ['adminLoginModal', 'adminUploadModal', 'adminEditModal'].forEach(id => {
    const el = document.getElementById(id);
    el?.addEventListener('click', (e) => {
      if (e.target === el) el.classList.remove('active');
    });
  });
}

function openAdminLoginModal() {
  const modal = document.getElementById('adminLoginModal');
  if (!modal) return;
  const errEl = document.getElementById('adminLoginError');
  if (errEl) errEl.textContent = '';
  document.getElementById('adminUsernameInput').value = '';
  document.getElementById('adminPasswordInput').value = '';
  modal.classList.add('active');
  setTimeout(() => document.getElementById('adminUsernameInput')?.focus(), 80);
}

function closeAdminLoginModal() {
  document.getElementById('adminLoginModal')?.classList.remove('active');
}

function verifyStaticAdminCredentials(user, pass) {
  try {
    return user === 'admin' && btoa(unescape(encodeURIComponent(pass))) === 'YWRtaW4xMjM0';
  } catch (e) {
    return false;
  }
}

async function handleAdminLoginSubmit(e) {
  e.preventDefault();
  const username = document.getElementById('adminUsernameInput').value.trim();
  const password = document.getElementById('adminPasswordInput').value.trim();
  const errEl = document.getElementById('adminLoginError');
  if (errEl) errEl.textContent = '';

  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (res.status === 401) {
      const data = await res.json().catch(() => ({}));
      if (errEl) errEl.textContent = data.message || 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง';
      return;
    }
    if (res.ok) {
      const data = await res.json();
      if (data.success) {
        setAdminMode(true, data.token || 'rathcharot_admin_token_2026_secured');
        closeAdminLoginModal();
        return;
      }
    }
  } catch (err) {
    // Fallback below when served from static CDN (no Python API server)
  }

  if (verifyStaticAdminCredentials(username, password)) {
    setAdminMode(true, 'rathcharot_admin_token_2026_secured');
    closeAdminLoginModal();
  } else if (errEl) {
    errEl.textContent = 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง';
  }
}

function logoutAdmin() {
  setAdminMode(false);
  closeCoverPickerModal();
  closeAdminUploadModal();
  closeAdminEditModal();
  if (document.getElementById('galleryModal')?.classList.contains('active')) {
    renderGalleryGrid(currentGalleryCat, false);
  }
}

let pendingAdminUploadFiles = [];

function openAdminUploadModal(defaultCatId = '') {
  if (!isAdminMode()) return;
  const modal = document.getElementById('adminUploadModal');
  const select = document.getElementById('adminUploadCategory');
  const fileInput = document.getElementById('adminUploadFiles');
  const preview = document.getElementById('adminUploadPreviewList');
  const statusEl = document.getElementById('adminUploadStatus');
  if (!modal || !select) return;

  select.innerHTML = '';
  CATALOG_CATEGORIES.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat.id;
    opt.textContent = cat.title;
    select.appendChild(opt);
  });
  if (defaultCatId) {
    select.value = defaultCatId;
  } else if (currentGalleryCat && currentGalleryCat !== 'all') {
    select.value = currentGalleryCat;
  }

  pendingAdminUploadFiles = [];
  if (fileInput) fileInput.value = '';
  if (preview) preview.innerHTML = '';
  if (statusEl) statusEl.textContent = '';
  modal.classList.add('active');
}

function closeAdminUploadModal() {
  document.getElementById('adminUploadModal')?.classList.remove('active');
}

function handleAdminUploadFilePreview(e) {
  pendingAdminUploadFiles = Array.from(e.target.files || []);
  const preview = document.getElementById('adminUploadPreviewList');
  if (!preview) return;
  preview.innerHTML = pendingAdminUploadFiles
    .map(f => `<div>📷 ${f.name} (${Math.round(f.size / 1024)} KB)</div>`)
    .join('');
}

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

async function handleAdminUploadSubmit() {
  if (!isAdminMode()) return;
  const catId = document.getElementById('adminUploadCategory')?.value;
  const statusEl = document.getElementById('adminUploadStatus');
  const btn = document.getElementById('btnAdminUploadSubmit');
  if (!catId || pendingAdminUploadFiles.length === 0) {
    if (statusEl) statusEl.textContent = 'กรุณาเลือกไฟล์ภาพอย่างน้อย 1 ภาพ';
    return;
  }

  const cat = CATALOG_CATEGORIES.find(c => c.id === catId);
  if (!cat) return;

  if (btn) btn.disabled = true;
  if (statusEl) statusEl.textContent = 'กำลังเพิ่มภาพ...';

  let uploadedViaApi = false;
  const customUploads = readJsonStorage(ADMIN_CUSTOM_UPLOADS_KEY, []);

  for (const file of pendingAdminUploadFiles) {
    const dataUrl = await readFileAsDataUrl(file);
    let savedToServer = false;
    try {
      const res = await fetch('/api/upload-photo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category_id: catId,
          filename: file.name,
          data_base64: dataUrl
        })
      });
      if (res.ok) {
        const resData = await res.json();
        if (resData.success) {
          savedToServer = true;
          uploadedViaApi = true;
        }
      }
    } catch (err) {
      // Static mode fallback below
    }

    if (!savedToServer) {
      const staticImg = {
        filename: file.name,
        rel_path: `${cat.folder}/${file.name}`,
        encoded_path: dataUrl
      };
      cat.images.push(staticImg);
      customUploads.push({ catId, image: staticImg });
    }
  }

  if (uploadedViaApi) {
    await syncCategoriesFromServerApi();
  } else {
    writeJsonStorage(ADMIN_CUSTOM_UPLOADS_KEY, customUploads);
  }

  if (btn) btn.disabled = false;
  buildGalleryModal();
  refreshAllCategoryCounters();
  if (document.getElementById('galleryModal')?.classList.contains('active')) {
    openGalleryModal(catId);
  }
  closeAdminUploadModal();
}

async function syncCategoriesFromServerApi() {
  try {
    const res = await fetch('/api/catalog-data');
    if (!res.ok) return;
    const data = await res.json();
    if (Array.isArray(data.categories)) {
      data.categories.forEach(serverCat => {
        const localCat = CATALOG_CATEGORIES.find(c => c.id === serverCat.id);
        if (localCat && Array.isArray(serverCat.images)) {
          localCat.images.length = 0;
          localCat.images.push(...serverCat.images);
        }
      });
    }
  } catch (e) {
    // Ignore when static
  }
}

let activeEditCatId = '';

function openAdminEditModal(catId, _slideIdx) {
  if (!isAdminMode() || !catId) return;
  const modal = document.getElementById('adminEditModal');
  const titleInput = document.getElementById('adminEditTitleInput');
  const descInput = document.getElementById('adminEditDescInput');
  const card = document.querySelector(`.cover-menu-card[data-cover-cat="${catId}"]`);
  if (!modal || !titleInput || !descInput || !card) return;

  activeEditCatId = catId;
  titleInput.value = card.querySelector('.card-title')?.textContent.trim() || '';
  descInput.value = card.querySelector('.card-desc')?.textContent.trim() || '';
  modal.classList.add('active');
}

function closeAdminEditModal() {
  document.getElementById('adminEditModal')?.classList.remove('active');
  activeEditCatId = '';
}

function handleAdminEditSubmit(e) {
  e.preventDefault();
  if (!isAdminMode() || !activeEditCatId) return;
  const title = document.getElementById('adminEditTitleInput').value.trim();
  const desc = document.getElementById('adminEditDescInput').value.trim();
  const edits = readJsonStorage(ADMIN_CARD_EDITS_KEY, {});
  edits[activeEditCatId] = { title, desc };
  writeJsonStorage(ADMIN_CARD_EDITS_KEY, edits);
  applyCardTextEdit(activeEditCatId, title, desc);
  closeAdminEditModal();
}

function handleAdminEditReset() {
  if (!isAdminMode() || !activeEditCatId) return;
  const def = DEFAULT_CARD_TEXTS[activeEditCatId];
  const edits = readJsonStorage(ADMIN_CARD_EDITS_KEY, {});
  delete edits[activeEditCatId];
  writeJsonStorage(ADMIN_CARD_EDITS_KEY, edits);
  if (def) {
    applyCardTextEdit(activeEditCatId, def.title, def.desc);
  }
  closeAdminEditModal();
}

async function deleteCatalogPhoto(catId, filename, relPath, encodedPath) {
  if (!isAdminMode() || !catId || !filename) return;
  if (!window.confirm(`ต้องการลบภาพ "${filename}" ออกจากหมวดนี้หรือไม่?`)) return;

  let deletedOnServer = false;
  try {
    const res = await fetch('/api/delete-photo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category_id: catId, filename })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success) deletedOnServer = true;
    }
  } catch (err) {
    // Fallback for static Vercel mode
  }

  const cat = CATALOG_CATEGORIES.find(c => c.id === catId);
  if (cat) {
    const idx = cat.images.findIndex(im => im.filename === filename || im.encoded_path === encodedPath || im.rel_path === relPath);
    if (idx >= 0) cat.images.splice(idx, 1);
  }

  if (!deletedOnServer) {
    const customUploads = readJsonStorage(ADMIN_CUSTOM_UPLOADS_KEY, []);
    const filteredCustom = customUploads.filter(u => !(u.catId === catId && u.image?.filename === filename));
    if (filteredCustom.length !== customUploads.length) {
      writeJsonStorage(ADMIN_CUSTOM_UPLOADS_KEY, filteredCustom);
    } else {
      const deletedKeys = readJsonStorage(ADMIN_DELETED_KEY, []);
      const key = `${catId}::${filename}`;
      if (!deletedKeys.includes(key)) {
        deletedKeys.push(key);
        writeJsonStorage(ADMIN_DELETED_KEY, deletedKeys);
      }
    }
  }

  // Fallback hero/cover if the deleted image was active
  const currentCover = getActiveCoverSrcForCategory(catId);
  if (currentCover && (currentCover === encodedPath || currentCover.endsWith('/' + filename)) && cat && cat.images.length > 0) {
    const slideIdx = getSlideIndexByCategoryId(catId);
    selectCoverHeroImage(catId, slideIdx, cat.images[0].encoded_path);
  }

  buildGalleryModal();
  refreshAllCategoryCounters();

  if (document.getElementById('galleryModal')?.classList.contains('active')) {
    openGalleryModal(currentGalleryCat || 'all');
  }

  if (document.getElementById('lightboxModal')?.classList.contains('active')) {
    lightboxCurrentImages = lightboxCurrentImages.filter(im => im.filename !== filename);
    if (lightboxCurrentImages.length === 0) {
      closeLightbox();
    } else {
      lightboxCurrentIndex = Math.min(lightboxCurrentIndex, lightboxCurrentImages.length - 1);
      renderLightboxFrame();
    }
  }
}

function openCoverPickerModal(catId, slideIdx) {
  if (!isAdminMode()) return;
  const modal = document.getElementById('coverPickerModal');
  const grid = document.getElementById('coverPickerGrid');
  const titleEl = document.getElementById('coverPickerTitle');
  const resetBtn = document.getElementById('btnResetCoverHero');
  if (!modal || !grid) return;

  const catData = CATALOG_CATEGORIES.find(c => c.id === catId);
  if (!catData || !Array.isArray(catData.images)) return;

  if (titleEl) {
    titleEl.textContent = `🖼️ เลือกภาพหลัก: ${catData.title}`;
  }

  const currentSrc = getActiveCoverSrcForCategory(catId);
  const currentIdx = findMatchingImageIndex(catData.images, currentSrc);
  grid.innerHTML = '';

  catData.images.forEach((img, idx) => {
    const isSelected = idx === currentIdx || img.encoded_path === currentSrc;
    const card = document.createElement('div');
    card.className = `gallery-card cover-picker-card${isSelected ? ' selected' : ''}`;
    card.innerHTML = `
      ${isSelected ? '<span class="cover-picker-active-tag">✓ ภาพหลักปัจจุบัน</span>' : ''}
      <img src="${img.encoded_path}" alt="${img.filename}" loading="lazy" decoding="async" />
      <div class="gallery-card-badge">ภาพที่ ${idx + 1} / ${catData.images.length}</div>
    `;
    card.addEventListener('click', () => {
      selectCoverHeroImage(catId, slideIdx, img.encoded_path);
    });
    grid.appendChild(card);
  });

  if (resetBtn) {
    resetBtn.onclick = () => resetCoverHeroForCategory(catId, slideIdx);
  }

  modal.classList.add('active');
}

function closeCoverPickerModal() {
  const modal = document.getElementById('coverPickerModal');
  if (!modal) return;
  modal.classList.remove('active');
  setTimeout(() => {
    const grid = document.getElementById('coverPickerGrid');
    if (grid && !modal.classList.contains('active')) {
      grid.innerHTML = '';
    }
  }, 250);
}

function persistCoverToServer(slideIdx, heroSrc) {
  if (!slideIdx || !heroSrc || heroSrc.startsWith('data:')) return;
  fetch('/api/save-slide', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      slide_index: slideIdx,
      hero_src: heroSrc,
      thumbs: null
    })
  }).catch(() => {});
}

function selectCoverHeroImage(catId, slideIdx, encodedPath) {
  const overrides = getCoverHeroOverrides();
  overrides[catId] = encodedPath;
  saveCoverHeroOverrides(overrides);
  applyCoverHeroForCategory(catId, encodedPath);
  persistCoverToServer(slideIdx, encodedPath);
  closeCoverPickerModal();
}

function resetCoverHeroForCategory(catId, slideIdx) {
  const defaultSrc = DEFAULT_COVER_HEROES[catId];
  const overrides = getCoverHeroOverrides();
  delete overrides[catId];
  saveCoverHeroOverrides(overrides);
  if (defaultSrc) {
    applyCoverHeroForCategory(catId, defaultSrc);
    persistCoverToServer(slideIdx, defaultSrc);
  }
  closeCoverPickerModal();
}

// Expose handlers globally
window.updateSlideView = updateSlideView;
window.openSlideLightbox = openSlideLightbox;
window.nextSlide = nextSlide;
window.prevSlide = prevSlide;
window.openLightbox = openLightbox;
window.closeLightbox = closeLightbox;
window.nextLightboxImage = nextLightboxImage;
window.prevLightboxImage = prevLightboxImage;
window.closeGalleryModal = closeGalleryModal;
window.openGalleryModal = openGalleryModal;
window.openQrModal = openQrModal;
window.closeQrModal = closeQrModal;
window.openCoverPickerModal = openCoverPickerModal;
window.closeCoverPickerModal = closeCoverPickerModal;
window.selectCoverHeroImage = selectCoverHeroImage;
window.resetCoverHeroForCategory = resetCoverHeroForCategory;
window.openAdminLoginModal = openAdminLoginModal;
window.closeAdminLoginModal = closeAdminLoginModal;
window.openAdminUploadModal = openAdminUploadModal;
window.closeAdminUploadModal = closeAdminUploadModal;
window.openAdminEditModal = openAdminEditModal;
window.closeAdminEditModal = closeAdminEditModal;
window.logoutAdmin = logoutAdmin;
window.fitStageToScreen = fitStageToScreen;
