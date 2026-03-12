# Implementation Plan: Intelli-Credit AI Corporate Credit Decisioning Engine

## Overview

This implementation plan breaks down the Intelli-Credit system into discrete coding tasks. The approach follows a layered implementation strategy:

1. Core data models and database setup
2. Document ingestion and parsing (Data Ingestor)
3. Research and intelligence gathering (Research Agent)
4. Credit analysis and scoring (Credit Engine)
5. CAM generation and export (CAM Generator)
6. API layer and integration
7. Frontend UI (React/TypeScript)

Each task builds incrementally, with property-based tests integrated throughout to validate correctness early.

## Tasks

- [x] 1. Set up project structure and core infrastructure
  - Create Python backend project with FastAPI
  - Set up PostgreSQL database with schema from design
  - Configure AWS S3 for document storage
  - Set up development environment with dependencies (pandas, pdfplumber, pytesseract, scikit-learn, shap, FAISS)
  - Create React/TypeScript frontend project with Tailwind CSS
  - Set up testing frameworks (pytest with Hypothesis for Python, Jest with fast-check for TypeScript)
  - _Requirements: All (infrastructure foundation)_

- [x] 2. Implement core data models and database layer
  - [x] 2.1 Create Python dataclasses for all domain models
    - Implement FinancialData, GSTData, Transaction, Company, Promoter, Debt, Asset models
    - Implement NewsArticle, MCAData, LegalCase, SentimentScore models
    - Implement FiveCsScores, RiskScore, LoanRecommendation, Explanation models
    - Implement CAMDocument, AuditTrail, AuditEvent models
    - _Requirements: All (data foundation)_
  
  - [x]* 2.2 Write property test for data model validation
    - **Property 13: Five Cs Score Validity**
    - **Validates: Requirements 5.4, 6.4, 7.4, 8.4, 9.4, 10.1**
  
  - [x] 2.3 Create database repository layer
    - Implement CRUD operations for applications, companies, financial_data tables
    - Implement CRUD operations for research_data, credit_assessments, audit_trail tables
    - Add connection pooling and transaction management
    - _Requirements: All (data persistence)_

- [x] 3. Implement document parsing and OCR (Data Ingestor - Part 1)
  - [x] 3.1 Create DocumentParser class
    - Implement parse_pdf() using pdfplumber
    - Implement apply_ocr() using pytesseract for scanned documents
    - Add document type detection logic
    - _Requirements: 1.4, 1.5_
  
  - [x]* 3.2 Write property test for OCR application
    - **Property 2: OCR Application for Scanned Documents**
    - **Validates: Requirements 1.5**
  
  - [x] 3.3 Create DataExtractor class with format-specific extractors
    - Implement extract_gst_returns() for GSTR-2A and GSTR-3B formats
    - Implement extract_itr() for Income Tax Returns
    - Implement extract_bank_statements() for transaction history
    - Implement extract_annual_report() for financial statements
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 18.1_
  
  - [x]* 3.4 Write property test for document extraction completeness
    - **Property 1: Document Data Extraction Completeness**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.6**
  
  - [x]* 3.5 Write property test for GST format parsing
    - **Property 45: GST Format Parsing**
    - **Validates: Requirements 18.1**

- [x] 4. Implement data normalization and confidence scoring (Data Ingestor - Part 2)
  - [x] 4.1 Create DataNormalizer class
    - Implement normalize_financial_data() to convert various formats to unified schema
    - Implement calculate_confidence_scores() for extracted fields
    - Add validation rules for financial data
    - _Requirements: 2.5, 17.4_
  
  - [x]* 4.2 Write property test for data normalization
    - **Property 6: Data Normalization**
    - **Validates: Requirements 2.5**
  
  - [x]* 4.3 Write property test for confidence score provision
    - **Property 44: Confidence Score Provision**
    - **Validates: Requirements 17.4**
  
  - [x]* 4.4 Write property test for low confidence flagging
    - **Property 43: Low Confidence Field Flagging**
    - **Validates: Requirements 17.3**
  
  - [x]* 4.5 Write property test for extraction accuracy
    - **Property 3: Extraction Accuracy Threshold**
    - **Validates: Requirements 1.7, 17.1, 17.2**

