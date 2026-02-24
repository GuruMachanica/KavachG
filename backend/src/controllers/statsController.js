const Incident = require('../models/incidentModel');

// @desc    Get incident statistics
// @route   GET /api/stats
// @access  Private
const getIncidentStats = async (req, res) => {
  try {
    // Filter params
    const { from, to, sector } = req.query;
    
    // Build query object
    const query = {};
    
    if (sector) query.sector = sector;
    
    // Date range
    if (from || to) {
      query.timestamp = {};
      if (from) query.timestamp.$gte = new Date(from);
      if (to) query.timestamp.$lte = new Date(to);
    }
    
    // Get total counts by type
    const totalIncidents = await Incident.countDocuments(query);
    const fireIncidents = await Incident.countDocuments({ ...query, incident_type: 'fire' });
    const fallIncidents = await Incident.countDocuments({ ...query, incident_type: 'fall' });
    const ppeIncidents = await Incident.countDocuments({ ...query, incident_type: 'ppe' });
    const otherIncidents = await Incident.countDocuments({ ...query, incident_type: 'other' });
    
    // Get severity counts
    const criticalIncidents = await Incident.countDocuments({ ...query, severity: 'critical' });
    const highIncidents = await Incident.countDocuments({ ...query, severity: 'high' });
    const mediumIncidents = await Incident.countDocuments({ ...query, severity: 'medium' });
    const lowIncidents = await Incident.countDocuments({ ...query, severity: 'low' });
    
    // Get status counts
    const detectedIncidents = await Incident.countDocuments({ ...query, status: 'detected' });
    const acknowledgedIncidents = await Incident.countDocuments({ ...query, status: 'acknowledged' });
    const resolvedIncidents = await Incident.countDocuments({ ...query, status: 'resolved' });
    const falseAlarmIncidents = await Incident.countDocuments({ ...query, status: 'false_alarm' });
    
    // Calculate percentages
    const typePercentage = {
      fire: totalIncidents > 0 ? (fireIncidents / totalIncidents) * 100 : 0,
      fall: totalIncidents > 0 ? (fallIncidents / totalIncidents) * 100 : 0,
      ppe: totalIncidents > 0 ? (ppeIncidents / totalIncidents) * 100 : 0,
      other: totalIncidents > 0 ? (otherIncidents / totalIncidents) * 100 : 0
    };
    
    const severityPercentage = {
      critical: totalIncidents > 0 ? (criticalIncidents / totalIncidents) * 100 : 0,
      high: totalIncidents > 0 ? (highIncidents / totalIncidents) * 100 : 0,
      medium: totalIncidents > 0 ? (mediumIncidents / totalIncidents) * 100 : 0,
      low: totalIncidents > 0 ? (lowIncidents / totalIncidents) * 100 : 0
    };
    
    // Preparing response
    const stats = {
      totalIncidents,
      byType: {
        fire: fireIncidents,
        fall: fallIncidents,
        ppe: ppeIncidents,
        other: otherIncidents,
        percentage: typePercentage
      },
      bySeverity: {
        critical: criticalIncidents,
        high: highIncidents,
        medium: mediumIncidents,
        low: lowIncidents,
        percentage: severityPercentage
      },
      byStatus: {
        detected: detectedIncidents,
        acknowledged: acknowledgedIncidents,
        resolved: resolvedIncidents,
        false_alarm: falseAlarmIncidents
      }
    };
    
    res.status(200).json({
      success: true,
      data: stats
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};

// @desc    Get incidents by sector
// @route   GET /api/stats/by-sector
// @access  Private
const getIncidentsBySector = async (req, res) => {
  try {
    const { from, to } = req.query;
    
    // Build query object
    const query = {};
    
    // Date range
    if (from || to) {
      query.timestamp = {};
      if (from) query.timestamp.$gte = new Date(from);
      if (to) query.timestamp.$lte = new Date(to);
    }
    
    // Aggregate by sector
    const sectorStats = await Incident.aggregate([
      { $match: query },
      { $group: {
          _id: '$sector',
          count: { $sum: 1 },
          fire: { $sum: { $cond: [{ $eq: ['$incident_type', 'fire'] }, 1, 0] } },
          fall: { $sum: { $cond: [{ $eq: ['$incident_type', 'fall'] }, 1, 0] } },
          ppe: { $sum: { $cond: [{ $eq: ['$incident_type', 'ppe'] }, 1, 0] } },
          other: { $sum: { $cond: [{ $eq: ['$incident_type', 'other'] }, 1, 0] } },
          critical: { $sum: { $cond: [{ $eq: ['$severity', 'critical'] }, 1, 0] } },
          high: { $sum: { $cond: [{ $eq: ['$severity', 'high'] }, 1, 0] } },
          medium: { $sum: { $cond: [{ $eq: ['$severity', 'medium'] }, 1, 0] } },
          low: { $sum: { $cond: [{ $eq: ['$severity', 'low'] }, 1, 0] } }
        }
      },
      { $sort: { count: -1 } }
    ]);
    
    res.status(200).json({
      success: true,
      count: sectorStats.length,
      data: sectorStats
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};

// @desc    Get incidents by time
// @route   GET /api/stats/by-time
// @access  Private
const getIncidentsByTime = async (req, res) => {
  try {
    const { interval = 'day', from, to, sector } = req.query;
    
    // Build match query
    const match = {};
    if (sector) match.sector = sector;
    
    // Date range
    if (from || to) {
      match.timestamp = {};
      if (from) match.timestamp.$gte = new Date(from);
      if (to) match.timestamp.$lte = new Date(to);
    }
    
    // Set time group format based on interval
    let groupFormat;
    if (interval === 'hour') {
      groupFormat = { year: { $year: '$timestamp' }, month: { $month: '$timestamp' }, day: { $dayOfMonth: '$timestamp' }, hour: { $hour: '$timestamp' } };
    } else if (interval === 'day') {
      groupFormat = { year: { $year: '$timestamp' }, month: { $month: '$timestamp' }, day: { $dayOfMonth: '$timestamp' } };
    } else if (interval === 'week') {
      groupFormat = { year: { $year: '$timestamp' }, week: { $week: '$timestamp' } };
    } else if (interval === 'month') {
      groupFormat = { year: { $year: '$timestamp' }, month: { $month: '$timestamp' } };
    } else {
      return res.status(400).json({
        success: false,
        message: 'Invalid interval parameter'
      });
    }
    
    // Aggregate by time interval
    const timeStats = await Incident.aggregate([
      { $match: match },
      { $group: {
          _id: groupFormat,
          count: { $sum: 1 },
          fire: { $sum: { $cond: [{ $eq: ['$incident_type', 'fire'] }, 1, 0] } },
          fall: { $sum: { $cond: [{ $eq: ['$incident_type', 'fall'] }, 1, 0] } },
          ppe: { $sum: { $cond: [{ $eq: ['$incident_type', 'ppe'] }, 1, 0] } },
          other: { $sum: { $cond: [{ $eq: ['$incident_type', 'other'] }, 1, 0] } }
        }
      },
      { $sort: { '_id.year': 1, '_id.month': 1, '_id.day': 1, '_id.hour': 1, '_id.week': 1 } }
    ]);
    
    // Add formatted date to each result
    const formattedTimeStats = timeStats.map(stat => {
      let formattedDate;
      
      if (interval === 'hour') {
        formattedDate = new Date(stat._id.year, stat._id.month - 1, stat._id.day, stat._id.hour);
      } else if (interval === 'day') {
        formattedDate = new Date(stat._id.year, stat._id.month - 1, stat._id.day);
      } else if (interval === 'week') {
        // Create a date for the first day of the year
        const firstDay = new Date(stat._id.year, 0, 1);
        // Add the week number (weeks start from 0)
        formattedDate = new Date(firstDay.setDate(firstDay.getDate() + (stat._id.week * 7)));
      } else if (interval === 'month') {
        formattedDate = new Date(stat._id.year, stat._id.month - 1, 1);
      }
      
      return {
        ...stat,
        date: formattedDate
      };
    });
    
    res.status(200).json({
      success: true,
      count: formattedTimeStats.length,
      interval,
      data: formattedTimeStats
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
  getIncidentStats,
  getIncidentsBySector,
  getIncidentsByTime
}; 