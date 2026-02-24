const { Incident, User } = require('../models');
const { Op } = require('sequelize');

// @desc    Get all incidents
// @route   GET /api/incidents
// @access  Private
const getIncidents = async (req, res) => {
  try {
    const { type, severity, sector, status, from, to, limit = 20, page = 1 } = req.query;
    
    // Build query object
    const where = {};
    
    if (type) where.incident_type = type;
    if (severity) where.severity = severity;
    if (sector) where.sector = sector;
    if (status) where.status = status;
    
    // Date range
    if (from || to) {
      where.timestamp = {};
      if (from) where.timestamp[Op.gte] = new Date(from);
      if (to) where.timestamp[Op.lte] = new Date(to);
    }
    
    // Pagination
    const offset = (parseInt(page) - 1) * parseInt(limit);
    
    const { count, rows: incidents } = await Incident.findAndCountAll({
      where,
      order: [['timestamp', 'DESC']],
      limit: parseInt(limit),
      offset,
      include: [
        {
          model: User,
          as: 'resolved_by',
          attributes: ['id', 'name', 'email']
        }
      ]
    });
    
    res.status(200).json({
      success: true,
      count: incidents.length,
      total: count,
      page: parseInt(page),
      pages: Math.ceil(count / parseInt(limit)),
      data: incidents
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};

// @desc    Get incident by ID
// @route   GET /api/incidents/:id
// @access  Private
const getIncidentById = async (req, res) => {
  try {
    const incident = await Incident.findByPk(req.params.id, {
      include: [
        {
          model: User,
          as: 'resolved_by',
          attributes: ['id', 'name', 'email']
        }
      ]
    });
    
    if (!incident) {
      return res.status(404).json({
        success: false,
        message: 'Incident not found'
      });
    }
    
    res.status(200).json({
      success: true,
      data: incident
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};

// @desc    Create a new incident
// @route   POST /api/incidents
// @access  Private
const createIncident = async (req, res) => {
  try {
    const incident = await Incident.create(req.body);
    
    res.status(201).json({
      success: true,
      data: incident
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};

// @desc    Update incident status
// @route   PUT /api/incidents/:id
// @access  Private
const updateIncident = async (req, res) => {
  try {
    const incident = await Incident.findByPk(req.params.id);
    
    if (!incident) {
      return res.status(404).json({
        success: false,
        message: 'Incident not found'
      });
    }
    
    // If updating status to resolved, add resolution info
    if (req.body.status === 'resolved' && incident.status !== 'resolved') {
      req.body.resolution_time = new Date();
      if (req.user) {
        req.body.resolvedById = req.user.id;
      }
    }
    
    await incident.update(req.body);
    
    // Get updated incident with related user data
    const updatedIncident = await Incident.findByPk(req.params.id, {
      include: [
        {
          model: User,
          as: 'resolved_by',
          attributes: ['id', 'name', 'email']
        }
      ]
    });
    
    res.status(200).json({
      success: true,
      data: updatedIncident
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};

// @desc    Delete incident
// @route   DELETE /api/incidents/:id
// @access  Private/Admin
const deleteIncident = async (req, res) => {
  try {
    const incident = await Incident.findByPk(req.params.id);
    
    if (!incident) {
      return res.status(404).json({
        success: false,
        message: 'Incident not found'
      });
    }
    
    await incident.destroy();
    
    res.status(200).json({
      success: true,
      message: 'Incident removed'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};

module.exports = {
  getIncidents,
  getIncidentById,
  createIncident,
  updateIncident,
  deleteIncident
}; 