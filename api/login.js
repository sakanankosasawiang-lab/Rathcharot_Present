const { checkCredentials, signToken, setAuthCookie, parseBody } = require('./_lib/auth');
const { getStorageMode } = require('./_lib/storage');

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

  const body = parseBody(req);
  const username = body.username || '';
  const password = body.password || '';

  if (!checkCredentials(username, password)) {
    res.status(401).json({
      status: 'error',
      success: false,
      message: 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'
    });
    return;
  }

  const token = signToken({ user: username.trim(), role: 'admin' });
  setAuthCookie(res, token);

  res.status(200).json({
    status: 'ok',
    success: true,
    token,
    storage_mode: getStorageMode(),
    message: 'เข้าสู่ระบบสำเร็จ'
  });
};
