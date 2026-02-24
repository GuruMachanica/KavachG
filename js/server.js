const express = require('express');
const path = require('path');
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();
const PORT = 3000;
const BACKEND_URL = 'http://localhost:5001/api';

// Enable CORS
app.use(cors());

// Parse JSON bodies
app.use(express.json());

// Serve static files from the current directory
app.use(express.static(path.join(__dirname, '..')));

// API routes
let sharedData = {
    message: "Hello from the server!"
};

// GET route
app.get('/api/data', (req, res) => {
    res.json(sharedData);
});

// POST route
app.post('/api/data', (req, res) => {
    const { message } = req.body;
    sharedData.message = message;
    res.json({ status: 'Message updated', message });
});

// Add a test endpoint to create an incident
app.post('/api/test-incident', async (req, res) => {
    try {
        const incidentData = req.body || {
            incident_type: 'fire',
            severity: 'medium',
            confidence_score: 0.75,
            sector: 'frontend-test'
        };

        const response = await fetch(`${BACKEND_URL}/incidents`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(incidentData)
        });

        const data = await response.json();
        res.status(response.status).json(data);
    } catch (error) {
        console.error('Error creating incident:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to create incident',
            error: error.message
        });
    }
});

// Add endpoint to get incidents from backend
app.get('/api/incidents', async (req, res) => {
    try {
        // This would normally need authentication
        const response = await fetch(`${BACKEND_URL}/incidents`);
        const data = await response.json();
        res.status(response.status).json(data);
    } catch (error) {
        console.error('Error fetching incidents:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch incidents',
            error: error.message
        });
    }
});

// For all other requests, serve the index.html file
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Frontend server running on http://localhost:${PORT}`);
    console.log(`Test incident creation: POST http://localhost:${PORT}/api/test-incident`);
}); 