- [x] 5. Implement circular trading detection (Data Ingestor - Part 3)
  - [x] 5.1 Create CircularTradingDetector class
    - Implement detect_circular_trading() to cross-check GST sales vs bank deposits
    - Implement compare_gstr_versions() to compare GSTR-2A and GSTR-3B
    - Add alert generation with discrepancy details
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [x]* 5.2 Write property test for circular trading cross-check
    - **Property 7: Circular Trading Detection via Cross-Check**
    - **Validates: Requirements 3.1**
  
  - [x]* 5.3 Write property test for GSTR mismatch detection
    - **Property 8: GSTR Mismatch Detection**
    - **Validates: Requirements 3.2**
  
  - [x]* 5.4 Write property test for alert generation
    - **Property 9: Circular Trading Alert Generation**
    - **Validates: Requirements 3.3**
  
  - [x]* 5.5 Write property test for high-risk deposit ratio
    - **Property 10: High-Risk Deposit Ratio Flagging**
    - **Validates: Requirements 3.4**

- [x] 6. Checkpoint - Data Ingestor validation
  - Ensure all Data Ingestor tests pass
  - Verify document parsing works with sample documents
  - Ask the user if questions arise

- [x] 7. Implement web research and crawling (Research Agent - Part 1)
  - [x] 7.1 Create WebCrawler class
    - Implement search_company_news() using news APIs
    - Implement fetch_mca_filings() for MCA data retrieval
    - Implement search_ecourts() for litigation search
    - Implement fetch_rbi_notifications() for regulatory data
    - Add retry logic and error handling for API calls
    - _Requirements: 2.1, 2.2, 2.3, 4.1, 4.3, 4.4, 4.5_
  
  - [x]* 7.2 Write property test for external data integration
    - **Property 4: External Data Source Integration**
    - **Validates: Requirements 2.1, 2.2, 2.3**
  
  - [x]* 7.3 Write property test for research source attribution
    - **Property 11: Research Source Attribution**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**

- [x] 8. Implement sentiment analysis and compliance checking (Research Agent - Part 2)
  - [x] 8.1 Create SentimentAnalyzer class
    - Implement analyze_news_sentiment() using NLP models
    - Implement extract_key_events() from news articles
    - Integrate with OpenAI/Llama for advanced text analysis
    - _Requirements: 4.2_
  
  - [x]* 8.2 Write property test for sentiment classification
    - **Property 12: Sentiment Classification**
    - **Validates: Requirements 4.2**
  
  - [x] 8.3 Create ComplianceChecker class
    - Implement check_mca_compliance() for filing status verification
    - Implement check_director_disqualification() for director checks
    - _Requirements: 4.3_

- [x] 9. Implement Five Cs analysis - Character and Capacity (Credit Engine - Part 1)
  - [x] 9.1 Create FiveCsAnalyzer class with Character analysis
    - Implement analyze_character() to assess promoter credibility
    - Integrate litigation history, governance records, and CIBIL data
    - Calculate Character score (0-100)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x]* 9.2 Write property test for Character assessment data sources
    - **Property 14: Character Assessment Data Sources**
    - **Validates: Requirements 5.1, 5.2, 5.3**
  
  - [x] 9.3 Implement Capacity analysis
    - Implement analyze_capacity() to calculate DSCR and repayment ability
    - Calculate Capacity score (0-100)
    - Generate breakdown of cash flow components
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x]* 9.4 Write property test for DSCR calculation
    - **Property 15: DSCR Calculation Formula**
    - **Validates: Requirements 6.1**
  
  - [x]* 9.5 Write property test for DSCR threshold flagging
    - **Property 16: DSCR Threshold Flagging**
    - **Validates: Requirements 6.2**
  
  - [x]* 9.6 Write property test for capacity breakdown
    - **Property 17: Capacity Score Breakdown**
    - **Validates: Requirements 6.5**

