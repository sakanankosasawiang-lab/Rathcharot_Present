const handlers = {
  'login': require('./login'),
  'auth-check': require('./auth-check'),
  'catalog-data': require('./catalog-data'),
  'upload-photo': require('./upload-photo'),
  'delete-photo': require('./delete-photo'),
  'deleted-photos': require('./deleted-photos'),
  'restore-photo': require('./restore-photo'),
  'save-slide': require('./save-slide'),
  'resync': require('./resync')
};

module.exports = async function handler(req, res) {
  const urlPath = (req.url || '').split('?')[0];
  let route = (req.query && req.query.route) || urlPath.replace(/^\/api\//, '').replace(/\/+$/, '');
  const fn = handlers[route];
  if (!fn) {
    res.status(404).json({ status: 'error', success: false, message: `Unknown API route: ${route}` });
    return;
  }
  return fn(req, res);
};
