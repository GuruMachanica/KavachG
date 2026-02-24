const express = require('express');
const router = express.Router();
const { 
  getIncidents, 
  getIncidentById, 
  createIncident, 
  updateIncident, 
  deleteIncident 
} = require('../controllers/incidentController');
const { protect, admin, supervisor, operator } = require('../middleware/authMiddleware');

// GET all incidents / POST new incident
router.route('/')
  .get(protect, getIncidents)
  .post(createIncident);

// GET/PUT/DELETE incident by ID
router.route('/:id')
  .get(protect, getIncidentById)
  .put(protect, operator, updateIncident)
  .delete(protect, admin, deleteIncident);

module.exports = router; 