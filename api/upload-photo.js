const { requireAdmin, parseBody } = require('./_lib/auth');
const { readState, writeState, storeUploadedImage, getStorageMode } = require('./_lib/storage');

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
    const dataBase64 = String(body.data_base64 || '');

    if (!catId || !filename || !dataBase64) {
      res.status(400).json({
        status: 'error',
        success: false,
        message: 'ข้อมูลไม่ครบ (ต้องการ category_id, filename และ data_base64)'
      });
      return;
    }

    const stored = await storeUploadedImage(catId, filename, dataBase64);
    const state = await readState();

    // Remove from deleted list if re-uploaded with same filename
    state.deleted_photos = (state.deleted_photos || []).filter(
      d => !(d.catId === catId && d.filename === stored.filename)
    );

    const record = {
      catId,
      filename: stored.filename,
      rel_path: stored.rel_path,
      encoded_path: stored.encoded_path,
      blob_url: stored.blob_url,
      uploaded_at: new Date().toISOString()
    };
    state.added_photos = (state.added_photos || []).filter(
      p => !(p.catId === catId && p.filename === stored.filename)
    );
    state.added_photos.push(record);
    await writeState(state);

    res.status(200).json({
      status: 'ok',
      success: true,
      storage_mode: getStorageMode(),
      image: {
        filename: stored.filename,
        rel_path: stored.rel_path,
        encoded_path: stored.encoded_path,
        is_custom: true
      },
      message: `อัปโหลดภาพ "${stored.filename}" เรียบร้อยแล้ว`
    });
  } catch (err) {
    res.status(500).json({
      status: 'error',
      success: false,
      message: err.message || 'อัปโหลดภาพไม่สำเร็จ'
    });
  }
};
