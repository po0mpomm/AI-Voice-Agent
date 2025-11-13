const API_BASE = "";
const chatContainer = document.getElementById("chat-container");
const micButton = document.getElementById("mic-button");
const textForm = document.getElementById("text-form");
const textInput = document.getElementById("text-input");
const statusIndicator = document.getElementById("status-indicator");
const statusLabel = document.getElementById("status-label");
const toast = document.getElementById("toast");
const template = document.getElementById("message-template");
const languageSelect = document.getElementById("language-select");
const micLabel = micButton ? micButton.querySelector(".mic-label") : null;

const languageCopy = {
  en: {
    user: "You",
    assistant: "Assistant",
    avatarUser: "You",
    avatarAssistant: "AI",
    placeholder: "Type your message here...",
    mic: "Tap to speak",
    recording: "Recording...",
    languageSwitched: "Language set to English.",
  },
  hi: {
    user: "आप",
    assistant: "सहायक",
    avatarUser: "आप",
    avatarAssistant: "एआई",
    placeholder: "अपना संदेश यहाँ लिखें...",
    mic: "बोलने के लिए टैप करें",
    recording: "रिकॉर्डिंग जारी...",
    languageSwitched: "भाषा हिंदी पर बदल दी गई है।",
  },
};

const speechLocales = {
  en: "en-US",
  hi: "hi-IN",
};

let availableVoices = [];
let voicesLoaded = false;

if ("speechSynthesis" in window) {
  const loadVoices = () => {
    availableVoices = window.speechSynthesis.getVoices();
    voicesLoaded = availableVoices.length > 0;
    if (availableVoices.length > 0) {
      console.log("Available voices:", availableVoices.map(v => ({ name: v.name, lang: v.lang })));
      const hindiVoices = availableVoices.filter(v => 
        v.lang?.toLowerCase().includes("hi") || 
        v.name?.toLowerCase().includes("hindi")
      );
      if (hindiVoices.length > 0) {
        console.log("Hindi voices found:", hindiVoices.map(v => ({ name: v.name, lang: v.lang })));
      } else {
        console.log("No Hindi voices found. Available languages:", 
          [...new Set(availableVoices.map(v => v.lang))].filter(Boolean));
      }
    }
  };

  window.speechSynthesis.addEventListener("voiceschanged", loadVoices);
  loadVoices();
  setTimeout(loadVoices, 1000);
}

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let conversation = [];
let conversationId = crypto.randomUUID();
let currentLanguage = languageSelect ? languageSelect.value : "en";

if (languageSelect) {
  languageSelect.addEventListener("change", (event) => {
    currentLanguage = event.target.value;
    resetConversation();
    updateLanguageUI();
    const message = languageCopy[currentLanguage]?.languageSwitched ?? "Language updated.";
    showToast(message);
  });
}

updateLanguageUI();
updateStatus();

async function updateStatus() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error("status error");
    setStatus(true);
  } catch {
    setStatus(false);
    showToast("Server unreachable. Try starting the backend.");
  }
}

function setStatus(connected) {
  statusIndicator.classList.toggle("online", connected);
  statusIndicator.classList.toggle("offline", !connected);
  statusLabel.textContent = connected ? "Connected" : "Connecting...";
}

function showToast(message, duration = 3200) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, duration);
}

function addMessage(role, content, language = currentLanguage) {
  const clone = template.content.cloneNode(true);
  const message = clone.querySelector(".message");
  const header = clone.querySelector(".message-header");
  const textDiv = clone.querySelector(".message-text");
  const avatar = clone.querySelector(".message-avatar");

  message.classList.add(role);
  const copy = languageCopy[language] ?? languageCopy.en;
  header.textContent = role === "user" ? copy.user : copy.assistant;
  
  if (role === "user") {
    avatar.textContent = "👤";
  } else {
    avatar.textContent = "🤖";
  }

  const welcomeScreen = document.getElementById("welcome-screen");
  if (welcomeScreen) {
    welcomeScreen.style.display = "none";
  }

  chatContainer.appendChild(clone);
  
  if (role === "assistant" && window.animations && window.animations.typeWriter) {
    window.animations.typeWriter(textDiv, content, 20);
  } else {
    textDiv.textContent = content;
  }
  
  message.style.animation = "messageSlideIn3D 0.6s ease-out forwards";
  
  chatContainer.scrollTo({
    top: chatContainer.scrollHeight,
    behavior: "smooth",
  });
  
  setTimeout(() => {
    avatar.style.animation = "avatarPulse 1s ease-out";
    setTimeout(() => {
      avatar.style.animation = "";
    }, 1000);
  }, 100);
}

async function sendToChat(prompt) {
  const payload = {
    messages: [...conversation, { role: "user", content: prompt }],
    conversation_id: conversationId,
    language: currentLanguage,
  };

  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await extractErrorMessage(response);
    throw new Error(message);
  }

  const data = await response.json();
  conversation.push({ role: "user", content: prompt });
  conversation.push({ role: "assistant", content: data.response });

  addMessage("assistant", data.response, payload.language);
  speak(data.response, payload.language);
}

