const fetch = require('node-fetch');

// Function to login
async function login() {
  try {
    const response = await fetch('http://localhost:5000/api/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: 'admin@kavachg.com',
        password: 'admin123'
      })
    });
    
    const data = await response.json();
    
    if (data.success && data.token) {
      console.log('Login successful!');
      console.log('User:', data.user.name);
      console.log('Role:', data.user.role);
      return data.token;
    } else {
      console.log('Login failed:', data.message);
      return null;
    }
  } catch (error) {
    console.error('Error during login:', error.message);
    return null;
  }
}

// Function to get incidents
async function getIncidents(token) {
  try {
    const response = await fetch('http://localhost:5000/api/incidents', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log(`\nFound ${data.incidents.length} incidents:`);
      
      data.incidents.forEach((incident, index) => {
        console.log(`\nIncident #${index + 1}:`);
        console.log(`- ID: ${incident.id}`);
        console.log(`- Type: ${incident.incident_type}`);
        console.log(`- Timestamp: ${incident.timestamp}`);
        console.log(`- Sector: ${incident.sector}`);
        console.log(`- Severity: ${incident.severity}`);
        console.log(`- Status: ${incident.status}`);
      });
    } else {
      console.log('Failed to get incidents:', data.message);
    }
  } catch (error) {
    console.error('Error getting incidents:', error.message);
  }
}

// Main function
async function main() {
  console.log('Checking KavachG API...');
  
  // Login to get token
  const token = await login();
  
  if (token) {
    // Get incidents
    await getIncidents(token);
  }
  
  console.log('\nAPI check completed.');
}

// Run the main function
main(); 