- [x] 10. Implement Five Cs analysis - Capital and Collateral (Credit Engine - Part 2)
  - [x] 10.1 Implement Capital analysis
    - Implement analyze_capital() to evaluate equity strength
    - Calculate Debt-to-Equity ratio
    - Analyze net worth trends over three years
    - Calculate Capital score (0-100)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x]* 10.2 Write property test for Debt-to-Equity calculation
    - **Property 18: Debt-to-Equity Calculation**
    - **Validates: Requirements 7.1**
  
  - [x]* 10.3 Write property test for Debt-to-Equity threshold
    - **Property 19: Debt-to-Equity Threshold Flagging**
    - **Validates: Requirements 7.2**
  
  - [x]* 10.4 Write property test for net worth trend analysis
    - **Property 20: Net Worth Trend Analysis**
    - **Validates: Requirements 7.3**
  
  - [x] 10.5 Implement Collateral analysis
    - Implement analyze_collateral() to calculate LTV
    - Handle multiple collateral assets with aggregate LTV
    - Calculate Collateral score (0-100)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x]* 10.6 Write property test for LTV calculation
    - **Property 21: LTV Calculation Formula**
    - **Validates: Requirements 8.1**
  
  - [x]* 10.7 Write property test for LTV threshold flagging
    - **Property 22: LTV Threshold Flagging**
    - **Validates: Requirements 8.2**
  
  - [x]* 10.8 Write property test for aggregate LTV
    - **Property 23: Aggregate LTV Calculation**
    - **Validates: Requirements 8.3**

- [x] 11. Implement Five Cs analysis - Conditions (Credit Engine - Part 3)
  - [x] 11.1 Implement Conditions analysis
    - Implement analyze_conditions() to assess external risks
    - Analyze sector-specific risks from industry reports
    - Check RBI notifications and policy changes
    - Assess commodity price volatility risks
    - Calculate Conditions score (0-100)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 12. Implement risk aggregation and scoring (Credit Engine - Part 4)
  - [x] 12.1 Create RatioCalculator class
    - Implement calculate_dscr(), calculate_debt_equity_ratio(), calculate_ltv()
    - Add accounting period consistency checks
    - Implement industry benchmark comparison
    - Calculate three-year trends
    - Flag out-of-range ratios with severity
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_
  
  - [x]* 12.2 Write property test for financial ratio calculation set
    - **Property 38: Financial Ratio Calculation Set**
    - **Validates: Requirements 16.1**
  
  - [x]* 12.3 Write property test for accounting period consistency
    - **Property 39: Accounting Period Consistency**
    - **Validates: Requirements 16.2**
  
  - [x]* 12.4 Write property test for benchmark comparison
    - **Property 40: Industry Benchmark Comparison**
    - **Validates: Requirements 16.3**
  
  - [x]* 12.5 Write property test for trend calculation
    - **Property 41: Three-Year Trend Calculation**
    - **Validates: Requirements 16.4**
  
  - [x]* 12.6 Write property test for out-of-range flagging
    - **Property 42: Out-of-Range Ratio Flagging**
    - **Validates: Requirements 16.5**
  
  - [x] 12.7 Create RiskAggregator class
    - Implement calculate_composite_risk_score() with weighted Five Cs
    - Implement classify_risk_level() for high/medium/low classification
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x]* 12.8 Write property test for weighted risk score
    - **Property 24: Weighted Risk Score Calculation**
    - **Validates: Requirements 10.2**

- [x] 13. Implement loan calculation and interest rate determination (Credit Engine - Part 5)
  - [x] 13.1 Create LoanCalculator class
    - Implement calculate_max_loan_amount() using EBITDA formula (0.4 × EBITDA)
    - Apply collateral cap (75% of collateral value)
    - Apply DSCR-based reduction for low DSCR
    - Implement most conservative constraint logic
    - Generate calculation breakdown
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [x]* 13.2 Write property test for EBITDA-based loan calculation
    - **Property 25: Maximum Loan Amount Calculation**
    - **Validates: Requirements 11.1**
  
  - [x]* 13.3 Write property test for collateral cap
    - **Property 26: Collateral-Based Loan Cap**
    - **Validates: Requirements 11.2**
  
  - [x]* 13.4 Write property test for DSCR reduction
    - **Property 27: DSCR-Based Loan Reduction**
    - **Validates: Requirements 11.3**
  
  - [x]* 13.5 Write property test for calculation breakdown
    - **Property 28: Loan Amount Calculation Breakdown**
    - **Validates: Requirements 11.4**
  
  - [x]* 13.6 Write property test for conservative constraint
    - **Property 29: Most Conservative Constraint Application**
    - **Validates: Requirements 11.5**
  
  - [x] 13.7 Implement determine_interest_rate()
    - Calculate interest rate as base rate + risk premium
    - Apply risk-based premium tiers
    - Document rate components
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [x]* 13.8 Write property test for interest rate formula
    - **Property 30: Interest Rate Formula**
    - **Validates: Requirements 12.1**

