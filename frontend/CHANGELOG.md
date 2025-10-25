# Changelog

## [Unreleased] - 2025-10-25

### ✨ Added
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

