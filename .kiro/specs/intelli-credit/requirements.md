# Requirements Document: Intelli-Credit AI Corporate Credit Decisioning Engine

## Introduction

Intelli-Credit is an AI-powered corporate credit decisioning engine designed for Credit Officers in Indian Banks and Non-Banking Financial Companies (NBFCs). The system automates the preparation of Credit Appraisal Memos (CAMs) by ingesting multi-format financial data, performing intelligent web research, and generating explainable lending recommendations based on the Five Cs of Credit framework.

## Glossary

- **CAM**: Credit Appraisal Memo - A comprehensive document used by banks to evaluate loan applications
- **Data_Ingestor**: Component responsible for extracting and processing financial data from multiple sources
- **Research_Agent**: Component that performs web-based intelligence gathering about borrowers
- **Credit_Engine**: Component that calculates risk scores and loan recommendations
- **CAM_Generator**: Component that produces formatted Credit Appraisal Memos
- **DSCR**: Debt Service Coverage Ratio - Measures ability to repay debt (Cash Flow / Debt Service)
- **Five_Cs**: Character, Capacity, Capital, Collateral, Conditions - Traditional credit assessment framework
- **GST**: Goods and Services Tax - Indian indirect tax system
- **ITR**: Income Tax Return - Annual tax filing document
- **MCA**: Ministry of Corporate Affairs - Indian government body regulating companies
- **GSTR**: GST Return - Periodic tax filing documents (GSTR-2A for purchases, GSTR-3B for summary)
- **OCR**: Optical Character Recognition - Technology to extract text from scanned images
- **CIBIL**: Credit Information Bureau India Limited - Credit bureau providing credit scores
- **EBITDA**: Earnings Before Interest, Taxes, Depreciation, and Amortization
- **LTV**: Loan-to-Value ratio - Loan amount divided by collateral value
- **Circular_Trading**: Fraudulent practice where sales are artificially inflated through fake transactions

## Requirements

### Requirement 1: Multi-Format Financial Data Ingestion

**User Story:** As a Credit Officer, I want to upload financial documents in various formats, so that I can automatically extract data without manual entry.

#### Acceptance Criteria

1. WHEN a user uploads a structured GST return file, THEN the Data_Ingestor SHALL parse and extract all transaction records
2. WHEN a user uploads an ITR document, THEN the Data_Ingestor SHALL extract income, expenses, and tax payment information
3. WHEN a user uploads bank statement files, THEN the Data_Ingestor SHALL extract transaction history with dates, amounts, and descriptions
4. WHEN a user uploads a PDF annual report, THEN the Data_Ingestor SHALL extract financial statements including balance sheet and profit-loss data
5. WHEN a user uploads a scanned document, THEN the Data_Ingestor SHALL apply OCR to convert images to text before extraction
6. WHEN a user uploads board minutes or rating reports, THEN the Data_Ingestor SHALL extract key decisions and credit ratings
7. WHEN extraction completes, THEN the Data_Ingestor SHALL achieve minimum 85% field extraction accuracy for all document types

### Requirement 2: External Data Source Integration

**User Story:** As a Credit Officer, I want the system to automatically fetch external data sources, so that I have comprehensive information for credit assessment.

#### Acceptance Criteria

1. WHEN a company identifier is provided, THEN the Data_Ingestor SHALL retrieve MCA filings for that company
2. WHEN processing a loan application, THEN the Data_Ingestor SHALL fetch relevant news articles about the company
3. WHEN assessing credit risk, THEN the Data_Ingestor SHALL retrieve legal records from e-Courts database
4. WHEN a Credit Officer adds site visit notes, THEN the Data_Ingestor SHALL store and associate them with the application
5. WHEN all data sources are ingested, THEN the Data_Ingestor SHALL normalize and store data in a unified format

### Requirement 3: Circular Trading Detection

**User Story:** As a Credit Officer, I want the system to detect circular trading patterns, so that I can identify potentially fraudulent applications.

#### Acceptance Criteria

1. WHEN GST sales data and bank deposit data are available, THEN the Data_Ingestor SHALL cross-check sales amounts against actual deposits
2. WHEN a significant mismatch is detected between GSTR-2A and GSTR-3B, THEN the Data_Ingestor SHALL flag the application for circular trading risk
3. WHEN circular trading indicators are found, THEN the Data_Ingestor SHALL generate an alert with specific discrepancies and amounts
4. WHEN bank deposits are less than 70% of reported GST sales, THEN the Data_Ingestor SHALL mark this as a high-risk indicator

