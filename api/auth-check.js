const { extractToken, verifyToken } = require('./_lib/auth');
const { getStorageMode } = require('./_lib/storage');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  const token = extractToken(req);
  const decoded = verifyToken(token);
  res.status(200).json({
    authenticated: !!decoded,
    user: decoded ? decoded.user : null,
    storage_mode: getStorageMode()
  });
};
