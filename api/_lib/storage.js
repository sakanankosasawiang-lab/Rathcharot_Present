const fs = require('fs');
const path = require('path');

const STATE_BLOB_PATH = '_rathcharot_state/catalog_state.json';
const TMP_STATE_PATH = path.join('/tmp', 'rathcharot_catalog_state.json');
const KV_STATE_KEY = 'rathcharot:catalog_state:v2';

let memoryFallbackState = null;

function createEmptyState() {
  return {
    added_photos: [],     // [{ catId, filename, rel_path, encoded_path, blob_url, uploaded_at }]
    deleted_photos: [],   // [{ catId, folder, filename, rel_path, encoded_path, blob_url, deleted_at, is_custom }]
    cover_heroes: {},     // { [catId]: encoded_path }
    card_edits: {},       // { [catId]: { title, desc } }
    slide_edits: {}       // { [catId]: { title, subtitle, badge, why_us: [] } }
  };
}

function getStorageMode() {
  if (process.env.BLOB_READ_WRITE_TOKEN) {
    return process.env.KV_REST_API_URL && process.env.KV_REST_API_TOKEN
      ? 'vercel-blob-kv'
      : 'vercel-blob';
  }
  if (process.env.KV_REST_API_URL && process.env.KV_REST_API_TOKEN) {
    return 'vercel-kv';
  }
  return 'ephemeral';
}

function loadBaseCatalogCategories() {
  const candidates = [
    path.join(process.cwd(), 'catalog_data.js'),
    path.join(__dirname, '..', '..', 'catalog_data.js')
  ];
  let raw = '';
  for (const p of candidates) {
    if (fs.existsSync(p)) {
      raw = fs.readFileSync(p, 'utf8');
      break;
    }
  }
  if (!raw) return [];
  const match = raw.match(/const CATALOG_CATEGORIES = (\[[\s\S]*?\]);/);
  if (!match) return [];
  try {
    return JSON.parse(match[1]);
  } catch {
    return [];
  }
}

async function kvGet(key) {
  const url = process.env.KV_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN;
  if (!url || !token) return null;
  const res = await fetch(`${url}/get/${encodeURIComponent(key)}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) return null;
  const data = await res.json();
  if (!data || data.result == null) return null;
  return typeof data.result === 'string' ? JSON.parse(data.result) : data.result;
}

async function kvSet(key, value) {
  const url = process.env.KV_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN;
  if (!url || !token) return false;
  const res = await fetch(`${url}/set/${encodeURIComponent(key)}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(value)
  });
  return res.ok;
}

async function readState() {
  const mode = getStorageMode();

  if (mode === 'vercel-blob-kv' || mode === 'vercel-kv') {
    try {
      const state = await kvGet(KV_STATE_KEY);
      if (state) return { ...createEmptyState(), ...state };
    } catch {
      // fallback below
    }
  }

  if (mode === 'vercel-blob' || mode === 'vercel-blob-kv') {
    try {
      const { list } = require('@vercel/blob');
      const result = await list({ prefix: STATE_BLOB_PATH, limit: 1 });
      const blob = result.blobs.find(b => b.pathname === STATE_BLOB_PATH) || result.blobs[0];
      if (blob && blob.url) {
        const res = await fetch(`${blob.url}?t=${Date.now()}`, { cache: 'no-store' });
        if (res.ok) {
          const parsed = await res.json();
          return { ...createEmptyState(), ...parsed };
        }
      }
    } catch {
      // fallback below
    }
  }

  // Ephemeral /tmp fallback
  try {
    if (fs.existsSync(TMP_STATE_PATH)) {
      const parsed = JSON.parse(fs.readFileSync(TMP_STATE_PATH, 'utf8'));
      memoryFallbackState = { ...createEmptyState(), ...parsed };
      return memoryFallbackState;
    }
  } catch {
    // ignore
  }
  if (memoryFallbackState) return memoryFallbackState;
  return createEmptyState();
}

async function writeState(state) {
  const merged = { ...createEmptyState(), ...state };
  const mode = getStorageMode();

  if (mode === 'vercel-blob-kv' || mode === 'vercel-kv') {
    try {
      const ok = await kvSet(KV_STATE_KEY, merged);
      if (ok) return true;
    } catch {
      // continue to blob/tmp
    }
  }

  if (mode === 'vercel-blob' || mode === 'vercel-blob-kv') {
    try {
      const { put } = require('@vercel/blob');
      await put(STATE_BLOB_PATH, JSON.stringify(merged), {
        access: 'public',
        addRandomSuffix: false,
        allowOverwrite: true,
        contentType: 'application/json'
      });
      return true;
    } catch {
      // continue to tmp
    }
  }

  memoryFallbackState = merged;
  try {
    fs.writeFileSync(TMP_STATE_PATH, JSON.stringify(merged), 'utf8');
  } catch {
    // ignore if /tmp unavailable on Windows local test
  }
  return true;
}

function sanitizeFilename(name) {
  const base = path.basename(String(name || 'photo.jpg'));
  const clean = base.replace(/[^\w.\-\u0E00-\u0E7F ]+/g, '_').trim();
  return clean || `photo_${Date.now()}.jpg`;
}

