const Incident = require('../models/incidentModel');

// @desc    Get all incidents
// @route   GET /api/incidents
// @access  Private
const getIncidents = async (req, res) => {
  try {
    const { type, severity, sector, status, from, to, limit = 20, page = 1 } = req.query;
    
    // Build query object
    const query = {};
    
    if (type) query.incident_type = type;
    if (severity) query.severity = severity;
    if (sector) query.sector = sector;
    if (status) query.status = status;
    
    // Date range
    if (from || to) {
      query.timestamp = {};
      if (from) query.timestamp.$gte = new Date(from);
      if (to) query.timestamp.$lte = new Date(to);
    }
    
    // Pagination
    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    const incidents = await Incident.find(query)
      .sort({ timestamp: -1 })
      .limit(parseInt(limit))
      .skip(skip);
    
    const total = await Incident.countDocuments(query);
    
    res.status(200).json({
      success: true,
      count: incidents.length,
      total,
      page: parseInt(page),
      pages: Math.ceil(total / parseInt(limit)),
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
    const incident = await Incident.findById(req.params.id);
    
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
    const incident = await Incident.findById(req.params.id);
    
    if (!incident) {
      return res.status(404).json({
        success: false,
        message: 'Incident not found'
      });
    }
    
    // If updating status to resolved, add resolution info
    if (req.body.status === 'resolved' && incident.status !== 'resolved') {
      req.body.resolution_time = new Date();
      req.body.resolved_by = req.user._id; // From auth middleware
    }
    
    const updatedIncident = await Incident.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );
    
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
    const incident = await Incident.findById(req.params.id);
    
    if (!incident) {
      return res.status(404).json({
        success: false,
        message: 'Incident not found'
      });
    }
    
    await incident.remove();
    
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