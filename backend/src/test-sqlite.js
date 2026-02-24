const { sequelize, testConnection } = require('./config/database');
const { syncModels, createInitialAdmin } = require('./models');
const Incident = require('./models/incidentModel-sqlite');

async function testSQLite() {
  try {
    console.log('Testing SQLite implementation...');
    
    // Test database connection
    const connected = await testConnection();
    if (!connected) {
      console.log('SQLite database connection failed');
      return;
    }
    
    console.log('SQLite database connection has been established successfully.');
    
    // Sync models
    console.log('Syncing database models...');
    await syncModels();
    console.log('All models were synchronized successfully.');
    
    // Create admin if it doesn't exist
    await createInitialAdmin();
    
    // Fetch and display all incidents
    console.log('\nFetching incidents from SQLite database:');
    const incidents = await Incident.findAll({
      order: [['createdAt', 'DESC']],
      limit: 20
    });
    
    if (incidents.length === 0) {
      console.log('No incidents found in the database.');
    } else {
      console.log(`Found ${incidents.length} incidents. Most recent ones:`);
      
      incidents.forEach((incident, index) => {
        console.log(`\nIncident #${index + 1}:`);
        console.log(`- ID: ${incident.id}`);
        console.log(`- Type: ${incident.incident_type}`);
        console.log(`- Timestamp: ${incident.timestamp}`);
        console.log(`- Sector: ${incident.sector}`);
        console.log(`- Severity: ${incident.severity}`);
        console.log(`- Confidence: ${incident.confidence_score}`);
        console.log(`- Status: ${incident.status}`);
      });
    }
    
    console.log('\nSQLite test completed successfully');
    
  } catch (error) {
    console.error('SQLite test failed:', error);
  } finally {
    await sequelize.close();
    console.log('SQLite connection closed');
  }
}

testSQLite(); 