- [x] 14. Implement explainability engine (Credit Engine - Part 6)
  - [x] 14.1 Create ExplainabilityEngine class
    - Implement explain_risk_score() using SHAP values
    - Implement explain_loan_amount() with constraint identification
    - Implement explain_interest_rate() with risk factor documentation
    - Add source citation for all data points
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [x]* 14.2 Write property test for explanation completeness
    - **Property 31: Recommendation Explanation Completeness**
    - **Validates: Requirements 13.1**
  
  - [x]* 14.3 Write property test for top factors identification
    - **Property 32: Top Risk Factors Identification**
    - **Validates: Requirements 13.2**
  
  - [x]* 14.4 Write property test for limiting constraint identification
    - **Property 33: Limiting Constraint Identification**
    - **Validates: Requirements 13.3**
  
  - [x]* 14.5 Write property test for source citation
    - **Property 34: Explanation Source Citation**
    - **Validates: Requirements 13.5**

- [x] 15. Checkpoint - Credit Engine validation
  - Ensure all Credit Engine tests pass
  - Verify Five Cs scoring with sample data
  - Verify loan calculations and explanations
  - Ask the user if questions arise

- [x] 16. Implement audit trail management (CAM Generator - Part 1)
  - [x] 16.1 Create AuditTrailManager class
    - Implement record_data_ingestion() for data source tracking
    - Implement record_research_activity() for URL and data logging
    - Implement record_calculation() for formula and input documentation
    - Implement record_modification() for change tracking
    - _Requirements: 15.1, 15.2, 15.3, 15.5_
  
  - [x]* 16.2 Write property test for audit trail completeness
    - **Property 37: Audit Trail Completeness**
    - **Validates: Requirements 15.1, 15.2, 15.3, 15.4, 15.5**

- [x] 17. Implement CAM document generation (CAM Generator - Part 2)
  - [x] 17.1 Create CAMGenerator class
    - Implement generate_executive_summary()
    - Implement generate_company_overview()
    - Implement generate_industry_analysis()
    - Implement generate_financial_analysis()
    - Implement generate_risk_assessment()
    - Implement generate_five_cs_summary()
    - Implement generate_final_recommendation()
    - Implement add_explainability_notes()
    - Implement add_audit_trail()
    - _Requirements: 14.1, 14.2, 15.4_
  
  - [x]* 17.2 Write property test for CAM section completeness
    - **Property 35: CAM Section Completeness**
    - **Validates: Requirements 14.1, 14.2**

- [x] 18. Implement document export functionality (CAM Generator - Part 3)
  - [x] 18.1 Create DocumentExporter class
    - Implement export_to_word() using python-docx
    - Implement export_to_pdf() using reportlab or similar
    - Add template loading and formatting
    - _Requirements: 14.3_
  
  - [x]* 18.2 Write property test for export format support
    - **Property 36: CAM Export Format Support**
    - **Validates: Requirements 14.3**

- [x] 19. Implement FastAPI backend endpoints
  - [x] 19.1 Create application management endpoints
    - POST /api/applications - Create new loan application
    - GET /api/applications/{id} - Get application details
    - POST /api/applications/{id}/documents - Upload documents
    - GET /api/applications/{id}/status - Get processing status
    - _Requirements: All (API layer)_
  
  - [x] 19.2 Create processing endpoints
    - POST /api/applications/{id}/process - Trigger full workflow
    - GET /api/applications/{id}/research - Get research results
    - GET /api/applications/{id}/credit-assessment - Get credit scores
    - GET /api/applications/{id}/recommendation - Get loan recommendation
    - _Requirements: 19.1, 19.2, 19.3, 19.4_
  
  - [x] 19.3 Create CAM generation endpoints
    - POST /api/applications/{id}/cam/generate - Generate CAM
    - GET /api/applications/{id}/cam - Get CAM document
    - GET /api/applications/{id}/cam/export/word - Export to Word
    - GET /api/applications/{id}/cam/export/pdf - Export to PDF
    - _Requirements: 14.1, 14.2, 14.3_
  
  - [x] 19.4 Add authentication and authorization middleware
    - Implement JWT-based authentication
    - Add role-based access control for Credit Officers
    - _Requirements: All (security)_

