# KavachG Backend

This is the backend API for the KavachG safety monitoring system. It's built with Node.js, Express, and MongoDB.

## Project Structure

```
backend/
├── src/
│   ├── config/        # Configuration files
│   ├── controllers/   # Route controllers
│   ├── middleware/    # Custom middleware
│   ├── models/        # Mongoose models
│   ├── routes/        # API routes
│   └── server.js      # Entry point
├── package.json
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/users/login` - Login user
- `GET /api/users/profile` - Get user profile (protected)

### Users
- `GET /api/users` - Get all users (admin)
- `POST /api/users` - Register new user (admin)
- `GET /api/users/:id` - Get user by ID (admin)
- `PUT /api/users/:id` - Update user (admin)
- `DELETE /api/users/:id` - Delete user (admin)

### Incidents
- `GET /api/incidents` - Get all incidents (protected)
- `POST /api/incidents` - Create new incident (protected)
- `GET /api/incidents/:id` - Get incident by ID (protected)
- `PUT /api/incidents/:id` - Update incident (operator+)
- `DELETE /api/incidents/:id` - Delete incident (admin)

### Statistics
- `GET /api/stats` - Get overall incident statistics (protected)
- `GET /api/stats/by-sector` - Get incidents by sector (protected)
- `GET /api/stats/by-time` - Get incidents by time (protected)

## Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Set up environment variables in `.env` file (or use defaults):
   ```
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/safety_monitoring
   JWT_SECRET=your_secret_key
   NODE_ENV=development
   ```

3. Start the server:
   ```
   npm run dev
   ```

## User Roles

- **Admin**: Can manage users and has full access
- **Supervisor**: Can manage incidents and view all data
- **Operator**: Can update incidents and view all data
- **Viewer**: Can only view data, no modification

## Integration with ML System

The backend stores incident data detected by the ML system. ML scripts store incident data directly in MongoDB, and the backend provides API endpoints for querying and managing this data.

Each incident includes:
- Incident type (fire, fall, PPE violation, etc.)
- Severity level
- Confidence score
- Timestamp
- Location/sector
- Status (detected, acknowledged, resolved)
- Image/video references 