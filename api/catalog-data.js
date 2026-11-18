const { getMergedCatalog } = require('./_lib/storage');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'GET') {
    res.status(405).json({ status: 'error', message: 'Method not allowed' });
    return;
  }
  try {
    const merged = await getMergedCatalog();
    res.status(200).json({
      status: 'ok',
      ...merged
    });
  } catch (err) {
    res.status(500).json({
      status: 'error',
      message: err.message || 'ไม่สามารถโหลดข้อมูลแคตตาล็อกได้'
    });
  }
};
