# Hindi Voice Setup Guide

## Problem
The browser's Web Speech API requires Hindi TTS (Text-to-Speech) voices to be installed on your operating system. Most systems don't have Hindi voices installed by default.

## Solutions

### Option 1: Install Hindi Voices on Windows (Recommended)

1. **Open Windows Settings**
   - Press `Win + I` or click Start → Settings

2. **Go to Time & Language**
   - Click on "Time & Language"
   - Select "Language & region" from the left sidebar

3. **Add Hindi Language**
   - Click "Add a language"
   - Search for "Hindi" and select "हिंदी (Hindi)"
   - Click "Next" and then "Install"

4. **Install Speech Pack**
   - After installing Hindi, click on it
   - Click "Options"
   - Under "Speech", click "Download" to install the Hindi speech pack

5. **Restart Browser**
   - Close and reopen your browser
   - The Hindi voice should now be available

### Option 2: Use Chrome/Edge with Google TTS

Chrome and Edge browsers have better TTS support:
- They may have some Hindi voices available by default
- Try switching to Chrome or Edge if you're using a different browser

### Option 3: Check Available Voices

1. Open your browser's Developer Console (F12)
2. Go to the Console tab
3. Type: `speechSynthesis.getVoices().map(v => ({name: v.name, lang: v.lang}))`
4. This will show all available voices and their language codes
5. Look for any voice with "hi" in the language code

### Option 4: Use English for Voice, Hindi for Text

If Hindi voices are not available, you can:
- Keep the language set to Hindi for text responses
- Switch to English when you want voice responses
- The text chat will still work perfectly in Hindi

## Testing

After installing Hindi voices:
1. Refresh the page (F5)
2. Open the browser console (F12)
3. You should see "Hindi voices found:" in the console if voices are detected
4. Try asking a question in Hindi and check if the voice works

## Troubleshooting

- **No Hindi voices after installation**: Restart your browser completely
- **Voice still not working**: Check the browser console for error messages
- **Only English voices available**: Your system may not support Hindi TTS. Consider using Option 4 above.

