# Migration Checklist

This checklist helps you migrate from the old structure to the new restructured architecture.

## Phase 1: Preparation ✅ (Complete)

- [x] New directory structure created
- [x] Files copied to new locations
- [x] Documentation written
- [x] Setup scripts created
- [x] Backward compatibility maintained

## Phase 2: Verification (Current Phase)

### Backend Verification

- [ ] Start backend server
  ```bash
  cd backend
  source venv/bin/activate
  uvicorn app.main:app --reload
  ```
- [ ] Verify API endpoints work at http://localhost:8000/docs
- [ ] Test document upload endpoint
- [ ] Test credit assessment endpoint
- [ ] Test CAM generation endpoint
- [ ] Check database connections
- [ ] Review logs for errors

### Frontend Verification

- [ ] Start frontend server
  ```bash
  cd frontend
  npm run dev
  ```
- [ ] Verify dashboard loads at http://localhost:5173
- [ ] Test navigation between pages
- [ ] Test document upload flow
- [ ] Test results display
- [ ] Check browser console for errors
- [ ] Verify API calls are working

### AI Pipeline Verification

- [ ] Verify all modules are importable
  ```bash
  cd backend
  source venv/bin/activate
  python -c "from ai_pipeline.document_processing.pdf_extractor import DocumentParser; print('OK')"
  python -c "from ai_pipeline.credit_model.five_cs_analyzer import FiveCsAnalyzer; print('OK')"
  python -c "from ai_pipeline.research_agent.web_crawler import WebCrawler; print('OK')"
  python -c "from ai_pipeline.cam_generator.cam_generator import CAMGenerator; print('OK')"
  ```
- [ ] Test document processing with sample file
- [ ] Test credit scoring
- [ ] Test CAM generation

### Testing

- [ ] Run backend unit tests
  ```bash
  cd backend
  pytest tests/unit/ -v
  ```
- [ ] Run backend integration tests
  ```bash
  pytest tests/integration/ -v
  ```
- [ ] Run frontend tests
  ```bash
  cd frontend
  npm test
  ```
- [ ] Run property-based tests
  ```bash
  cd backend
  pytest tests/property/ -v
  ```

## Phase 3: Import Migration (Optional)

### Step 1: Update Backend Imports

Create a branch for migration:
```bash
git checkout -b feature/migrate-to-new-structure
```

#### Update imports in backend/app/api/routes/

- [ ] `applications.py`
  ```python
  # Old
  from app.services.data_ingestor.document_parser import DocumentParser
  
  # New
  from ai_pipeline.document_processing.pdf_extractor import DocumentParser
  ```

- [ ] `processing.py`
  ```python
  # Old
  from app.services.credit_engine.five_cs_analyzer import FiveCsAnalyzer
  
  # New
  from ai_pipeline.credit_model.five_cs_analyzer import FiveCsAnalyzer
  ```

- [ ] `cam.py`
  ```python
  # Old
  from app.services.cam_generator.cam_generator import CAMGenerator
  
  # New
  from ai_pipeline.cam_generator.cam_generator import CAMGenerator
  ```

#### Update imports in backend/app/services/

- [ ] `workflow_orchestrator.py`
  - Update all service imports to use ai_pipeline

#### Update imports in tests/

- [ ] Update all test files to import from ai_pipeline
- [ ] Run tests after each update
- [ ] Fix any import errors

### Step 2: Update Frontend Imports

#### Update component imports

- [ ] Update `App.tsx` to import from new locations
- [ ] Update existing pages to use new components
- [ ] Update all API client imports to use `services/api`

Example updates:
```typescript
// Old
import { apiClient } from '../../api/client';
import { FiveCsScorecard } from '../pages/Analysis/FiveCsScorecard';

// New
import { apiClient } from '../services/api';
import { FiveCsScorecard } from '../pages/Analysis/FiveCsScorecard';
```

### Step 3: Test After Migration

- [ ] Run all backend tests
- [ ] Run all frontend tests
- [ ] Test full application flow
- [ ] Check for console errors
- [ ] Verify all features work

## Phase 4: Cleanup (After Verification)

### Remove Old Files (Only after everything works!)

- [ ] Backup current working state
  ```bash
  git commit -am "Backup before cleanup"
  ```

- [ ] Remove old backend service files
  ```bash
  # Only if new imports are working!
  rm -rf backend/app/services/data_ingestor/
  rm -rf backend/app/services/credit_engine/
  rm -rf backend/app/services/cam_generator/
  rm -rf backend/app/services/research_agent/
  ```

- [ ] Remove old frontend files (if duplicated)
  ```bash
  # Only if new structure is working!
  # Review each file before deleting
  ```

- [ ] Update .gitignore if needed

- [ ] Commit changes
  ```bash
  git add .
  git commit -m "Complete migration to new structure"
  ```

## Phase 5: Documentation Update

- [ ] Update main README.md to reference new structure
- [ ] Update API documentation
- [ ] Update deployment documentation
- [ ] Update team wiki/confluence
- [ ] Notify team of new structure

## Phase 6: CI/CD Update

- [ ] Update CI/CD pipeline configurations
- [ ] Update Docker configurations if needed
- [ ] Update deployment scripts
- [ ] Test CI/CD pipeline
- [ ] Update monitoring/logging paths

## Rollback Plan

If issues arise during migration:

1. **Immediate Rollback**:
   ```bash
   git checkout main
   git branch -D feature/migrate-to-new-structure
   ```

2. **Partial Rollback**:
   ```bash
   git revert <commit-hash>
   ```

3. **Keep Both Structures**:
   - Old structure continues to work
   - New structure available for gradual adoption
   - No breaking changes

## Success Criteria

Migration is successful when:

- [ ] All tests pass
- [ ] Application runs without errors
- [ ] All features work as expected
- [ ] Performance is maintained or improved
- [ ] Team understands new structure
- [ ] Documentation is complete
- [ ] CI/CD pipeline works

## Timeline Suggestion

- **Week 1**: Verification phase (Phase 2)
- **Week 2**: Import migration (Phase 3)
- **Week 3**: Testing and fixes
- **Week 4**: Cleanup and documentation (Phase 4-5)
- **Week 5**: CI/CD update and deployment (Phase 6)

## Support

If you encounter issues:

1. Check `RESTRUCTURE_SUMMARY.md` for details
2. Review `docs/architecture.md` for structure
3. Check `docs/system_design.md` for implementation details
4. Create an issue on GitHub
5. Contact the team lead

## Notes

- **No Rush**: Take time to verify each step
- **Test Frequently**: Run tests after each change
- **Communicate**: Keep team informed of progress
- **Document Issues**: Note any problems encountered
- **Backup**: Always have a working backup

---

**Current Status**: Phase 1 Complete ✅
**Next Step**: Phase 2 Verification
**Estimated Time**: 2-4 weeks for full migration