- [x] 20. Implement end-to-end workflow orchestration
  - [x] 20.1 Create WorkflowOrchestrator class
    - Implement orchestrate_full_workflow() to chain all components
    - Add async processing for long-running tasks
    - Implement progress tracking and status updates
    - Add error handling and rollback logic
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_
  
  - [x]* 20.2 Write property test for workflow automation
    - **Property 49: End-to-End Workflow Automation**
    - **Validates: Requirements 19.1, 19.2, 19.3, 19.4**
  
  - [x]* 20.3 Write property test for workflow completion time
    - **Property 50: Workflow Completion Time**
    - **Validates: Requirements 19.5**

- [x] 21. Checkpoint - Backend integration validation
  - Ensure all API endpoints work correctly
  - Test end-to-end workflow with sample data
  - Verify CAM generation and export
  - Ask the user if questions arise

- [x] 22. Implement React frontend - Application management UI
  - [x] 22.1 Create application list and detail views
    - Build ApplicationList component with table view
    - Build ApplicationDetail component with tabs
    - Add document upload interface with drag-and-drop
    - Implement status tracking and progress indicators
    - Style with Tailwind CSS
    - _Requirements: All (UI layer)_
  
  - [x] 22.2 Create document upload and management UI
    - Build DocumentUpload component with file validation
    - Build DocumentList component showing uploaded files
    - Add confidence score visualization
    - Show extraction results and flagged fields
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 17.3, 17.4_

- [x] 23. Implement React frontend - Research and analysis UI
  - [x] 23.1 Create research results display
    - Build ResearchPanel component showing news, MCA, legal data
    - Add sentiment visualization
    - Display source URLs and timestamps
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [x] 23.2 Create Five Cs scoring dashboard
    - Build FiveCsScorecard component with score visualization
    - Add radar chart for Five Cs scores
    - Display detailed breakdowns for each C
    - Show risk level classification
    - _Requirements: 5.4, 6.4, 7.4, 8.4, 9.4, 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 23.3 Create financial analysis dashboard
    - Build FinancialRatios component with ratio cards
    - Add trend charts for three-year analysis
    - Display industry benchmark comparisons
    - Highlight flagged ratios
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

- [x] 24. Implement React frontend - Recommendation and CAM UI
  - [x] 24.1 Create loan recommendation display
    - Build RecommendationPanel component
    - Display max loan amount with calculation breakdown
    - Show interest rate with components
    - Add explainability section with top factors
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 12.1, 12.5, 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [x] 24.2 Create CAM preview and export UI
    - Build CAMPreview component with section navigation
    - Add export buttons for Word and PDF
    - Display audit trail in expandable section
    - Show generation timestamp and version
    - _Requirements: 14.1, 14.2, 14.3, 15.4_

- [x] 25. Implement React frontend - Manual input and corrections
  - [x] 25.1 Create site visit notes input
    - Build SiteVisitNotes component with rich text editor
    - Add association with application
    - _Requirements: 2.4_
  
  - [x] 25.2 Create manual correction interface
    - Build FieldCorrection component for flagged fields
    - Allow Credit Officers to override extracted values
    - Track corrections in audit trail
    - _Requirements: 17.5_

- [x] 26. Implement frontend state management and API integration
  - [x] 26.1 Set up React Query for API calls
    - Configure API client with authentication
    - Implement queries for all GET endpoints
    - Implement mutations for all POST endpoints
    - Add error handling and retry logic
    - _Requirements: All (frontend-backend integration)_
  
  - [x] 26.2 Add real-time status updates
    - Implement WebSocket or polling for workflow progress
    - Update UI as processing stages complete
    - Show notifications for completion and errors
    - _Requirements: 19.5_

- [x] 27. Final integration and testing
  - [x]* 27.1 Run full property-based test suite
    - Execute all 50 property tests with 100+ iterations each
    - Verify all properties pass
    - _Requirements: All_
  
  - [x]* 27.2 Run integration tests
    - Test end-to-end workflow from UI to CAM generation
    - Test error scenarios and edge cases
    - Verify audit trail completeness
    - _Requirements: All_
  
  - [x] 27.3 Performance testing
    - Test workflow completion time (target < 5 minutes)
    - Test with large documents (100+ pages)
    - Test concurrent user scenarios
    - _Requirements: 19.5_

- [x] 28. Final checkpoint - System validation
  - Ensure all tests pass
  - Verify demo workflow works end-to-end
  - Review CAM output quality
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples and edge cases
- Backend implementation (Python/FastAPI) comes before frontend (React/TypeScript)
- Checkpoints ensure incremental validation at major milestones
