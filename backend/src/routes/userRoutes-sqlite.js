const express = require('express');
const router = express.Router();
const {
  loginUser,
  registerUser,
  getUsers,
  getUserById,
  updateUser,
  deleteUser,
  getUserProfile
} = require('../controllers/userController-sqlite');
const { protect, admin } = require('../middleware/authMiddleware-sqlite');

// Authentication
router.post('/login', loginUser);

// User profile
router.route('/profile')
  .get(protect, getUserProfile);

// Admin: manage users
router.route('/')
  .get(protect, admin, getUsers)
  .post(protect, admin, registerUser);

// Admin: manage specific user
router.route('/:id')
  .get(protect, admin, getUserById)
  .put(protect, admin, updateUser)
  .delete(protect, admin, deleteUser);

module.exports = router; 