async function storeUploadedImage(catId, filename, dataBase64) {
  const safeName = sanitizeFilename(filename);
  const uniqueName = `${Date.now()}_${safeName}`;
  const mode = getStorageMode();

  let mimeType = 'image/jpeg';
  let rawBase64 = String(dataBase64 || '');
  const dataUrlMatch = rawBase64.match(/^data:(image\/[a-zA-Z0-9.+-]+);base64,(.*)$/);
  if (dataUrlMatch) {
    mimeType = dataUrlMatch[1];
    rawBase64 = dataUrlMatch[2];
  }

  if ((mode === 'vercel-blob' || mode === 'vercel-blob-kv') && process.env.BLOB_READ_WRITE_TOKEN) {
    const { put } = require('@vercel/blob');
    const buffer = Buffer.from(rawBase64, 'base64');
    const blobPath = `uploads/${catId}/${uniqueName}`;
    const blob = await put(blobPath, buffer, {
      access: 'public',
      contentType: mimeType,
      addRandomSuffix: false
    });
    return {
      filename: safeName,
      stored_name: uniqueName,
      rel_path: blobPath,
      encoded_path: blob.url,
      blob_url: blob.url
    };
  }

  // Fallback when Vercel Blob is not connected yet: store compact data URL in state
  const fullDataUrl = dataUrlMatch ? dataBase64 : `data:${mimeType};base64,${rawBase64}`;
  return {
    filename: safeName,
    stored_name: uniqueName,
    rel_path: `uploads/${catId}/${uniqueName}`,
    encoded_path: fullDataUrl,
    blob_url: ''
  };
}

async function deleteBlobIfPresent(blobUrl) {
  if (!blobUrl || !process.env.BLOB_READ_WRITE_TOKEN) return;
  try {
    const { del } = require('@vercel/blob');
    await del(blobUrl);
  } catch {
    // ignore
  }
}

async function getMergedCatalog() {
  const baseCats = loadBaseCatalogCategories();
  const state = await readState();

  const deletedSet = new Set(
    (state.deleted_photos || []).map(d => `${d.catId}::${d.filename}`)
  );

  const categories = baseCats.map(cat => {
    const images = (cat.images || [])
      .filter(img => !deletedSet.has(`${cat.id}::${img.filename}`))
      .map(img => ({ ...img }));

    const added = (state.added_photos || [])
      .filter(p => p.catId === cat.id && !deletedSet.has(`${cat.id}::${p.filename}`));

    added.forEach(p => {
      if (!images.some(im => im.filename === p.filename && im.encoded_path === p.encoded_path)) {
        images.push({
          filename: p.filename,
          rel_path: p.rel_path,
          encoded_path: p.encoded_path,
          is_custom: true
        });
      }
    });

    const slideEdit = (state.slide_edits || {})[cat.id] || {};
    return {
      ...cat,
      title: slideEdit.title || cat.title,
      subtitle: slideEdit.subtitle || cat.subtitle,
      badge: slideEdit.badge || cat.badge,
      why_us: Array.isArray(slideEdit.why_us) && slideEdit.why_us.length > 0 ? slideEdit.why_us : cat.why_us,
      images
    };
  });

  const SLIDE_MAP = [
    { slide_index: 1, category_id: 'streaming' },
    { slide_index: 2, category_id: 'royal' },
    { slide_index: 3, category_id: 'chinese' },
    { slide_index: 4, category_id: 'chanting' },
    { slide_index: 5, category_id: 'cremation' },
    { slide_index: 6, category_id: 'floating' },
    { slide_index: 7, category_id: 'profile' },
    { slide_index: 8, category_id: 'coffin' },
    { slide_index: 9, category_id: 'promotion' }
  ];

  const slides = SLIDE_MAP.map(({ slide_index, category_id }) => {
    const cat = categories.find(c => c.id === category_id);
    const imgs = cat ? cat.images : [];
    const savedSlide = (state.slide_edits || {})[category_id] || (state.slide_edits || {})[String(slide_index)] || {};
    const coverOverride = (state.cover_heroes || {})[category_id];
    const hero_src = savedSlide.hero_src || coverOverride || (imgs[0] ? imgs[0].encoded_path : '');
    const defaultThumbs = imgs.slice(0, 6).map(i => i.encoded_path);
    const thumbs = Array.isArray(savedSlide.thumbs) && savedSlide.thumbs.length > 0
      ? savedSlide.thumbs
      : defaultThumbs;
    return {
      slide_index,
      category_id,
      title: cat ? cat.title : category_id,
      hero_src,
      hero_alt: savedSlide.hero_alt || (cat ? cat.title : 'ภาพบรรยากาศพิธีการ'),
      thumbs
    };
  });

  return {
    categories,
    slides,
    cover_heroes: state.cover_heroes || {},
    card_edits: state.card_edits || {},
    slide_edits: state.slide_edits || {},
    deleted_count: (state.deleted_photos || []).length,
    storage_mode: getStorageMode()
  };
}

module.exports = {
  getStorageMode,
  loadBaseCatalogCategories,
  readState,
  writeState,
  storeUploadedImage,
  deleteBlobIfPresent,
  getMergedCatalog
};
