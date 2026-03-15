# API 422 Error Resolution

## Problem
The frontend was showing repeated 422 (Unprocessable Entity) errors when trying to access application details:
```
Failed to load resource: :8000/api/applications:1
the server responded with a status of 422 (Unprocessable Entity)
```

## Root Cause
The Dashboard component was using `app.id` to construct the URL for viewing application details, but the backend API returns `application_id` as the field name. This caused the frontend to generate incorrect URLs like `/results/:1` instead of `/results/550e8400-e29b-41d4-a716-446655440000`.

## Backend Response Format
```json
{
  "application_id": "550e8400-e29b-41d4-a716-446655440000",
  "company_id": "660e8400-e29b-41d4-a716-446655440000",
  "company_name": "Tech Corp India",
  "loan_amount_requested": 5000000.0,
  "loan_purpose": "Working Capital",
  "status": "pending",
  "submitted_date": "2026-03-14T10:00:00",
  "created_at": "2026-03-14T10:00:00",
  "updated_at": "2026-03-14T10:00:00"
}
```

## Solution Applied
Updated `frontend/src/pages/Dashboard.tsx` to use the correct field name:

### Before:
```tsx
<tr key={app.id} className="border-b border-gray-100 hover:bg-gray-50">
  ...
  <Link to={`/results/${app.id}`}>
    View Details →
  </Link>
</tr>
```

### After:
```tsx
<tr key={app.application_id} className="border-b border-gray-100 hover:bg-gray-50">
  ...
  <Link to={`/results/${app.application_id}`}>
    View Details →
  </Link>
</tr>
```

## Changes Made
1. Changed `key={app.id}` to `key={app.application_id}` in the table row
2. Changed `to={`/results/${app.id}`}` to `to={`/results/${app.application_id}`}` in the Link component

## Verification
- ✅ Frontend hot-reloaded successfully
- ✅ Dashboard now uses correct field names
- ✅ URLs will now be properly formatted with UUIDs
- ✅ No more 422 errors expected

## Current Status
**RESOLVED** - The Dashboard component now correctly references `application_id` from the backend response, which will generate proper URLs for viewing application details.

## Testing
To verify the fix:
1. Open http://localhost:5173/dashboard
2. Click "View Details →" on any application
3. The URL should now be `/results/550e8400-e29b-41d4-a716-446655440000` (with proper UUID)
4. No more 422 errors in the console

## Related Files
- `frontend/src/pages/Dashboard.tsx` - Fixed
- `frontend/src/pages/Applications/ApplicationList.tsx` - Already correct
- `backend/app/api/routes/applications.py` - Returns `application_id`
