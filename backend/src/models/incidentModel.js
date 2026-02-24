const mongoose = require('mongoose');

const incidentSchema = new mongoose.Schema(
  {
    timestamp: {
      type: Date,
      default: Date.now,
      required: true,
      index: true
    },
    incident_type: {
      type: String,
      enum: ['fire', 'fall', 'ppe', 'other'],
      required: true,
      index: true
    },
    severity: {
      type: String,
      enum: ['low', 'medium', 'high', 'critical'],
      required: true
    },
    confidence_score: {
      type: Number,
      required: true,
      min: 0,
      max: 1
    },
    sector: {
      type: String,
      required: true,
      index: true
    },
    image_path: {
      type: String
    },
    video_clip_path: {
      type: String
    },
    status: {
      type: String,
      enum: ['detected', 'acknowledged', 'resolved', 'false_alarm'],
      default: 'detected'
    },
    resolved_by: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    resolution_notes: {
      type: String
    },
    resolution_time: {
      type: Date
    },
    location: {
      type: {
        type: String,
        enum: ['Point'],
        default: 'Point'
      },
      coordinates: {
        type: [Number], // [longitude, latitude]
        default: [0, 0]
      }
    }
  },
  {
    timestamps: true
  }
);

// Define indexes
incidentSchema.index({ location: '2dsphere' });
incidentSchema.index({ timestamp: -1 });
incidentSchema.index({ incident_type: 1 });
incidentSchema.index({ sector: 1 });

const Incident = mongoose.model('Incident', incidentSchema);

module.exports = Incident; 