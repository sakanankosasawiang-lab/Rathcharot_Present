const { requireAdmin } = require('./_lib/auth');
const { readState, getStorageMode } = require('./_lib/storage');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'GET') {
    res.status(405).json({ status: 'error', message: 'Method not allowed' });
    return;
  }
  if (!requireAdmin(req, res)) return;

  try {
    const state = await readState();
    const deleted_photos = (state.deleted_photos || []).map(d => ({
      category_id: d.catId || d.category_id,
      folder: d.folder || '',
      filename: d.filename,
      deleted_path: d.encoded_path || d.rel_path || '',
      deleted_at: d.deleted_at || ''
    }));
    res.status(200).json({
      status: 'ok',
      deleted_photos,
      storage_mode: getStorageMode()
    });
  } catch (err) {
    res.status(500).json({ status: 'error', deleted_photos: [], message: err.message });
  }
};
