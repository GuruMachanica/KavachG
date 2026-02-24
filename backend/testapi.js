// Simple script to test the API directly
const fetch = require('node-fetch');

// Base URL of the API
const API_URL = 'http://localhost:5000/api';

// Test creating an incident
async function createIncident() {
  try {
    console.log('Attempting to create a test incident...');
    
    const response = await fetch(`${API_URL}/incidents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        incident_type: 'fire',
        severity: 'high',
        confidence_score: 0.95,
        sector: 'test-sector',
        timestamp: new Date()
      })
    });
    
    const data = await response.json();
    console.log('API Response:', data);
    
    if (data.success) {
      console.log('Incident created successfully!');
      return data.data._id;
    } else {
      console.error('Failed to create incident:', data.message);
      return null;
    }
  } catch (error) {
    console.error('Error creating incident:', error.message);
    return null;
  }
}

// Test getting incidents
async function getIncidents() {
  try {
    console.log('Attempting to get incidents...');
    
    const response = await fetch(`${API_URL}/health`);
    const data = await response.json();
    
    console.log('API Health Check Response:', data);
  } catch (error) {
    console.error('Error getting incidents:', error.message);
  }
}

// Run the tests
async function runTests() {
  console.log('Starting API tests...');
  
  // First check API health
  await getIncidents();
  
  // Then create an incident
  const incidentId = await createIncident();
  
  if (incidentId) {
    console.log(`Test incident created with ID: ${incidentId}`);
  }
  
  console.log('API tests completed.');
}

runTests(); 