-- Intelli-Credit Database Schema
-- PostgreSQL Database Schema for Credit Decisioning Engine

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
    application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    loan_amount_requested DECIMAL(15,2),
    loan_purpose TEXT,
    submitted_date TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    company_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cin VARCHAR(21) UNIQUE,
    gstin VARCHAR(15),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    incorporation_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Promoters table
CREATE TABLE IF NOT EXISTS promoters (
    promoter_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    din VARCHAR(8),
    shareholding DECIMAL(5,2),
    role VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    file_path TEXT NOT NULL,
    upload_date TIMESTAMP NOT NULL DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    confidence_score DECIMAL(5,2),
    extracted_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Financial data table
CREATE TABLE IF NOT EXISTS financial_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    period VARCHAR(20) NOT NULL,
    revenue DECIMAL(15,2),
    expenses DECIMAL(15,2),
    ebitda DECIMAL(15,2),
    net_profit DECIMAL(15,2),
    total_assets DECIMAL(15,2),
    total_liabilities DECIMAL(15,2),
    equity DECIMAL(15,2),
    cash_flow DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Research data table
CREATE TABLE IF NOT EXISTS research_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    data_type VARCHAR(50) NOT NULL,
    source_url TEXT,
    content JSONB NOT NULL,
    sentiment VARCHAR(20),
    retrieved_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Credit assessments table
CREATE TABLE IF NOT EXISTS credit_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    risk_score DECIMAL(5,2) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    character_score DECIMAL(5,2),
    capacity_score DECIMAL(5,2),
    capital_score DECIMAL(5,2),
    collateral_score DECIMAL(5,2),
    conditions_score DECIMAL(5,2),
    max_loan_amount DECIMAL(15,2),
    recommended_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Audit trail table
CREATE TABLE IF NOT EXISTS audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID REFERENCES applications(application_id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    user_id UUID,
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_applications_company_id ON applications(company_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_documents_application_id ON documents(application_id);
CREATE INDEX IF NOT EXISTS idx_financial_data_company_id ON financial_data(company_id);
CREATE INDEX IF NOT EXISTS idx_research_data_company_id ON research_data(company_id);
CREATE INDEX IF NOT EXISTS idx_credit_assessments_application_id ON credit_assessments(application_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_application_id ON audit_trail(application_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_timestamp ON audit_trail(timestamp);
