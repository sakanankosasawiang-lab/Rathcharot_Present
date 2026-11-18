const crypto = require('crypto');

const DEFAULT_USER = 'admin';
const DEFAULT_PASS = 'admin1234';
const DEFAULT_SECRET = 'rathcharot_catalog_jwt_secret_2026_v2';
const LEGACY_TOKEN = 'rathcharot_admin_token_2026_secured';

function getSecret() {
  return process.env.ADMIN_JWT_SECRET || DEFAULT_SECRET;
}

function signToken(payload) {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
  const body = Buffer.from(JSON.stringify({
    ...payload,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 7 // 7 days
  })).toString('base64url');
  const sig = crypto
    .createHmac('sha256', getSecret())
    .update(`${header}.${body}`)
    .digest('base64url');
  return `${header}.${body}.${sig}`;
}

function verifyToken(token) {
  if (!token || typeof token !== 'string') return null;
  if (token === LEGACY_TOKEN) return { user: DEFAULT_USER, legacy: true };
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  const [header, body, sig] = parts;
  const expected = crypto
    .createHmac('sha256', getSecret())
    .update(`${header}.${body}`)
    .digest('base64url');
  const sigBuf = Buffer.from(sig);
  const expBuf = Buffer.from(expected);
  if (sigBuf.length !== expBuf.length || !crypto.timingSafeEqual(sigBuf, expBuf)) {
    return null;
  }
  try {
    const data = JSON.parse(Buffer.from(body, 'base64url').toString('utf8'));
    if (data.exp && data.exp < Math.floor(Date.now() / 1000)) return null;
    return data;
  } catch {
    return null;
  }
}

function checkCredentials(username, password) {
  const expectedUser = (process.env.ADMIN_USERNAME || DEFAULT_USER).trim();
  const expectedPass = (process.env.ADMIN_PASSWORD || DEFAULT_PASS).trim();
  return String(username || '').trim() === expectedUser && String(password || '').trim() === expectedPass;
}

function extractToken(req) {
  const authHeader = req.headers.authorization || req.headers.Authorization || '';
  if (authHeader.startsWith('Bearer ')) {
    return authHeader.slice(7).trim();
  }
  const cookieHeader = req.headers.cookie || '';
  const match = cookieHeader.match(/(?:^|;\s*)rathcharot_admin_token=([^;]+)/);
  if (match) {
    return decodeURIComponent(match[1]);
  }
  return '';
}

function requireAdmin(req, res) {
  const token = extractToken(req);
  const decoded = verifyToken(token);
  if (!decoded) {
    res.status(401).json({
      status: 'error',
      success: false,
      message: 'กรุณาเข้าสู่ระบบ Admin ก่อนดำเนินการ'
    });
    return null;
  }
  return decoded;
}

function setAuthCookie(res, token) {
  const isProd = process.env.VERCEL === '1' || process.env.NODE_ENV === 'production';
  const parts = [
    `rathcharot_admin_token=${encodeURIComponent(token)}`,
    'Path=/',
    'HttpOnly',
    'SameSite=Lax',
    `Max-Age=${60 * 60 * 24 * 7}`
  ];
  if (isProd) parts.push('Secure');
  res.setHeader('Set-Cookie', parts.join('; '));
}

function parseBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') {
    try { return JSON.parse(req.body); } catch { return {}; }
  }
  return {};
}

module.exports = {
  signToken,
  verifyToken,
  checkCredentials,
  extractToken,
  requireAdmin,
  setAuthCookie,
  parseBody
};
