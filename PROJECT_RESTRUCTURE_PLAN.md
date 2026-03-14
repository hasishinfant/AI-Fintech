# Intelli-Credit Project Restructure Plan

## Current Structure Issues
- Components are scattered across multiple directories
- No clear separation between AI pipeline and API layer
- Missing dedicated research agent and CAM generator modules
- Frontend components need better organization

## Target Structure

```
intelli-credit/
├── frontend/                # React dashboard (credit officer UI)
│   ├── public/
│   ├── src/
│   │   ├── components/      # UI components
│   │   │   ├── UploadPanel.jsx
│   │   │   ├── RiskScoreCard.jsx
│   │   │   ├── CAMPreview.jsx
│   │   │   └── ResearchInsights.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── UploadDocuments.jsx
│   │   │   └── Results.jsx
│   │   ├── services/        # API calls
│   │   │   └── api.js
│   │   ├── styles/
│   │   │   └── global.css
│   │   └── App.jsx
│   ├── package.json
│   └── README.md
│
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── routes/
│   │   │   ├── upload.py
│   │   │   ├── risk.py
│   │   │   ├── research.py
│   │   │   └── cam.py
│   │   ├── services/
│   │   │   ├── pdf_parser.py
│   │   │   ├── ocr_engine.py
│   │   │   ├── financial_extractor.py
│   │   │   └── gst_analysis.py
│   │   ├── models/
│   │   │   ├── risk_model.py
│   │   │   └── scoring_engine.py
│   │   ├── database/
│   │   │   ├── db.py
│   │   │   └── schemas.py
│   │   └── utils/
│   │       └── helpers.py
│   ├── requirements.txt
│   └── README.md
│
├── ai_pipeline/             # AI / ML modules
│   ├── document_processing/
│   │   ├── pdf_extractor.py
│   │   ├── table_parser.py
│   │   └── text_cleaner.py
│   ├── research_agent/
│   │   ├── news_scraper.py
│   │   ├── litigation_search.py
│   │   └── sector_analysis.py
│   ├── credit_model/
│   │   ├── five_cs_model.py
│   │   ├── loan_recommendation.py
│   │   └── explainability.py
│   └── cam_generator/
│       ├── cam_template.py
│       └── report_builder.py
│
├── data/                    # sample data for demo
│   ├── sample_annual_report.pdf
│   ├── gst_sample.csv
│   └── bank_statement.csv
│
├── docs/                    # hackathon documentation
│   ├── architecture.md
│   ├── system_design.md
│   └── demo_flow.md
│
├── docker/
│   └── docker-compose.yml
│
├── scripts/                 # automation scripts
│   └── setup.sh
│
├── .env
├── README.md
└── LICENSE
```

## Migration Steps

### Phase 1: Create New Directory Structure
1. Create ai_pipeline/ directory with subdirectories
2. Create docs/ directory
3. Create data/ directory for samples
4. Create scripts/ directory

### Phase 2: Reorganize Backend
1. Move services to proper locations
2. Consolidate routes
3. Update imports

### Phase 3: Reorganize Frontend
1. Create components/ directory with specific components
2. Create pages/ directory
3. Create services/ directory for API calls
4. Update imports

### Phase 4: Extract AI Pipeline
1. Move document processing logic to ai_pipeline/
2. Move research agent logic to ai_pipeline/
3. Move credit model logic to ai_pipeline/
4. Move CAM generator logic to ai_pipeline/

### Phase 5: Documentation
1. Create architecture.md
2. Create system_design.md
3. Create demo_flow.md
4. Update main README.md

### Phase 6: Testing
1. Verify all imports work
2. Test API endpoints
3. Test frontend
4. Run integration tests

## Status: READY TO EXECUTE
