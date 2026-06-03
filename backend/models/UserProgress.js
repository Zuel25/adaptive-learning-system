const mongoose = require('mongoose');

const userProgressSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      unique: true
    },
    pretestScore: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    pretestCompleted: {
      type: Boolean,
      default: false
    },
    pretestDate: {
      type: Date,
      default: null
    },
    level: {
      type: String,
      enum: ['Dasar', 'Menengah', 'Mahir'],
      default: 'Dasar'
    },
    materialsCompleted: {
      type: [String],
      default: []
    },
    practiceScores: {
      type: [
        {
          materialId: String,
          score: Number,
          completedAt: Date
        }
      ],
      default: []
    },
    averagePracticeScore: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    totalMaterialsToStudy: {
      type: Number,
      default: 15
    },
    progress: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    streakDays: {
      type: Number,
      default: 0
    },
    lastActivityDate: {
      type: Date,
      default: null
    },
    totalStudyTime: {
      type: Number,
      default: 0
    },
    badges: {
      type: [String],
      default: []
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

userProgressSchema.index({ userId: 1 });
userProgressSchema.index({ level: 1 });
userProgressSchema.index({ progress: -1 });

userProgressSchema.methods.calculateProgress = function() {
  const completedCount = this.materialsCompleted.length;
  const total = this.totalMaterialsToStudy;
  this.progress = Math.round((completedCount / total) * 100);
  return this.progress;
};

userProgressSchema.methods.calculateAverageScore = function() {
  if (this.practiceScores.length === 0) {
    this.averagePracticeScore = 0;
    return 0;
  }
  const sum = this.practiceScores.reduce((acc, item) => acc + item.score, 0);
  this.averagePracticeScore = Math.round(sum / this.practiceScores.length);
  return this.averagePracticeScore;
};

userProgressSchema.methods.updateLevel = function() {
  if (this.pretestScore < 50) {
    this.level = 'Dasar';
  } else if (this.pretestScore < 75) {
    this.level = 'Menengah';
  } else {
    this.level = 'Mahir';
  }
  return this.level;
};

userProgressSchema.pre('save', function(next) {
  this.calculateProgress();
  this.calculateAverageScore();
  next();
});

module.exports = mongoose.model('UserProgress', userProgressSchema);