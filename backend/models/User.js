const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, 'Nama lengkap wajib diisi'],
      trim: true,
      minlength: [3, 'Nama minimal 3 karakter'],
      maxlength: [50, 'Nama maksimal 50 karakter']
    },
    email: {
      type: String,
      required: [true, 'Email wajib diisi'],
      unique: true,
      lowercase: true,
      match: [/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/, 'Format email tidak valid']
    },
    password: {
      type: String,
      required: [true, 'Password wajib diisi'],
      minlength: [6, 'Password minimal 6 karakter'],
      select: false // Jangan return password saat query
    },
    role: {
      type: String,
      enum: {
        values: ['student', 'teacher', 'admin'],
        message: 'Role harus student, teacher, atau admin'
      },
      default: 'student'
    },
    profilePicture: {
      type: String,
      default: null
    },
    phone: {
      type: String,
      default: null
    },
    verified: {
      type: Boolean,
      default: false
    },
    verificationToken: {
      type: String,
      default: null,
      select: false
    },
    lastLogin: {
      type: Date,
      default: null
    },
    isActive: {
      type: Boolean,
      default: true
    },
    createdAt: {
      type: Date,
      default: Date.now
    },
    updatedAt: {
      type: Date,
      default: Date.now
    }
  },
  {
    timestamps: true
  }
);

// Index untuk performa query
userSchema.index({ email: 1 });
userSchema.index({ createdAt: -1 });

// Hash password sebelum save
userSchema.pre('save', async function(next) {
  // Hanya hash jika password dimodifikasi
  if (!this.isModified('password')) {
    return next();
  }

  try {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Method untuk compare password
userSchema.methods.comparePassword = async function(enteredPassword) {
  return await bcrypt.compare(enteredPassword, this.password);
};

// Method untuk mendapatkan public profile (tanpa password sensitive)
userSchema.methods.toJSON = function() {
  const obj = this.toObject();
  delete obj.password;
  delete obj.verificationToken;
  return obj;
};

// Prevent duplikat error middleware
userSchema.post('save', function(error, doc, next) {
  if (error.name === 'MongoError' && error.code === 11000) {
    next(new Error(`Email sudah terdaftar di sistem`));
  } else {
    next(error);
  }
});

module.exports = mongoose.model('User', userSchema);
