# Development Guide

## Project Overview

ECFR Metrics is a full-stack application for analyzing Electronic Code of Federal Regulations XML data. It consists of:
- **Backend**: FastAPI REST API for XML parsing and metric computation
- **Frontend**: Next.js dashboard for data visualization

## Architecture

```
┌─────────────┐         ┌─────────────┐
│   Frontend  │ ───────▶│   Backend   │
│  (Next.js)  │ HTTP    │  (FastAPI)  │
│  Port 3000  │ ◀─────  │  Port 8000  │
└─────────────┘  JSON   └─────────────┘
       │                       │
       │                       │
       ▼                       ▼
  Recharts                  lxml XML
  Visualizations            Parser
```

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- pip and npm

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/abou-diop/ecfr-metric.git
   cd ecfr-metric
   ```

2. **Start Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
   Backend will be available at `http://localhost:8000`

3. **Start Frontend** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Frontend will be available at `http://localhost:3000`

### Using Docker

To run the entire stack with Docker Compose:

```bash
docker-compose up --build
```

This will start both backend and frontend services.

## API Endpoints

### Health Check
```http
GET http://localhost:8000/
```

### Analyze XML File
```http
POST http://localhost:8000/api/analyze
Content-Type: multipart/form-data

file: [XML file]
```

### Get Sample Metrics
```http
GET http://localhost:8000/api/sample-metrics
```

## Testing

### Backend Testing

Test the health endpoint:
```bash
curl http://localhost:8000/
```

Test XML analysis:
```bash
cd backend
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@sample_ecfr.xml"
```

### Frontend Testing

1. Navigate to `http://localhost:3000`
2. Click "Load Sample Data" to test with sample data
3. Or upload a real ECFR XML file

## Code Structure

### Backend (`/backend`)
```
backend/
├── main.py              # FastAPI application and endpoints
├── requirements.txt     # Python dependencies
├── sample_ecfr.xml     # Sample ECFR XML file
├── Dockerfile          # Docker configuration
└── README.md           # Backend documentation
```

Key functions in `main.py`:
- `parse_ecfr_xml()`: Parses XML and extracts metrics
- `analyze_ecfr()`: POST endpoint for file upload
- `get_sample_metrics()`: GET endpoint for sample data

### Frontend (`/frontend`)
```
frontend/
├── app/
│   ├── page.tsx        # Main dashboard page
│   ├── layout.tsx      # Root layout
│   └── globals.css     # Global styles
├── components/
│   └── MetricsDisplay.tsx  # Metrics visualization component
├── package.json        # Node dependencies
├── tsconfig.json       # TypeScript configuration
├── Dockerfile          # Docker configuration
└── README.md           # Frontend documentation
```

## Metrics Computed

1. **Structural Metrics**
   - Total XML elements
   - Count of sections, parts, subparts
   - Element type distribution

2. **Content Metrics**
   - Text length statistics (mean, min, max)
   - Total character count
   - Sections per part breakdown

## Adding New Features

### Adding a New Metric to Backend

1. Update `parse_ecfr_xml()` in `backend/main.py`:
   ```python
   # Add your metric computation
   new_metric = compute_new_metric(root)
   
   return {
       # existing metrics...
       "new_metric": new_metric
   }
   ```

2. Update `MetricsResponse` model:
   ```python
   class MetricsResponse(BaseModel):
       # existing fields...
       new_metric: YourType
   ```

### Adding a New Visualization to Frontend

1. Update the `Metrics` interface in `frontend/app/page.tsx`
2. Pass the new metric to `MetricsDisplay` component
3. Add visualization in `frontend/components/MetricsDisplay.tsx`

## Environment Variables

### Backend
No environment variables required by default.

### Frontend
Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Backend Issues

**Issue**: `ImportError: No module named 'fastapi'`
**Solution**: Install dependencies with `pip install -r requirements.txt`

**Issue**: Port 8000 already in use
**Solution**: Change port in `backend/main.py` or kill the process using port 8000

### Frontend Issues

**Issue**: `Module not found` errors
**Solution**: Run `npm install` in the frontend directory

**Issue**: API connection errors
**Solution**: Ensure backend is running and `NEXT_PUBLIC_API_URL` is correct

**Issue**: CORS errors
**Solution**: Verify CORS middleware is properly configured in `backend/main.py`

## Performance Considerations

- Large XML files (>10MB) may take longer to parse
- The frontend limits element distribution to top 10 for readability
- Consider pagination for very large datasets

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.
