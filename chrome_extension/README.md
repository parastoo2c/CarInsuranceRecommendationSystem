# Chrome Extension - Insurance Recommender

Quick access Chrome extension for getting insurance recommendations.

## Features

- Lightweight popup interface
- Direct integration with Flask API
- Quick recommendations (Top 3)
- Link to full Django dashboard for details

## Installation

### Development Mode

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome_extension` directory

### Usage

1. Click the extension icon in your Chrome toolbar
2. Enter vehicle details and ZIP code
3. Click "Get Recommendations"
4. View Top 3 results instantly
5. Click "View Full Dashboard" for detailed analysis

## Configuration

Edit `popup.js` to change API endpoints:

```javascript
const FLASK_API_URL = 'http://localhost:5000/api/recommend';
const DJANGO_URL = 'http://localhost:8000';
```

For production deployment, update these URLs to your deployed service URLs.

## Icon Assets

Place icon files in `icons/` directory:
- `icon16.png` - 16x16px
- `icon48.png` - 48x48px
- `icon128.png` - 128x128px

You can create simple placeholder icons or use a proper icon design tool.

## Permissions

The extension requires:
- `storage` - To remember your last search
- `host_permissions` - To call Flask API (localhost during development)

## Manifest V3

This extension uses Manifest V3 (latest Chrome extension standard).

## Future Enhancements

- [ ] Preference weight customization in popup
- [ ] Recent searches history
- [ ] Bookmarking favorite plans
- [ ] Comparison mode (side-by-side)

