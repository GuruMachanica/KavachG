const express = require('express');
const router = express.Router();
const {
  getIncidentStats,
  getIncidentsBySector,
  getIncidentsByTime
} = require('../controllers/statsController');
const { protect } = require('../middleware/authMiddleware');

// GET overall statistics
router.get('/', protect, getIncidentStats);

// GET incidents by sector
router.get('/by-sector', protect, getIncidentsBySector);

// GET incidents by time
router.get('/by-time', protect, getIncidentsByTime);

module.exports = router; 