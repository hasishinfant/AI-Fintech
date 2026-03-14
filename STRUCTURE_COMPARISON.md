# Project Structure Comparison

## Before Restructure

```
intelli-credit/
├── frontend/
│   └── src/
│       ├── api/client.ts
│       └── pages/
│           ├── Analysis/
│           ├── Applications/
│           └── Recommendation/
└── backend/
    └── app/
        ├── api/routes/
        ├── services/
        │   ├── data_ingestor/
        │   ├── credit_engine/
        │   ├── cam_generator/
        │   └── research_agent/
        └── models/
```

## After Restructure

```
intelli-credit/
├── frontend/
│   └── src/
│       ├── components/      # NEW: Reusable components
│       ├── pages/           # NEW: Page components
│       ├── services/        # NEW: API client
│       └── types/
├── backend/
│   └── app/
│       ├── api/routes/
│       ├── services/        # Kept for backend logic
│       ├── models/
│       └── db/
├── ai_pipeline/             # NEW: AI/ML modules
│   ├── document_processing/
│   ├── research_agent/
│   ├── credit_model/
│   └── cam_generator/
├── docs/                    # NEW: Documentation
├── data/                    # NEW: Sample data
└── scripts/                 # NEW: Automation
```

## Key Changes

1. **AI Pipeline Extracted**: Separated from backend
2. **Frontend Organized**: Components, pages, services
3. **Documentation Added**: Comprehensive docs
4. **Scripts Added**: Setup automation
5. **Sample Data**: Demo-ready data directory
