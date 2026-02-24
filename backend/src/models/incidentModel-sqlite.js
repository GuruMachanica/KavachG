const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');
const User = require('./userModel-sqlite');

// Define Incident model
const Incident = sequelize.define('Incident', {
  timestamp: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
    allowNull: false
  },
  incident_type: {
    type: DataTypes.ENUM('fire', 'fall', 'ppe', 'other'),
    allowNull: false
  },
  severity: {
    type: DataTypes.ENUM('low', 'medium', 'high', 'critical'),
    allowNull: false
  },
  confidence_score: {
    type: DataTypes.FLOAT,
    allowNull: false,
    validate: {
      min: 0,
      max: 1
    }
  },
  sector: {
    type: DataTypes.STRING,
    allowNull: false
  },
  image_path: {
    type: DataTypes.STRING,
    allowNull: true
  },
  video_clip_path: {
    type: DataTypes.STRING,
    allowNull: true
  },
  status: {
    type: DataTypes.ENUM('detected', 'acknowledged', 'resolved', 'false_alarm'),
    defaultValue: 'detected'
  },
  resolution_notes: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  resolution_time: {
    type: DataTypes.DATE,
    allowNull: true
  },
  location_lat: {
    type: DataTypes.FLOAT,
    allowNull: true
  },
  location_long: {
    type: DataTypes.FLOAT,
    allowNull: true
  }
}, {
  timestamps: true,
  indexes: [
    {
      fields: ['timestamp']
    },
    {
      fields: ['incident_type']
    },
    {
      fields: ['sector']
    },
    {
      fields: ['status']
    }
  ]
});

// Define relationships
Incident.belongsTo(User, { as: 'resolved_by', foreignKey: 'resolvedById' });

module.exports = Incident; 