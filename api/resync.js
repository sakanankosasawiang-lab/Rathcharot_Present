const { requireAdmin } = require('./_lib/auth');
const { getMergedCatalog } = require('./_lib/storage');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') {
    res.status(405).json({ status: 'error', success: false, message: 'Method not allowed' });
    return;
  }
  if (!requireAdmin(req, res)) return;

  try {
    const merged = await getMergedCatalog();
    const total = merged.categories.reduce((acc, c) => acc + (c.images ? c.images.length : 0), 0);
    res.status(200).json({
      status: 'ok',
      success: true,
      total_photos: total,
      storage_mode: merged.storage_mode,
      message: `ซิงค์ข้อมูลแคตตาล็อกเรียบร้อย (${total} ภาพ)`
    });
  } catch (err) {
    res.status(500).json({
      status: 'error',
      success: false,
      message: err.message || 'ไม่สามารถซิงค์ข้อมูลได้'
    });
  }
};
