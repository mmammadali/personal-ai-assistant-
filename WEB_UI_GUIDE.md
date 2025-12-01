# 🌐 Iranian Manager Assistant - Web Interface Guide

## Overview

A professional, modern chat interface for the Iranian Manager Personal Assistant with ChatGPT-style design.

## Features

### 🎨 User Interface
- **Modern Design**: Clean, minimalist interface inspired by ChatGPT
- **Dark/Light Mode**: Toggle between themes with persistent preferences
- **Responsive**: Works seamlessly on desktop, tablet, and mobile devices
- **Smooth Animations**: Typing indicators, message transitions, and smooth scrolling
- **Quick Actions**: Pre-defined prompts for common tasks

### 💬 Chat Features
- **Real-time Messaging**: Instant communication with the AI assistant
- **Message History**: Persistent conversation threads per user session
- **Confirmation Dialogs**: Visual badges for human-in-the-loop approvals
- **Rich Formatting**: Support for emojis, bold text, and line breaks
- **Auto-scroll**: Automatically scrolls to the latest message

### 🛠️ Functionality
- **Event Management**: Create and retrieve calendar events
- **Task Management**: Create, retrieve, and update tasks
- **Jalali Calendar**: Full support for Persian/Jalali dates
- **Multi-language**: Supports both English and Persian/Farsi
- **Session Management**: Each user gets a unique conversation thread

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variable

Set your OpenAI API key:

**Windows:**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=your-api-key-here
```

### 3. Run the Application

```bash
python app.py
```

The server will start at: http://127.0.0.1:5000

## Usage

### Starting a Conversation

1. Open your browser and navigate to http://127.0.0.1:5000
2. You'll see a welcome screen with quick action buttons
3. Click any quick action or type your message in the input box
4. Press Enter or click the send button

### Quick Actions

The interface provides 4 quick action buttons:

1. **View Events** - Show all your calendar events
2. **View Tasks** - Display all your tasks
3. **New Event** - Start creating a new event
4. **Current Date** - Get the current Jalali date

### Managing Events

**Create an Event:**
```
Create a meeting for 1403-09-15 with title "Budget Review" with attendee "Ali Rezaei"
```

**Retrieve Events:**
```
Show me all events for 1403-09-15
```

### Managing Tasks

**Create a Task:**
```
Create a task to finish quarterly report by 1403-09-20 for project "Q4 Analysis"
```

**View Tasks:**
```
Show me all tasks for Q4 Analysis project
```

**Update Task Status:**
```
Mark the task for Q4 Analysis as done
```

### Human-in-the-Loop Confirmations

When you create or update events/tasks:

1. The assistant will show a **Confirmation Required** badge
2. Review the details
3. Reply with "yes" or "بله" to confirm
4. Reply with "no" or "خیر" to cancel

### Dark Mode

Click the moon/sun icon in the header to toggle between light and dark themes. Your preference is saved automatically.

### Clear Conversation

Click the trash icon in the header to start a new conversation thread.

## Keyboard Shortcuts

- **Enter**: Send message
- **Shift + Enter**: New line in message input

## API Endpoints

The web interface exposes several REST API endpoints:

### POST /api/chat
Send a message to the assistant

**Request:**
```json
{
  "message": "Show me my events"
}
```

**Response:**
```json
{
  "response": "📅 Found 2 event(s): ...",
  "is_confirmation": false,
  "timestamp": "14:30"
}
```

### GET /api/history
Get conversation history for the current session

**Response:**
```json
{
  "history": [
    {
      "user": "Show events",
      "assistant": "Here are your events..."
    }
  ]
}
```

### POST /api/clear
Clear the current conversation session

**Response:**
```json
{
  "success": true,
  "message": "Conversation cleared"
}
```

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "Iranian Manager Assistant"
}
```

## Design Philosophy

The interface follows modern chat UI best practices:

1. **Clarity**: Clean, uncluttered design with focus on conversation
2. **Simplicity**: Intuitive controls with minimal learning curve
3. **Responsiveness**: Smooth animations and instant feedback
4. **Accessibility**: High contrast colors, readable fonts
5. **Consistency**: Familiar patterns from popular chat applications

## Customization

### Colors

Edit `static/css/style.css` to customize the color scheme. CSS variables are defined in the `:root` section:

```css
:root {
    --accent-primary: #10a37f;  /* Main brand color */
    --accent-secondary: #1a7f64;  /* Hover states */
    /* ... more variables */
}
```

### Quick Actions

Modify quick action buttons in `templates/chat.html`:

```html
<button class="action-card" data-prompt="Your custom prompt">
    <i class="fas fa-your-icon"></i>
    <span>Your Label</span>
</button>
```

### Layout

Adjust the maximum width in `static/css/style.css`:

```css
.container {
    max-width: 1200px; /* Change this value */
}
```

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, change it in `app.py`:

```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Use different port
```

### OpenAI API Key Error

Ensure your API key is set correctly:

```bash
# Verify it's set
echo %OPENAI_API_KEY%  # Windows
echo $OPENAI_API_KEY   # Linux/Mac
```

### Database Issues

The application uses SQLite. If you encounter database errors, delete `assistant.db` and restart:

```bash
rm assistant.db  # Linux/Mac
del assistant.db  # Windows
python app.py
```

## Performance Tips

1. **Caching**: Browser automatically caches static assets (CSS, JS)
2. **Session Management**: Sessions are stored in memory; restart clears all
3. **Database**: SQLite is used for simplicity; consider PostgreSQL for production

## Security Notes

⚠️ **Important for Production:**

1. Change the Flask secret key in `app.py`
2. Use environment variables for sensitive data
3. Enable HTTPS with a reverse proxy (nginx, Apache)
4. Implement rate limiting for API endpoints
5. Add authentication/authorization if needed

## Browser Compatibility

Tested and working on:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements

Potential features for future versions:

- [ ] File attachments
- [ ] Voice input
- [ ] Export conversation history
- [ ] Multi-user authentication
- [ ] Conversation search
- [ ] Custom themes
- [ ] Notification system
- [ ] WebSocket support for real-time updates

## Support

For issues or questions:
1. Check the console logs (F12 in browser)
2. Review server logs in the terminal
3. Verify all dependencies are installed
4. Ensure OpenAI API key is valid

## License

This web interface is part of the Iranian Manager Personal Assistant project.

---

**Enjoy your new professional chat interface! 🎉**



