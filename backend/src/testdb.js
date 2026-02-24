const mongoose = require('mongoose');
const User = require('./models/userModel');
const Incident = require('./models/incidentModel');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/safety_monitoring';

async function testDB() {
  try {
    // Connect to MongoDB
    console.log('Attempting to connect to MongoDB...');
    await mongoose.connect(MONGODB_URI);
    console.log('Connected to MongoDB successfully!');

    // Test creating a user
    const testUser = {
      name: 'Test User',
      email: 'test@example.com',
      password: 'password123',
      role: 'admin'
    };

    // Check if user already exists
    const existingUser = await User.findOne({ email: testUser.email });
    if (existingUser) {
      console.log('Test user already exists:', existingUser);
    } else {
      // Create a new user
      const newUser = await User.create(testUser);
      console.log('Created test user successfully:', newUser);
    }

    // Test creating an incident
    const testIncident = {
      incident_type: 'fire',
      severity: 'high',
      confidence_score: 0.85,
      sector: 'sector-1'
    };

    const newIncident = await Incident.create(testIncident);
    console.log('Created test incident successfully:', newIncident);

    // Test querying incidents
    const incidents = await Incident.find().limit(5);
    console.log(`Found ${incidents.length} incidents in database.`);
    if (incidents.length > 0) {
      console.log('Sample incident:', incidents[0]);
    }

    console.log('Database tests completed successfully!');
  } catch (error) {
    console.error('Database test failed:', error);
  } finally {
    // Close the connection
    await mongoose.connection.close();
    console.log('MongoDB connection closed.');
  }
}

// Run the test
testDB(); 