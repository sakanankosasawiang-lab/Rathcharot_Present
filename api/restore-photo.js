const { requireAdmin, parseBody } = require('./_lib/auth');
const { readState, writeState, getStorageMode } = require('./_lib/storage');

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

    if (!catId || !filename) {
      res.status(400).json({ status: 'error', success: false, message: 'ข้อมูลไม่ครบ' });
      return;
    }

    const state = await readState();
    const idx = (state.deleted_photos || []).findIndex(
      d => (d.catId === catId || d.category_id === catId) && d.filename === filename
    );
    if (idx < 0) {
      res.status(404).json({ status: 'error', success: false, message: 'ไม่พบภาพในถังขยะ' });
      return;
    }

    const item = state.deleted_photos.splice(idx, 1)[0];
    if (item.is_custom && item.encoded_path) {
      state.added_photos = state.added_photos || [];
      state.added_photos.push({
        catId,
        filename: item.filename,
        rel_path: item.rel_path,
        encoded_path: item.encoded_path,
        blob_url: item.blob_url || '',
        uploaded_at: new Date().toISOString()
      });
    }

    await writeState(state);

    res.status(200).json({
      status: 'ok',
      success: true,
      storage_mode: getStorageMode(),
      message: `กู้คืนภาพ "${filename}" กลับเข้าหมวดเรียบร้อยแล้ว`
    });
  } catch (err) {
    res.status(500).json({ status: 'error', success: false, message: err.message || 'กู้คืนภาพไม่สำเร็จ' });
  }
};
