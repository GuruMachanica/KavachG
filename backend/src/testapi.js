const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

// Import routes and models
const incidentRoutes = require('./routes/incidentRoutes');
const userRoutes = require('./routes/userRoutes');
const statsRoutes = require('./routes/statsRoutes');
const User = require('./models/userModel');

// Create Express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Define routes
app.use('/api/incidents', incidentRoutes);
app.use('/api/users', userRoutes);
app.use('/api/stats', statsRoutes);

// Test routes
app.get('/api/test', (req, res) => {
  res.status(200).json({ message: 'API test endpoint is working' });
});

// Create a test admin user if none exists
app.post('/api/test/create-admin', async (req, res) => {
  try {
    // Check if admin exists
    const adminExists = await User.findOne({ role: 'admin' });
    
    if (adminExists) {
      return res.status(200).json({ 
        message: 'Admin user already exists',
        admin: {
          id: adminExists._id,
          name: adminExists.name,
          email: adminExists.email,
          role: adminExists.role
        } 
      });
    }
    
    // Create new admin
    const admin = await User.create({
      name: 'Admin User',
      email: 'admin@kavachg.com',
      password: 'admin123',
      role: 'admin'
    });
    
    res.status(201).json({
      message: 'Admin user created successfully',
      admin: {
        id: admin._id,
        name: admin.name,
        email: admin.email,
        role: admin.role
      }
    });
  } catch (error) {
    res.status(500).json({
      message: 'Error creating admin user',
      error: error.message
    });
  }
});

// Test route to create incident
app.post('/api/test/create-incident', async (req, res) => {
  try {
    const response = await fetch('http://localhost:5000/api/incidents', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        incident_type: 'fire',
        severity: 'high',
        confidence_score: 0.85,
        sector: 'sector-1'
      })
    });
    
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    res.status(500).json({
      message: 'Error creating test incident',
      error: error.message
    });
  }
});

// DB Connection
const PORT = 5500; // Use a different port for testing
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/safety_monitoring';

mongoose
  .connect(MONGODB_URI)
  .then(() => {
    console.log('Connected to MongoDB');
    app.listen(PORT, () => {
      console.log(`Test API server running on port ${PORT}`);
      console.log(`Access test endpoints at http://localhost:${PORT}/api/test`);
      console.log(`Create admin: http://localhost:${PORT}/api/test/create-admin`);
      console.log(`Create incident: http://localhost:${PORT}/api/test/create-incident`);
    });
  })
  .catch((err) => {
    console.error('MongoDB connection error:', err);
    process.exit(1);
  }); 