const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const { validateRegister, validateLogin } = require('../middleware/validator');
const { protect, rateLimit } = require('../middleware/authMiddleware');

// Rate limiting untuk auth routes
router.use(rateLimit(10, 15 * 60 * 1000)); // 10 requests per 15 minutes

// Public routes
router.post('/register', validateRegister, authController.register);
router.post('/login', validateLogin, authController.login);
router.get('/verify-email/:token', authController.verifyEmail);

// Private routes
router.get('/me', protect, authController.getMe);
router.post('/logout', protect, authController.logout);
router.post('/refresh-token', protect, authController.refreshToken);

module.exports = router;