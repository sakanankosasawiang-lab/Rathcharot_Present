const { requireAdmin, parseBody } = require('./_lib/auth');
const { readState, writeState, loadBaseCatalogCategories, deleteBlobIfPresent, getStorageMode } = require('./_lib/storage');

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
    const catId = String(body.category_id || '').trim();
    const filename = String(body.filename || '').trim();
    const permanent = !!body.permanent;

    if (!catId || !filename) {
      res.status(400).json({ status: 'error', success: false, message: 'ข้อมูลไม่ครบ (category_id, filename)' });
      return;
    }

    const state = await readState();
    const addedIdx = (state.added_photos || []).findIndex(
      p => p.catId === catId && p.filename === filename
    );

    let removedRecord = null;
    if (addedIdx >= 0) {
      removedRecord = state.added_photos.splice(addedIdx, 1)[0];
      if (permanent && removedRecord.blob_url) {
        await deleteBlobIfPresent(removedRecord.blob_url);
      }
    }

    if (!permanent) {
      const baseCats = loadBaseCatalogCategories();
      const baseCat = baseCats.find(c => c.id === catId);
      const baseImg = baseCat ? (baseCat.images || []).find(im => im.filename === filename) : null;

      const alreadyTrashed = (state.deleted_photos || []).some(
        d => d.catId === catId && d.filename === filename
      );
      if (!alreadyTrashed) {
        state.deleted_photos = state.deleted_photos || [];
        state.deleted_photos.push({
          catId,
          category_id: catId,
          folder: baseCat ? baseCat.folder : catId,
          filename,
          rel_path: removedRecord ? removedRecord.rel_path : (baseImg ? baseImg.rel_path : ''),
          encoded_path: removedRecord ? removedRecord.encoded_path : (baseImg ? baseImg.encoded_path : ''),
          blob_url: removedRecord ? (removedRecord.blob_url || '') : '',
          is_custom: !!removedRecord,
          deleted_at: new Date().toISOString()
        });
      }
    }

    // Clear cover hero if it pointed to deleted image
    if (state.cover_heroes && state.cover_heroes[catId]) {
      const curHero = state.cover_heroes[catId];
      if (
        (removedRecord && curHero === removedRecord.encoded_path) ||
        curHero.endsWith('/' + filename) ||
        curHero.endsWith(encodeURIComponent(filename))
      ) {
        delete state.cover_heroes[catId];
      }
    }

    await writeState(state);

    res.status(200).json({
      status: 'ok',
      success: true,
      storage_mode: getStorageMode(),
      message: `ลบภาพ "${filename}" เรียบร้อยแล้ว`
    });
  } catch (err) {
    res.status(500).json({
      status: 'error',
      success: false,
      message: err.message || 'ลบภาพไม่สำเร็จ'
    });
  }
};
