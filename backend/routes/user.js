const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const { validateUpdateProfile } = require('../middleware/validator');
const { protect, authorize } = require('../middleware/authMiddleware');

// Semua route memerlukan authentication
router.use(protect);

// Profile routes
router.get('/profile', userController.getUserProfile);
router.put('/profile', validateUpdateProfile, userController.updateUserProfile);
router.put('/change-password', userController.changePassword);

// Progress routes
router.get('/progress', userController.getUserProgress);
router.post('/pretest', userController.updatePretestScore);
router.post('/practice', userController.addPracticeScore);

// Teacher routes
router.get('/students', authorize('teacher', 'admin'), userController.getAllStudents);

module.exports = router;