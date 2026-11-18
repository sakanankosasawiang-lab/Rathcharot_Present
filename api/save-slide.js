const { requireAdmin, parseBody } = require('./_lib/auth');
const { readState, writeState, getStorageMode } = require('./_lib/storage');

const SLIDE_TO_CAT = {
  1: 'streaming',
  2: 'royal',
  3: 'chinese',
  4: 'chanting',
  5: 'cremation',
  6: 'floating',
  7: 'profile',
  8: 'coffin',
  9: 'promotion'
};

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  if (req.method !== 'POST') {
    res.status(405).json({ status: 'error', success: false, message: 'Method not allowed' });
    return;
  }
  if (!requireAdmin(req, res)) return;

  try {
    const body = parseBody(req);
    const state = await readState();
    state.cover_heroes = state.cover_heroes || {};
    state.card_edits = state.card_edits || {};
    state.slide_edits = state.slide_edits || {};

    const slideIndex = body.slide_index != null ? Number(body.slide_index) : null;
    const catId = String(body.category_id || (slideIndex ? SLIDE_TO_CAT[slideIndex] : '') || '').trim();

    if (!catId) {
      res.status(400).json({ status: 'error', success: false, message: 'ไม่ระบุหมวดหมู่หรือหมายเลขสไลด์' });
      return;
    }

    // 1. Cover hero update
    if (body.reset_cover_hero) {
      delete state.cover_heroes[catId];
      if (state.slide_edits[catId]) delete state.slide_edits[catId].hero_src;
    } else if (body.cover_hero || body.hero_src) {
      const heroPath = String(body.cover_hero || body.hero_src);
      state.cover_heroes[catId] = heroPath;
      state.slide_edits[catId] = { ...(state.slide_edits[catId] || {}), hero_src: heroPath };
    }

    // 2. Slide thumbs / alt update (from admin.html)
    if (Array.isArray(body.thumbs)) {
      state.slide_edits[catId] = { ...(state.slide_edits[catId] || {}), thumbs: body.thumbs };
    }
    if (body.hero_alt) {
      state.slide_edits[catId] = { ...(state.slide_edits[catId] || {}), hero_alt: String(body.hero_alt) };
    }

    // 3. Card title / desc update (from index.html admin modal)
    if (body.reset_card_edit) {
      delete state.card_edits[catId];
    } else if (body.card_title != null || body.card_desc != null) {
      state.card_edits[catId] = {
        title: String(body.card_title || '').trim(),
        desc: String(body.card_desc || '').trim()
      };
    }

    // 4. Slide text update (title / subtitle / why_us)
    if (body.slide_title != null || body.slide_subtitle != null || Array.isArray(body.why_us)) {
      const cur = state.slide_edits[catId] || {};
      if (body.slide_title != null) cur.title = String(body.slide_title).trim();
      if (body.slide_subtitle != null) cur.subtitle = String(body.slide_subtitle).trim();
      if (Array.isArray(body.why_us)) cur.why_us = body.why_us;
      state.slide_edits[catId] = cur;
    }

    await writeState(state);

    res.status(200).json({
      status: 'ok',
      success: true,
      storage_mode: getStorageMode(),
      message: 'บันทึกการแก้ไขเรียบร้อยแล้ว'
    });
  } catch (err) {
    res.status(500).json({
      status: 'error',
      success: false,
      message: err.message || 'บันทึกการแก้ไขไม่สำเร็จ'
    });
  }
};