### Requirement 4: Intelligent Web Research

**User Story:** As a Credit Officer, I want the system to perform automated web research, so that I have current intelligence about the borrower.

#### Acceptance Criteria

1. WHEN a company name is provided, THEN the Research_Agent SHALL search news APIs for recent articles about the company
2. WHEN conducting research, THEN the Research_Agent SHALL analyze news sentiment and classify it as positive, neutral, or negative
3. WHEN checking compliance, THEN the Research_Agent SHALL verify MCA filing status and flag any non-compliance
4. WHEN assessing legal risk, THEN the Research_Agent SHALL search e-Courts database for pending or past litigation
5. WHEN gathering industry context, THEN the Research_Agent SHALL retrieve relevant RBI notifications and industry reports
6. WHEN research is complete, THEN the Research_Agent SHALL provide source URLs and timestamps for all gathered information

### Requirement 5: Promoter Character Assessment

**User Story:** As a Credit Officer, I want the system to assess promoter credibility, so that I can evaluate the Character dimension of credit risk.

#### Acceptance Criteria

1. WHEN evaluating a promoter, THEN the Credit_Engine SHALL check for litigation history from e-Courts data
2. WHEN assessing governance, THEN the Credit_Engine SHALL analyze board minutes and MCA compliance records
3. WHEN checking credit history, THEN the Credit_Engine SHALL retrieve and analyze CIBIL commercial credit bureau data
4. WHEN Character assessment is complete, THEN the Credit_Engine SHALL assign a Character score from 0 to 100
5. WHEN any negative indicators are found, THEN the Credit_Engine SHALL document specific issues with supporting evidence

### Requirement 6: Capacity to Repay Analysis

**User Story:** As a Credit Officer, I want the system to calculate debt service coverage, so that I can assess the borrower's ability to repay.

#### Acceptance Criteria

1. WHEN financial statements are available, THEN the Credit_Engine SHALL calculate DSCR using the formula: Cash Flow divided by Debt Service
2. WHEN DSCR is below 1.25, THEN the Credit_Engine SHALL flag the application as having insufficient repayment capacity
3. WHEN calculating cash flow, THEN the Credit_Engine SHALL use operating cash flow from cash flow statements or derive it from financial statements
4. WHEN Capacity assessment is complete, THEN the Credit_Engine SHALL assign a Capacity score from 0 to 100
5. WHEN DSCR is calculated, THEN the Credit_Engine SHALL provide a breakdown showing cash flow components and debt obligations

### Requirement 7: Capital Strength Evaluation

**User Story:** As a Credit Officer, I want the system to evaluate borrower equity strength, so that I can assess the Capital dimension of credit risk.

#### Acceptance Criteria

1. WHEN balance sheet data is available, THEN the Credit_Engine SHALL calculate Debt-to-Equity ratio
2. WHEN Debt-to-Equity ratio exceeds 2.0, THEN the Credit_Engine SHALL flag the application as having weak capital structure
3. WHEN evaluating capital, THEN the Credit_Engine SHALL analyze trends in net worth over the past three years
4. WHEN Capital assessment is complete, THEN the Credit_Engine SHALL assign a Capital score from 0 to 100
5. WHEN capital adequacy is assessed, THEN the Credit_Engine SHALL document the composition of equity and debt

### Requirement 8: Collateral Valuation

**User Story:** As a Credit Officer, I want the system to calculate loan-to-value ratios, so that I can assess collateral adequacy.

#### Acceptance Criteria

1. WHEN collateral information is provided, THEN the Credit_Engine SHALL calculate LTV as loan amount divided by collateral value
2. WHEN LTV exceeds 0.75, THEN the Credit_Engine SHALL flag the application as having insufficient collateral coverage
3. WHEN multiple collateral assets are provided, THEN the Credit_Engine SHALL calculate aggregate LTV across all assets
4. WHEN Collateral assessment is complete, THEN the Credit_Engine SHALL assign a Collateral score from 0 to 100
5. WHEN collateral is evaluated, THEN the Credit_Engine SHALL document asset types, values, and valuation dates

