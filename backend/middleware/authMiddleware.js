const jwt = require('jsonwebtoken');
const User = require('../models/User');

// Middleware untuk verifikasi JWT token
const protect = async (req, res, next) => {
  let token;

  // Ambil token dari header
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1];
  }

  // Validasi token ada
  if (!token) {
    return res.status(401).json({
      success: false,
      message: 'Tidak ada token, akses ditolak'
    });
  }

  try {
    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Cari user
    req.user = await User.findById(decoded.userId);

    if (!req.user) {
      return res.status(404).json({
        success: false,
        message: 'User tidak ditemukan'
      });
    }

    if (!req.user.isActive) {
      return res.status(403).json({
        success: false,
        message: 'User akun tidak aktif'
      });
    }

    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Token sudah expired, silakan login ulang'
      });
    }
    return res.status(401).json({
      success: false,
      message: 'Token tidak valid'
    });
  }
};

// Middleware untuk verifikasi role
const authorize = (...roles) => {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: 'Anda tidak memiliki akses untuk resource ini'
      });
    }
    next();
  };
};

// Middleware untuk rate limiting (simple)
const rateLimitMap = new Map();

const rateLimit = (maxRequests = 100, windowMs = 15 * 60 * 1000) => {
  return (req, res, next) => {
    const ip = req.ip;
    const now = Date.now();
    const userRequests = rateLimitMap.get(ip) || [];
    
    // Hapus request yang sudah diluar window
    const recentRequests = userRequests.filter(time => now - time < windowMs);
    
    if (recentRequests.length >= maxRequests) {
      return res.status(429).json({
        success: false,
        message: 'Terlalu banyak request, silakan coba lagi nanti'
      });
    }
    
    recentRequests.push(now);
    rateLimitMap.set(ip, recentRequests);
    next();
  };
};

module.exports = {
  protect,
  authorize,
  rateLimit
};