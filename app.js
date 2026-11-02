// ==========================================================================
// Rathcharot & ChangPhapNganSop Presentation Controller
// Canva-Style Auto-Scaling Engine & Slide Navigation
// ==========================================================================

let currentSlideIndex = 0;
let slides = [];
let lightboxCurrentImages = [];
let lightboxCurrentIndex = 0;

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

function initApp() {
  slides = Array.from(document.querySelectorAll('.slide'));
  
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
  buildGalleryModal();
  
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

  // Mobile check: If screen is phone/tablet portrait (<= 900px or portrait), use 100% native mobile card layout
  const isMobile = window.innerWidth <= 900 || window.matchMedia('(orientation: portrait)').matches;
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
function updateSlideView(index) {
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
    const lightboxModal = document.getElementById('lightboxModal');
    const galleryModal = document.getElementById('galleryModal');
    const qrModal = document.getElementById('qrModal');

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
  let touchStartX = 0;
  let touchEndX = 0;
  let touchStartY = 0;
  let touchEndY = 0;

  const targetArea = document.querySelector('.viewport-container') || document.body;
  if (!targetArea) return;

  targetArea.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
  }, { passive: true });

  targetArea.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    touchEndY = e.changedTouches[0].screenY;
    handleSwipe();
  }, { passive: true });

  function handleSwipe() {
    const diffX = touchEndX - touchStartX;
    const diffY = touchEndY - touchStartY;
    // Require at least 45px swipe and more horizontal than vertical
    if (Math.abs(diffX) > 45 && Math.abs(diffX) > Math.abs(diffY)) {
      if (diffX < 0) nextSlide();
      else prevSlide();
    }
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
      updateSlideView(idx);
    });
  });

  // Brand click -> Slide 0
  document.querySelector('.brand-badge')?.addEventListener('click', () => updateSlideView(0));

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
      updateSlideView(idx);
      closeDrawer();
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
        const activeIdx = catData.images.findIndex(img => img.encoded_path === activeSrc || img.rel_path === activeSrc);
        openLightbox(catData.images, activeIdx >= 0 ? activeIdx : 0, catData.title);
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
function openLightbox(imagesList, startIndex = 0, title = '') {
  lightboxCurrentImages = imagesList;
  lightboxCurrentIndex = startIndex;

  const modal = document.getElementById('lightboxModal');
  const img = document.getElementById('lightboxImg');
  const caption = document.getElementById('lightboxCaption');

  if (!modal || !img) return;

  function render() {
    const cur = lightboxCurrentImages[lightboxCurrentIndex];
    img.src = cur.encoded_path || cur.rel_path;
    img.alt = cur.filename;
    if (caption) {
      caption.textContent = `${title || 'ภาพผลงาน'} (${lightboxCurrentIndex + 1} / ${lightboxCurrentImages.length}) - ${cur.filename}`;
    }
  }

  render();
  modal.classList.add('active');
}

function closeLightbox() {
  document.getElementById('lightboxModal')?.classList.remove('active');
}

function nextLightboxImage() {
  if (lightboxCurrentImages.length === 0) return;
  lightboxCurrentIndex = (lightboxCurrentIndex + 1) % lightboxCurrentImages.length;
  const cur = lightboxCurrentImages[lightboxCurrentIndex];
  const img = document.getElementById('lightboxImg');
  const caption = document.getElementById('lightboxCaption');
  if (img) img.src = cur.encoded_path || cur.rel_path;
  if (caption) {
    caption.textContent = `ภาพ ${lightboxCurrentIndex + 1} จาก ${lightboxCurrentImages.length} - ${cur.filename}`;
  }
}

function prevLightboxImage() {
  if (lightboxCurrentImages.length === 0) return;
  lightboxCurrentIndex = (lightboxCurrentIndex - 1 + lightboxCurrentImages.length) % lightboxCurrentImages.length;
  const cur = lightboxCurrentImages[lightboxCurrentIndex];
  const img = document.getElementById('lightboxImg');
  const caption = document.getElementById('lightboxCaption');
  if (img) img.src = cur.encoded_path || cur.rel_path;
  if (caption) {
    caption.textContent = `ภาพ ${lightboxCurrentIndex + 1} จาก ${lightboxCurrentImages.length} - ${cur.filename}`;
  }
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
        allImagesForCat.push({ ...img, catTitle: cat.title });
      });
    });
  } else {
    const cat = CATALOG_CATEGORIES.find(c => c.id === selectedCatId);
    if (cat) {
      allImagesForCat = cat.images.map(img => ({ ...img, catTitle: cat.title }));
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
      <span class="gallery-card-zoom-icon">🔍</span>
      <div class="gallery-card-badge">${img.catTitle || ''} • ภาพที่ ${globalIdx + 1}</div>
    `;
    card.addEventListener('click', () => {
      openLightbox(allImagesForCat, globalIdx, allImagesForCat[globalIdx]?.catTitle || 'คลังภาพผลงาน');
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

// Expose handlers globally
window.updateSlideView = updateSlideView;
window.nextSlide = nextSlide;
window.prevSlide = prevSlide;
window.closeLightbox = closeLightbox;
window.nextLightboxImage = nextLightboxImage;
window.prevLightboxImage = prevLightboxImage;
window.closeGalleryModal = closeGalleryModal;
window.openGalleryModal = openGalleryModal;
window.openQrModal = openQrModal;
window.closeQrModal = closeQrModal;
window.fitStageToScreen = fitStageToScreen;
