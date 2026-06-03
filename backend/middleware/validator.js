const { body, validationResult } = require('express-validator');

// Middleware untuk handle validation errors
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      message: 'Validation error',
      errors: errors.array()
    });
  }
  next();
};

// Validation rules untuk register
const validateRegister = [
  body('name')
    .trim()
    .notEmpty().withMessage('Nama tidak boleh kosong')
    .isLength({ min: 3 }).withMessage('Nama minimal 3 karakter')
    .isLength({ max: 50 }).withMessage('Nama maksimal 50 karakter'),
  body('email')
    .trim()
    .notEmpty().withMessage('Email tidak boleh kosong')
    .isEmail().withMessage('Format email tidak valid')
    .normalizeEmail(),
  body('password')
    .notEmpty().withMessage('Password tidak boleh kosong')
    .isLength({ min: 6 }).withMessage('Password minimal 6 karakter')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/).withMessage('Password harus mengandung huruf besar, huruf kecil, dan angka'),
  body('role')
    .notEmpty().withMessage('Role tidak boleh kosong')
    .isIn(['student', 'teacher']).withMessage('Role harus student atau teacher'),
  handleValidationErrors
];

// Validation rules untuk login
const validateLogin = [
  body('email')
    .trim()
    .notEmpty().withMessage('Email tidak boleh kosong')
    .isEmail().withMessage('Format email tidak valid')
    .normalizeEmail(),
  body('password')
    .notEmpty().withMessage('Password tidak boleh kosong'),
  handleValidationErrors
];

// Validation rules untuk update profile
const validateUpdateProfile = [
  body('name')
    .optional()
    .trim()
    .isLength({ min: 3 }).withMessage('Nama minimal 3 karakter')
    .isLength({ max: 50 }).withMessage('Nama maksimal 50 karakter'),
  body('phone')
    .optional()
    .trim()
    .isMobilePhone('id-ID').withMessage('Format nomor telepon tidak valid'),
  handleValidationErrors
];

module.exports = {
  validateRegister,
  validateLogin,
  validateUpdateProfile,
  handleValidationErrors
};