### Requirement 9: External Conditions Assessment

**User Story:** As a Credit Officer, I want the system to evaluate external risk factors, so that I can assess the Conditions dimension of credit risk.

#### Acceptance Criteria

1. WHEN assessing conditions, THEN the Credit_Engine SHALL analyze sector-specific risks from industry reports
2. WHEN evaluating regulatory risk, THEN the Credit_Engine SHALL check for relevant RBI notifications and policy changes
3. WHEN commodity exposure exists, THEN the Credit_Engine SHALL assess commodity price volatility risks
4. WHEN Conditions assessment is complete, THEN the Credit_Engine SHALL assign a Conditions score from 0 to 100
5. WHEN external risks are identified, THEN the Credit_Engine SHALL document specific risk factors with supporting data

### Requirement 10: Risk Score Calculation

**User Story:** As a Credit Officer, I want the system to calculate an overall risk score, so that I can quickly assess application risk level.

#### Acceptance Criteria

1. WHEN all Five Cs assessments are complete, THEN the Credit_Engine SHALL calculate a composite risk score from 0 to 100
2. WHEN calculating the risk score, THEN the Credit_Engine SHALL weight each of the Five Cs according to configured weights
3. WHEN the risk score is below 40, THEN the Credit_Engine SHALL classify the application as high risk
4. WHEN the risk score is between 40 and 70, THEN the Credit_Engine SHALL classify the application as medium risk
5. WHEN the risk score is above 70, THEN the Credit_Engine SHALL classify the application as low risk

### Requirement 11: Loan Amount Recommendation

**User Story:** As a Credit Officer, I want the system to recommend a maximum loan amount, so that I have a data-driven lending limit.

#### Acceptance Criteria

1. WHEN EBITDA is available, THEN the Credit_Engine SHALL calculate maximum loan amount as 0.4 multiplied by EBITDA
2. WHEN collateral value is lower than calculated loan amount, THEN the Credit_Engine SHALL cap the recommendation at 75% of collateral value
3. WHEN DSCR is below 1.25, THEN the Credit_Engine SHALL reduce the recommended loan amount proportionally
4. WHEN loan amount is calculated, THEN the Credit_Engine SHALL provide a breakdown of the calculation methodology
5. WHEN multiple limiting factors exist, THEN the Credit_Engine SHALL apply the most conservative constraint

### Requirement 12: Interest Rate Determination

**User Story:** As a Credit Officer, I want the system to recommend an appropriate interest rate, so that pricing reflects the risk level.

#### Acceptance Criteria

1. WHEN risk score is calculated, THEN the Credit_Engine SHALL determine interest rate as base rate plus risk premium
2. WHEN risk score is below 40, THEN the Credit_Engine SHALL apply a risk premium of at least 5 percentage points
3. WHEN risk score is between 40 and 70, THEN the Credit_Engine SHALL apply a risk premium between 2 and 5 percentage points
4. WHEN risk score is above 70, THEN the Credit_Engine SHALL apply a risk premium between 0 and 2 percentage points
5. WHEN interest rate is determined, THEN the Credit_Engine SHALL document the base rate and risk premium components

### Requirement 13: Explainable Recommendations

**User Story:** As a Credit Officer, I want to understand why the system made specific recommendations, so that I can justify decisions to stakeholders.

#### Acceptance Criteria

1. WHEN a recommendation is generated, THEN the Credit_Engine SHALL provide explanations for each component of the decision
2. WHEN explaining risk scores, THEN the Credit_Engine SHALL identify the top three factors contributing to the score
3. WHEN explaining loan amount, THEN the Credit_Engine SHALL show which constraint was the limiting factor
4. WHEN explaining interest rate, THEN the Credit_Engine SHALL document which risk factors drove the premium
5. WHEN generating explanations, THEN the Credit_Engine SHALL cite specific data points and their sources

### Requirement 14: CAM Document Generation

**User Story:** As a Credit Officer, I want the system to generate a formatted Credit Appraisal Memo, so that I can present the analysis to the credit committee.

#### Acceptance Criteria

