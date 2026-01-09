# ECFR Metrics - Full-Stack Application

A comprehensive full-stack application for analyzing and visualizing metrics from Electronic Code of Federal Regulations (ECFR) XML data.

## Features

### Backend (FastAPI)
- **XML Parsing**: Process ECFR XML files and extract structured data
- **Metric Computation**: Calculate various metrics including:
  - Total elements, sections, parts, and subparts
  - Element distribution analysis
  - Section count per part
  - Text length statistics (mean, min, max, total characters)
- **REST API**: Clean, documented API endpoints for data access
- **CORS Support**: Configured for seamless frontend integration
- **Sample Data**: Built-in sample endpoint for demonstration

### Frontend (Next.js)
- **Interactive Dashboard**: Modern, responsive UI for data exploration
- **File Upload**: Drag-and-drop ECFR XML file upload
- **Real-time Visualization**: Interactive charts and graphs using Recharts:
  - Bar charts for element distribution and sections per part
  - Pie charts for element type distribution
  - Statistical cards for key metrics
- **Sample Data Mode**: Explore functionality without uploading files
- **TypeScript**: Full type safety and better developer experience

## Architecture

```
ecfr-metric/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints and XML processing
│   ├── requirements.txt # Python dependencies
│   ├── sample_ecfr.xml  # Sample ECFR XML file
│   └── README.md        # Backend documentation
├── frontend/            # Next.js frontend
│   ├── app/            # Next.js 14 app directory
│   │   ├── page.tsx    # Main dashboard page
│   │   ├── layout.tsx  # Root layout
│   │   └── globals.css # Global styles
│   ├── components/     # React components
│   │   └── MetricsDisplay.tsx # Metrics visualization
│   ├── package.json    # Node dependencies
│   └── README.md       # Frontend documentation
└── README.md           # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the FastAPI server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## Usage

### Option 1: Upload XML File
1. Open the dashboard at `http://localhost:3000`
2. Click "Choose File" and select an ECFR XML file
3. The file will be automatically analyzed and metrics displayed

### Option 2: Use Sample Data
1. Open the dashboard at `http://localhost:3000`
2. Click "Load Sample Data"
3. Explore the sample metrics and visualizations

### API Endpoints

- `GET /` - Health check
- `POST /api/analyze` - Upload and analyze ECFR XML file
- `GET /api/sample-metrics` - Get sample metrics for demonstration

Example API call:
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_ecfr.xml"
```

## Metrics Computed

The application calculates the following metrics from ECFR XML files:

1. **Structural Metrics**:
   - Total number of XML elements
   - Count of sections, parts, and subparts
   - Element type distribution

2. **Content Metrics**:
   - Text length statistics (mean, min, max)
   - Total character count
   - Sections per part breakdown

3. **Visualizations**:
   - Bar charts showing element distribution
   - Pie charts for element type proportions
   - Statistical cards for quick insights

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for FastAPI
- **lxml**: XML processing library
- **Pydantic**: Data validation using Python type annotations

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Recharts**: Composable charting library
- **Axios**: HTTP client for API requests

## Development

### Running Tests
Backend tests can be added using pytest:
```bash
cd backend
pytest
```

Frontend can be linted:
```bash
cd frontend
npm run lint
```

### Building for Production

Backend:
```bash
cd backend
# The backend runs directly with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

Frontend:
```bash
cd frontend
npm run build
npm start
```

## Sample ECFR XML Structure

The application expects XML files following the ECFR structure:
```xml
<ECFR>
  <TITLE>
    <PART N="1">
      <SUBPART N="A">
        <SECTION N="1.1">
          <HD>Section Header</HD>
          <P>Section content...</P>
        </SECTION>
      </SUBPART>
    </PART>
  </TITLE>
</ECFR>
```

A sample file is provided in `backend/sample_ecfr.xml`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.