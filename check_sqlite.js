const sqlite3 = require('sqlite3').verbose();

// Connect to the database
const db = new sqlite3.Database('./backend/safety_monitoring.sqlite', (err) => {
  if (err) {
    console.error('Error connecting to database:', err.message);
    process.exit(1);
  }
  console.log('Connected to the SQLite database in backend directory.');
});

// Query incidents
db.all(`SELECT * FROM incidents ORDER BY id DESC`, (err, rows) => {
  if (err) {
    console.error('Error querying database:', err.message);
    db.close();
    process.exit(1);
  }
  
  console.log(`Found ${rows.length} incidents in database:`);
  
  if (rows.length === 0) {
    console.log('No incidents found.');
  } else {
    rows.forEach((row, i) => {
      console.log(`\nIncident #${i+1}:`);
      console.log(`- ID: ${row.id}`);
      console.log(`- Type: ${row.incident_type}`);
      console.log(`- Timestamp: ${row.timestamp}`);
      console.log(`- Sector: ${row.sector}`);
      console.log(`- Severity: ${row.severity}`);
      console.log(`- Confidence: ${row.confidence_score}`);
      console.log(`- Image Path: ${row.image_path}`);
      console.log(`- Description: ${row.description}`);
    });
  }
  
  // Close the database connection
  db.close((err) => {
    if (err) {
      console.error('Error closing database:', err.message);
    } else {
      console.log('Database connection closed.');
    }
  });
}); 