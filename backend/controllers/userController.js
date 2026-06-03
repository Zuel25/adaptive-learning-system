const User = require('../models/User');
const UserProgress = require('../models/UserProgress');

// @desc    Get user profile
// @route   GET /api/users/profile
// @access  Private
const getUserProfile = async (req, res, next) => {
  try {
    const user = await User.findById(req.user._id).populate('userProgress');
    const progress = await UserProgress.findOne({ userId: req.user._id });

    res.status(200).json({
      success: true,
      user,
      progress
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Update user profile
// @route   PUT /api/users/profile
// @access  Private
const updateUserProfile = async (req, res, next) => {
  try {
    const { name, phone } = req.body;

    const user = await User.findByIdAndUpdate(
      req.user._id,
      { name, phone, updatedAt: Date.now() },
      { new: true, runValidators: true }
    );

    res.status(200).json({
      success: true,
      message: 'Profil berhasil diupdate',
      user
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Change password
// @route   PUT /api/users/change-password
// @access  Private
const changePassword = async (req, res, next) => {
  try {
    const { oldPassword, newPassword, confirmPassword } = req.body;

    // Validasi input
    if (!oldPassword || !newPassword || !confirmPassword) {
      return res.status(400).json({
        success: false,
        message: 'Semua field wajib diisi'
      });
    }

    if (newPassword !== confirmPassword) {
      return res.status(400).json({
        success: false,
        message: 'Password baru tidak cocok'
      });
    }

    const user = await User.findById(req.user._id).select('+password');

    // Validasi old password
    const isPasswordValid = await user.comparePassword(oldPassword);
    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        message: 'Password lama tidak sesuai'
      });
    }

    // Update password
    user.password = newPassword;
    await user.save();

    res.status(200).json({
      success: true,
      message: 'Password berhasil diubah'
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Get user progress
// @route   GET /api/users/progress
// @access  Private
const getUserProgress = async (req, res, next) => {
  try {
    const progress = await UserProgress.findOne({ userId: req.user._id });

    if (!progress) {
      return res.status(404).json({
        success: false,
        message: 'Progress data tidak ditemukan'
      });
    }

    res.status(200).json({
      success: true,
      progress
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Update pretest score
// @route   POST /api/users/pretest
// @access  Private
const updatePretestScore = async (req, res, next) => {
  try {
    const { score } = req.body;

    if (score === undefined || score < 0 || score > 100) {
      return res.status(400).json({
        success: false,
        message: 'Score harus antara 0-100'
      });
    }

    let progress = await UserProgress.findOne({ userId: req.user._id });

    if (!progress) {
      progress = await UserProgress.create({ userId: req.user._id });
    }

    progress.pretestScore = score;
    progress.pretestCompleted = true;
    progress.pretestDate = new Date();
    progress.updateLevel();

    await progress.save();

    res.status(200).json({
      success: true,
      message: 'Pretest score berhasil diupdate',
      progress
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Add practice score
// @route   POST /api/users/practice
// @access  Private
const addPracticeScore = async (req, res, next) => {
  try {
    const { materialId, score } = req.body;

    if (!materialId || score === undefined || score < 0 || score > 100) {
      return res.status(400).json({
        success: false,
        message: 'Material ID dan score (0-100) wajib diisi'
      });
    }

    let progress = await UserProgress.findOne({ userId: req.user._id });

    if (!progress) {
      progress = await UserProgress.create({ userId: req.user._id });
    }

    // Tambah practice score
    progress.practiceScores.push({
      materialId,
      score,
      completedAt: new Date()
    });

    // Tandai material sebagai completed
    if (!progress.materialsCompleted.includes(materialId)) {
      progress.materialsCompleted.push(materialId);
    }

    progress.lastActivityDate = new Date();
    await progress.save();

    res.status(200).json({
      success: true,
      message: 'Practice score berhasil disimpan',
      progress
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Get all students (for teacher)
// @route   GET /api/users/students
// @access  Private (Teacher only)
const getAllStudents = async (req, res, next) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    const students = await User.find({ role: 'student' })
      .skip(skip)
      .limit(limit)
      .select('-password -verificationToken');

    const total = await User.countDocuments({ role: 'student' });

    const studentProgress = await Promise.all(
      students.map(async (student) => {
        const progress = await UserProgress.findOne({ userId: student._id });
        return { ...student.toJSON(), progress };
      })
    );

    res.status(200).json({
      success: true,
      total,
      page,
      pages: Math.ceil(total / limit),
      students: studentProgress
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getUserProfile,
  updateUserProfile,
  changePassword,
  getUserProgress,
  updatePretestScore,
  addPracticeScore,
  getAllStudents
};