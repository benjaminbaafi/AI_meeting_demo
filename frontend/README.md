# TranscribeAI Frontend

A modern, responsive web application for AI-powered audio and video transcription.

## 🚀 Project Structure

```
transcribeAI/
├── index.html              # Landing/home page
├── css/
│   ├── main.css           # Core styles & design tokens
│   └── components.css     # Reusable component styles
├── js/
│   ├── main.js            # Main application logic
│   ├── theme.js           # Dark mode management
│   ├── upload.js          # File upload & recording
│   ├── recording.js       # Live recording manager
│   ├── processing.js      # Processing state management
│   └── results.js         # Results dashboard manager
├── pages/
│   ├── upload.html        # Upload/record interface
│   ├── recording.html     # Live recording interface
│   ├── processing.html    # Processing status tracker
│   ├── results.html       # Results dashboard
│   ├── transcriptions.html # Transcription history
│   └── account.html       # User account settings
└── assets/
    └── images/            # Image assets (if needed)
```

## ✨ Features

- **Modern UI/UX**: Clean, professional interface built with Tailwind CSS
- **Dark Mode**: Toggle between light and dark themes with localStorage persistence
- **Responsive Design**: Mobile-first approach that works on all devices
- **File Upload**: Drag-and-drop file upload with progress tracking
- **Audio/Video Recording**: Built-in media recording capabilities
- **Multiple Pages**: Complete navigation between home, upload, transcriptions, and account pages
- **Modular Code**: Separated CSS and JavaScript for easy maintenance

## 🎨 Design System

### Colors
- Primary: `#2463eb` (Blue)
- Background Light: `#f6f6f8`
- Background Dark: `#111621`

### Typography
- Font Family: Inter (Google Fonts)
- Material Symbols Outlined for icons

### Supported File Formats
- Audio: MP3, WAV, M4A, OGG
- Video: MP4, MOV, WEBM

## 🛠️ Getting Started

### Prerequisites
- A modern web browser (Chrome, Firefox, Safari, Edge)
- No build tools required - pure HTML/CSS/JS

### Running the Project

1. **Open in Browser**
   - Simply open `index.html` in your web browser
   - Or use a local development server:

   ```powershell
   # Using Python
   python -m http.server 8000
   
   # Using Node.js (http-server)
   npx http-server
   ```

2. **Navigate the Application**
   - **Home** (`index.html`): Landing page with feature highlights
   - **Upload** (`pages/upload.html`): Upload or record audio/video
   - **My Transcriptions** (`pages/transcriptions.html`): View transcription history
   - **Account** (`pages/account.html`): Manage account settings

## 📁 File Details

### HTML Pages

#### `index.html`
- Landing page with hero section
- Feature highlights (Fast, Accurate, Secure)
- Supported file formats display
- Call-to-action buttons

#### `pages/upload.html`
- Drag-and-drop upload zone
- File browser button
- Audio/video recording buttons (redirect to recording page)
- Upload progress tracker
- Redirects to processing page on completion

#### `pages/recording.html`
- Media type selector (Video & Audio, Audio Only, Screen)
- Live preview with camera/screen feed
- Recording timer with elapsed time
- Recording controls (Start/Stop, Pause/Resume, Cancel)
- Permission handling for media access
- Recording indicator with pulsing dot
- Redirects to processing page after recording

#### `pages/processing.html`
- Animated processing status display
- Progress bar with percentage
- Step-by-step checklist (Upload → Transcribe → Analyze → Generate)
- Estimated time remaining
- Cancel button with confirmation
- Redirects to results page on completion

#### `pages/results.html`
- Video player with playback controls
- Transcription panel with timestamp navigation and search
- AI summary with copy and regenerate buttons
- Action items panel with checkboxes and priority indicators
- Export functionality for all content
- Share button for collaboration

#### `pages/transcriptions.html`
- List of transcription history
- Search and filter functionality
- View and download options

#### `pages/account.html`
- Profile information management
- Subscription plan details
- User preferences (dark mode, notifications)
- Account deletion option

### CSS Files

#### `css/main.css`
- CSS variables for theming
- Base styles and typography
- Layout utilities
- Responsive breakpoints

#### `css/components.css`
- Header/navigation styles
- Button variants
- Card components
- Upload zone styles
- Progress bar styles
- Theme toggle button

### JavaScript Files

#### `js/main.js`
- Application initialization
- Global event handlers
- Utility functions (formatFileSize, formatDuration, debounce)

#### `js/theme.js`
- Dark mode toggle logic
- Theme persistence (localStorage)
- System theme detection

#### `js/upload.js`
- File upload handling
- Drag-and-drop functionality
- File validation (format, size)
- Progress tracking
- Audio/video recording (MediaRecorder API)
- Redirects to processing page

#### `js/processing.js`
- Processing state management
- Progress bar updates
- Step status tracking
- Time estimation
- Cancel processing with confirmation
- Simulated processing for demo
- Redirects to results page

#### `js/results.js`
- Transcription search and filtering
- Video player controls
- Timestamp navigation
- Action items management (add, toggle, delete)
- Summary copy to clipboard
- AI summary regeneration
- Export functionality
- Share feature

## 🔧 Customization

### Changing Colors
Edit the CSS variables in `css/main.css`:
```css
:root {
    --color-primary: #2463eb;
    --color-background: #f6f6f8;
    /* ... */
}
```

### Adding New Pages
1. Create a new HTML file in the `pages/` directory
2. Copy the header structure from existing pages
3. Link to the new page in navigation
4. Add page-specific content

### Modifying Upload Behavior
Edit `js/upload.js` to:
- Change file size limits (`maxFileSize`)
- Add/remove allowed formats (`allowedFormats`)
- Customize upload API endpoint
- Implement actual recording functionality

## 🌐 External Dependencies

The project uses CDN-hosted dependencies:
- **Tailwind CSS**: `https://cdn.tailwindcss.com`
- **Google Fonts** (Inter): Google Fonts API
- **Material Symbols**: Google Fonts API

All dependencies load from CDN - no local installation required.

## 📱 Browser Compatibility

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

## 🔐 Security Considerations

- File uploads are client-side only (no backend yet)
- Implement server-side validation when connecting to backend
- Use HTTPS in production
- Sanitize user inputs before processing

## 🚧 Future Enhancements

- [ ] Backend API integration
- [ ] Real file upload to server
- [ ] Actual transcription processing
- [ ] User authentication
- [ ] Payment integration for upgrades
- [ ] Export transcriptions (TXT, PDF, DOCX)
- [ ] Speaker identification
- [ ] Timestamp markers

## 📄 License

This project is part of the TranscribeAI application.

## 👨‍💻 Developer Notes

- All pages use the same header component (consider extracting to a template)
- JavaScript modules are independent and can be loaded as needed
- Dark mode persists across sessions using localStorage
- Progress tracking is simulated (replace with actual upload logic)
- Recording functionality requires user permissions (microphone/camera)

---

**Ready to use!** Open `index.html` to start exploring the application.
