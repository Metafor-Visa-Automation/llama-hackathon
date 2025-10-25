# TODO List - Visa Application System

## High Priority

### AI Service Integration
- [ ] Replace mock data in `FillForm.jsx` with actual AI service call
- [ ] Create API endpoint `/api/visa-requirements` that accepts:
  - `originCountry` (ISO2 code)
  - `destinationCountry` (ISO2 code)
- [ ] API should return action_steps in the same format as `response-fransa.json`
- [ ] Add error handling for AI service failures
- [ ] Add loading states during AI processing
- [ ] Implement retry logic for failed AI calls

### Document Upload Backend
- [ ] Create backend endpoint to handle document uploads
- [ ] Implement secure file storage (e.g., AWS S3, Firebase Storage)
- [ ] Add file validation (size limits, file types)
- [ ] Generate unique identifiers for uploaded documents
- [ ] Link documents to user applications in database

### Form Submission
- [ ] Create backend endpoint to save form submissions
- [ ] Store both text answers and document references
- [ ] Link submissions to user accounts
- [ ] Send confirmation email after submission
- [ ] Generate application reference number

## Medium Priority

### Dashboard Integration
- [ ] Display submitted applications on Dashboard
- [ ] Show application status (pending, processing, approved, rejected)
- [ ] Allow users to view their submitted documents
- [ ] Enable document re-upload if needed
- [ ] Add timeline/progress tracker for applications

### User Experience
- [ ] Add form validation messages
- [ ] Implement auto-save functionality
- [ ] Add "Save & Continue Later" option
- [ ] Show estimated completion time
- [ ] Add progress indicators per section

## Low Priority

### Analytics & Monitoring
- [ ] Track form completion rates
- [ ] Monitor AI service performance
- [ ] Log document upload success/failure rates
- [ ] Add user feedback collection

### Enhancements
- [ ] Multi-language support
- [ ] PDF generation of completed forms
- [ ] Document preview before upload
- [ ] Batch document upload
- [ ] Mobile responsive optimizations

## Technical Debt
- [ ] Add unit tests for form logic
- [ ] Add integration tests for AI service
- [ ] Optimize document upload performance
- [ ] Add TypeScript types for better type safety
- [ ] Improve error boundaries

## Notes
- Current implementation uses mock data from `ai_responses/response-fransa.json`
- Document upload is client-side only (files not persisted)
- Form submission currently shows alert, needs backend integration