function speak(text, language = currentLanguage, attempt = 0) {
  if (!("speechSynthesis" in window)) {
    showToast("Speech synthesis not supported in this browser.");
    return;
  }

  if (!voicesLoaded && attempt < 3) {
    availableVoices = window.speechSynthesis.getVoices();
    voicesLoaded = availableVoices.length > 0;
    setTimeout(() => speak(text, language, attempt + 1), 250);
    return;
  }

  const locale = speechLocales[language] ?? speechLocales.en;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = locale;

  let matchingVoice = null;
  if (language === "hi") {
    const hindiCodes = ["hi-IN", "hi", "hi-in", "hin"];
    for (const code of hindiCodes) {
      matchingVoice = availableVoices.find((option) =>
        option.lang?.toLowerCase().startsWith(code.toLowerCase())
      );
      if (matchingVoice) break;
    }
    
    if (!matchingVoice) {
      matchingVoice = availableVoices.find((option) => {
        const name = option.name?.toLowerCase() || "";
        return name.includes("hindi") || name.includes("hi-") || name.includes("india");
      });
    }
  } else {
    matchingVoice = availableVoices.find((option) =>
      option.lang?.toLowerCase().startsWith(locale.toLowerCase())
    );
  }

  if (matchingVoice) {
    utterance.voice = matchingVoice;
    utterance.lang = matchingVoice.lang || locale;
  } else {
    if (language === "hi") {
      showToast("Hindi voice not available. Please install a Hindi TTS voice pack in your system settings, or use English language for voice responses.");
      console.log("Available voices:", availableVoices.map(v => ({ name: v.name, lang: v.lang })));
      return;
    }
    
    const fallback = availableVoices.find((option) => option.lang?.toLowerCase().startsWith("en"));
    if (fallback) {
      utterance.voice = fallback;
      utterance.lang = fallback.lang;
    } else {
      showToast("No suitable voice found for speech synthesis.");
      return;
    }
  }

  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

async function handleTextSubmit(event) {
  event.preventDefault();
  const value = textInput.value.trim();
  if (!value) return;

  addMessage("user", value, currentLanguage);
  textInput.value = "";

  try {
    await sendToChat(value);
  } catch (error) {
    console.error(error);
    showToast(error.message || "Unable to reach chat service.");
  }
}

async function initMediaRecorder() {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error("Microphone not supported on this device.");
  }

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.addEventListener("dataavailable", (event) => {
    if (event.data.size > 0) {
      audioChunks.push(event.data);
    }
  });

  mediaRecorder.addEventListener("stop", async () => {
    if (!audioChunks.length) return;

    const blob = new Blob(audioChunks, { type: "audio/webm" });
    audioChunks = [];

    const formData = new FormData();
    formData.append("file", blob, "recording.webm");
    formData.append("language", currentLanguage);

    try {
      const response = await fetch(`${API_BASE}/api/transcribe`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response);
        throw new Error(message);
      }

      const { text } = await response.json();
      if (!text.trim()) {
        showToast("Didn't catch that. Try again.");
        return;
      }

      addMessage("user", text, currentLanguage);
      await sendToChat(text);
    } catch (error) {
      console.error(error);
      showToast(error.message || "Voice processing failed.");
    }
  });
}

async function toggleRecording() {
  if (!mediaRecorder) {
    try {
      await initMediaRecorder();
    } catch (error) {
      console.error(error);
      showToast(error.message);
      return;
    }
  }

  if (!mediaRecorder) return;

  if (!isRecording) {
    audioChunks = [];
    mediaRecorder.start();
    isRecording = true;
    micButton.classList.add("recording");
    if (micLabel) {
      micLabel.textContent = languageCopy[currentLanguage]?.recording ?? "Recording...";
    }
  } else {
    mediaRecorder.stop();
    isRecording = false;
    micButton.classList.remove("recording");
    updateLanguageUI();
  }
}

micButton.addEventListener("click", () => {
  toggleRecording();
  micButton.style.transform = "scale(0.95)";
  setTimeout(() => {
    micButton.style.transform = "";
  }, 150);
});

micButton.addEventListener("mouseenter", () => {
  micButton.style.transform = "translateY(-5px) scale(1.1)";
  micButton.style.boxShadow = "0 15px 40px rgba(102, 126, 234, 0.6), 0 0 60px rgba(102, 126, 234, 0.4)";
});

micButton.addEventListener("mouseleave", () => {
  if (!micButton.classList.contains("recording")) {
    micButton.style.transform = "";
    micButton.style.boxShadow = "";
  }
});

textForm.addEventListener("submit", handleTextSubmit);

async function extractErrorMessage(response) {
  const fallback = `Request failed (${response.status})`;
  try {
    const raw = await response.text();
    if (!raw) {
      return fallback;
    }

    try {
      const parsed = JSON.parse(raw);
      const detail =
        parsed?.detail ??
        parsed?.error?.message ??
        parsed?.message;

      if (typeof detail === "string" && detail.trim()) {
        return detail.trim();
      }
    } catch {
      if (raw.trim()) {
        return raw.trim();
      }
    }

    return fallback;
  } catch {
    return fallback;
  }
}

function resetConversation() {
  conversation = [];
  conversationId = crypto.randomUUID();
  chatContainer.innerHTML = "";
  
  const welcomeScreen = document.getElementById("welcome-screen");
  if (welcomeScreen) {
    welcomeScreen.style.display = "flex";
  }
}

function updateLanguageUI() {
  const copy = languageCopy[currentLanguage] ?? languageCopy.en;
  if (textInput) {
    textInput.placeholder = copy.placeholder;
    textInput.setAttribute("aria-label", copy.placeholder);
  }
  if (micLabel) {
    micLabel.textContent = copy.mic;
  }
}

