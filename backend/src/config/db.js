const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/safety_monitoring', {
      // Mongoose 6+ doesn't need these options anymore, they're now default
    });

    console.log(`MongoDB Connected: ${conn.connection.host}`);
    
    // Initialize indexes
    const incidentModel = require('../models/incidentModel');
    
    return conn;
  } catch (error) {
    console.error(`Error connecting to MongoDB: ${error.message}`);
    process.exit(1);
  }
};

module.exports = connectDB; 