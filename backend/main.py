from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
import xml.etree.ElementTree as ET
from io import BytesIO
from pydantic import BaseModel

app = FastAPI(title="ECFR Metrics API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MetricsResponse(BaseModel):
    total_elements: int
    total_sections: int
    total_parts: int
    total_subparts: int
    element_distribution: Dict[str, int]
    section_count_by_part: Dict[str, int]
    text_length_stats: Dict[str, float]

def parse_ecfr_xml(xml_content: bytes) -> Dict[str, Any]:
    """Parse ECFR XML and extract metrics"""
    try:
        tree = ET.parse(BytesIO(xml_content))
        root = tree.getroot()
        
        # Count different element types
        element_counts = {}
        sections = []
        parts = []
        subparts = []
        text_lengths = []
        
        # Walk through all elements
        for elem in root.iter():
            tag = elem.tag
            element_counts[tag] = element_counts.get(tag, 0) + 1
            
            # Extract text content for analysis
            if elem.text:
                text_lengths.append(len(elem.text.strip()))
            
            # Track specific ECFR elements
            if 'SECTION' in tag.upper() or 'SEC' == tag.upper():
                sections.append(elem)
            if 'PART' in tag.upper():
                parts.append(elem)
            if 'SUBPART' in tag.upper():
                subparts.append(elem)
        
        # Calculate text length statistics
        text_stats = {
            "mean": sum(text_lengths) / len(text_lengths) if text_lengths else 0,
            "min": min(text_lengths) if text_lengths else 0,
            "max": max(text_lengths) if text_lengths else 0,
            "total_chars": sum(text_lengths)
        }
        
        # Section count by part
        section_by_part = {}
        for part in parts:
            part_num = part.get('N', 'Unknown')
            sections_in_part = len([s for s in part.iter() if 'SECTION' in s.tag.upper()])
            if sections_in_part > 0:
                section_by_part[f"Part {part_num}"] = sections_in_part
        
        return {
            "total_elements": sum(element_counts.values()),
            "total_sections": len(sections),
            "total_parts": len(parts),
            "total_subparts": len(subparts),
            "element_distribution": element_counts,
            "section_count_by_part": section_by_part,
            "text_length_stats": text_stats
        }
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing XML: {str(e)}")

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "ECFR Metrics API is running",
        "version": "1.0.0"
    }

@app.post("/api/analyze", response_model=MetricsResponse)
async def analyze_ecfr(file: UploadFile = File(...)):
    """
    Analyze ECFR XML file and return metrics
    
    Args:
        file: XML file upload
        
    Returns:
        MetricsResponse with computed metrics
    """
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="File must be XML format")
    
    content = await file.read()
    metrics = parse_ecfr_xml(content)
    
    return MetricsResponse(**metrics)

@app.get("/api/sample-metrics")
def get_sample_metrics():
    """
    Get sample metrics for demonstration purposes
    """
    return {
        "total_elements": 1542,
        "total_sections": 87,
        "total_parts": 12,
        "total_subparts": 34,
        "element_distribution": {
            "DIV": 245,
            "P": 456,
            "SECTION": 87,
            "HEAD": 123,
            "PART": 12,
            "SUBPART": 34,
            "TITLE": 15,
            "PRTPAGE": 89,
            "HD": 145,
            "TEXT": 336
        },
        "section_count_by_part": {
            "Part 1": 8,
            "Part 2": 12,
            "Part 3": 15,
            "Part 4": 9,
            "Part 5": 11,
            "Part 6": 7,
            "Part 7": 10,
            "Part 8": 6,
            "Part 9": 5,
            "Part 10": 4
        },
        "text_length_stats": {
            "mean": 145.6,
            "min": 5,
            "max": 2340,
            "total_chars": 65432
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
