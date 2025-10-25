# Changelog

## [Unreleased] - 2025-10-25

### 🎯 Latest Update: Progress Stepper & Redux Integration

#### ✨ Added
- **Interactive Progress Stepper**: Modern stepper UI at the top of the form
  - Click on any step to navigate to that question
  - Visual indicators for completed, current, and pending questions
  - Real-time progress percentage
  - Category pills showing question metadata
  - Sticky positioning for always-visible progress
- **Redux State Management**: Centralized form state management
  - `formSlice`: New Redux slice for form data
  - Answers stored in Redux (persists across navigation)
  - Documents stored locally (to avoid Redux size issues)
  - Completed questions tracking
  - Form metadata (timestamps, costs, duration)
- **Smart Question Completion**: Automatic tracking of completed questions
  - Real-time validation
  - Visual feedback in stepper
  - Progress updates automatically

#### 🎨 UI Improvements
- **Stepper Design**:
  - Glassmorphism effect with backdrop blur
  - Smooth animations and transitions
  - Color-coded status (Green=completed, Blue=current, Gray=pending)
  - Hover effects on clickable steps
  - Progress bar with animated fill
- **Layout Changes**:
  - Progress moved from bottom to top
  - Sticky header for constant visibility
  - Wider content area (900px)
  - Better spacing and padding

#### 🔧 Technical Details
- **Redux Actions**:
  - `setQuestions`: Initialize questions array
  - `setAnswer`: Store text answers
  - `goToQuestion`: Navigate to specific question
  - `nextQuestion/previousQuestion`: Sequential navigation
  - `markQuestionComplete/Incomplete`: Track completion
  - `resetForm`: Clear all form data
- **State Architecture**:
  ```javascript
  Redux Store:
  - questions: Array<Question>
  - answers: Object<questionId: string>
  - currentQuestionIndex: number
  - completedQuestions: Array<number>
  - formMetadata: Object
  
  Local State:
  - documents: Object<questionId: Array<File>>
  ```

---

### ✨ Previous Features
- **Multiple Document Upload Support**: Users can now upload multiple documents for each document-required question
- **Source URLs Display**: Each question now shows relevant source URLs at the bottom for transparency
- **Modern Document Cards**: Beautiful UI for uploaded documents with:
  - File type icons with color coding (PDF=red, DOC=blue, Images=green)
  - File size display
  - Individual remove buttons
  - Hover effects and animations
  - Grid layout for multiple documents
  - Document counter badge

### 🎨 Improved
- **Upload Area UX**: 
  - Drag & drop support for multiple files
  - Dynamic upload area that adapts when documents are added
  - "Add more documents" button after first upload
  - Multiple file selection support
- **Question Card Layout**:
  - Better spacing and organization
  - Source URLs in a dedicated section with link icon
  - Responsive grid for document cards
  - File info display with ellipsis for long names

### 🔧 Technical Changes
- Changed `document` prop to `documents` (array) in QuestionCard
- Changed `onDocumentChange` to `onDocumentAdd` and `onDocumentRemove`
- Updated validation logic to check for array length
- Added file size formatter utility
- Added file color mapper for visual distinction
- Support for PDF, JPG, JPEG, PNG, DOC, DOCX formats

### 📝 UI Components Updated
- `QuestionCard.jsx`: Complete rewrite of document upload section
- `FillForm.jsx`: State management updated for multiple documents per question

### 🎯 Features in Detail

#### Multiple Document Upload
```javascript
// Before: Single document
document: File

// After: Multiple documents
documents: Array<File>
```

Each document-required question can now accept multiple files:
- Drag & drop multiple files at once
- Click to select multiple files from file picker
- Visual cards for each uploaded file
- Individual remove buttons for each file
- Document counter showing total uploaded files

#### Source URLs
Each question displays up to 3 source URLs with:
- Link icon indicator
- Clickable URLs that open in new tab
- URL truncation for long URLs
- "+X more" indicator if more than 3 sources
- Subtle styling in a dedicated box

### 🚀 Usage Example

```jsx
<QuestionCard
  question={{
    title: "Geçerli Pasaport",
    description: "Pasaportunuz en az 6 ay süreyle geçerli olmalı.",
    requires_document: true,
    source_urls: ["https://example.com", "https://example2.com"]
  }}
  documents={[file1, file2, file3]}
  onDocumentAdd={(file) => addFile(file)}
  onDocumentRemove={(index) => removeFile(index)}
  // ... other props
/>
```

### 📱 Responsive Design
- Document cards use CSS Grid with auto-fill
- Minimum card width: 240px
- Responsive gap and padding
- Mobile-friendly touch targets

### 🎨 Color Coding
- **PDF files**: Red (#EF4444)
- **DOC/DOCX files**: Blue (#3B82F6)
- **Image files (JPG/PNG)**: Green (#10B981)
- **Other files**: Gray (#6B7280)

### ⚠️ Validation
- Questions requiring documents must have at least 1 document uploaded
- Users cannot proceed without meeting validation requirements
- Visual feedback with disabled/enabled states

