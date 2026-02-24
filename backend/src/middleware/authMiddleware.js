const jwt = require('jsonwebtoken');
const User = require('../models/userModel');

// Protect routes - verify user token
const protect = async (req, res, next) => {
  let token;
  
  // Check if token exists in the Authorization header
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    try {
      // Get token from header
      token = req.headers.authorization.split(' ')[1];
      
      // Verify token
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'kavachg_secret');
      
      // Get user from the token (exclude password)
      req.user = await User.findById(decoded.id).select('-password');
      
      if (!req.user) {
        return res.status(401).json({
          success: false,
          message: 'Not authorized, user not found'
        });
      }
      
      next();
    } catch (error) {
      res.status(401).json({
        success: false,
        message: 'Not authorized, token failed',
        error: error.message
      });
    }
  }

  if (!token) {
    res.status(401).json({
      success: false,
      message: 'Not authorized, no token'
    });
  }
};

// Admin middleware - verify user is admin
const admin = (req, res, next) => {
  if (req.user && req.user.role === 'admin') {
    next();
  } else {
    res.status(403).json({
      success: false,
      message: 'Not authorized as an admin'
    });
  }
};

// Supervisor middleware - verify user is supervisor or admin
const supervisor = (req, res, next) => {
  if (req.user && (req.user.role === 'supervisor' || req.user.role === 'admin')) {
    next();
  } else {
    res.status(403).json({
      success: false,
      message: 'Not authorized as a supervisor'
    });
  }
};

// Operator middleware - verify user is operator, supervisor or admin
const operator = (req, res, next) => {
  if (req.user && 
     (req.user.role === 'operator' || req.user.role === 'supervisor' || req.user.role === 'admin')) {
    next();
  } else {
    res.status(403).json({
      success: false,
      message: 'Not authorized as an operator'
    });
  }
};

module.exports = { protect, admin, supervisor, operator }; 