1. WHEN all analysis is complete, THEN the CAM_Generator SHALL produce a document with all required sections
2. WHEN generating the CAM, THEN the CAM_Generator SHALL include Executive Summary, Company Overview, Industry Analysis, Financial Analysis, Risk Assessment, Five Cs Summary, Final Recommendation, and Explainability Notes sections
3. WHEN the CAM is created, THEN the CAM_Generator SHALL support export to both Word and PDF formats
4. WHEN formatting the CAM, THEN the CAM_Generator SHALL follow standard banking CAM templates used in Indian financial institutions
5. WHEN the CAM includes data, THEN the CAM_Generator SHALL format financial tables and ratios in a clear, readable manner

### Requirement 15: Audit Trail and Traceability

**User Story:** As a Credit Officer, I want the system to maintain an audit trail, so that I can track all data sources and decisions.

#### Acceptance Criteria

1. WHEN data is ingested, THEN the CAM_Generator SHALL record the source, timestamp, and extraction method
2. WHEN research is performed, THEN the CAM_Generator SHALL log all URLs accessed and data retrieved
3. WHEN calculations are made, THEN the CAM_Generator SHALL document the formulas and input values used
4. WHEN the CAM is generated, THEN the CAM_Generator SHALL include a complete audit trail section
5. WHEN any data is modified, THEN the CAM_Generator SHALL record who made the change and when

### Requirement 16: Financial Ratio Calculations

**User Story:** As a Credit Officer, I want the system to calculate standard financial ratios, so that I can assess financial health comprehensively.

#### Acceptance Criteria

1. WHEN financial statements are available, THEN the Credit_Engine SHALL calculate DSCR, Debt-to-Equity ratio, and LTV
2. WHEN calculating ratios, THEN the Credit_Engine SHALL use consistent accounting periods across all calculations
3. WHEN ratios are calculated, THEN the Credit_Engine SHALL compare them against industry benchmarks
4. WHEN ratio trends are analyzed, THEN the Credit_Engine SHALL calculate year-over-year changes for the past three years
5. WHEN ratios fall outside acceptable ranges, THEN the Credit_Engine SHALL flag them with severity indicators

### Requirement 17: Document Parsing Accuracy

**User Story:** As a Credit Officer, I want high accuracy in document extraction, so that I can trust the automated analysis.

#### Acceptance Criteria

1. WHEN extracting data from structured documents, THEN the Data_Ingestor SHALL achieve minimum 90% accuracy
2. WHEN extracting data from scanned PDFs with OCR, THEN the Data_Ingestor SHALL achieve minimum 85% accuracy
3. WHEN extraction confidence is below 70% for any field, THEN the Data_Ingestor SHALL flag the field for manual review
4. WHEN parsing completes, THEN the Data_Ingestor SHALL provide a confidence score for each extracted field
5. WHEN errors are detected, THEN the Data_Ingestor SHALL allow Credit Officers to correct and retrain the extraction model

### Requirement 18: Indian Financial Document Support

**User Story:** As a Credit Officer in India, I want the system to understand Indian financial documents, so that it works with local formats and regulations.

#### Acceptance Criteria

1. WHEN processing GST returns, THEN the Data_Ingestor SHALL parse both GSTR-2A and GSTR-3B formats correctly
2. WHEN analyzing MCA filings, THEN the Data_Ingestor SHALL extract company registration details, director information, and financial filings
3. WHEN checking credit history, THEN the Credit_Engine SHALL integrate with CIBIL commercial credit bureau APIs
4. WHEN calculating ratios, THEN the Credit_Engine SHALL follow Indian accounting standards (Ind AS)
5. WHEN generating CAMs, THEN the CAM_Generator SHALL use terminology and formats familiar to Indian banking professionals

### Requirement 19: End-to-End Demo Workflow

**User Story:** As a Credit Officer, I want to process a complete loan application from upload to CAM generation, so that I can efficiently evaluate borrowers.

#### Acceptance Criteria

1. WHEN a user uploads a company annual report, THEN the Data_Ingestor SHALL automatically extract all financial data
2. WHEN financial extraction completes, THEN the Research_Agent SHALL automatically search for litigation and news
3. WHEN research completes, THEN the Credit_Engine SHALL automatically compute Five Cs scoring
4. WHEN scoring completes, THEN the CAM_Generator SHALL automatically generate a complete CAM with loan recommendation
5. WHEN the workflow completes, THEN the system SHALL present the final CAM to the user within 5 minutes of initial upload
