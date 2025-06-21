import React, { useState } from "react";
import CanvasArea from "./components/CanvasArea";
import { getIntent } from "./services/aiService";

function App() {
  const [widgets, setWidgets] = useState([]);
  const [textPrompt, setTextPrompt] = useState("");

  const handleTextSubmit = async () => {
    if (!textPrompt.trim()) return;
    const intent = await getIntent(textPrompt);
    if (intent) setWidgets((prev) => [...prev, intent]);
    setTextPrompt("");
  };

  const handleVoiceInput = () => {
    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;
      console.log("🎙️ You said:", transcript);
      const intent = await getIntent(transcript);
      if (intent) setWidgets((prev) => [...prev, intent]);
    };

    recognition.onerror = (err) => {
      console.error("Speech recognition error:", err);
    };

    recognition.start();
  };

  return (
    <>
      <div style={{ padding: "10px", background: "#111", color: "#fff" }}>
        <input
          value={textPrompt}
          onChange={(e) => setTextPrompt(e.target.value)}
          placeholder="Type your command here..."
          style={{
            padding: "10px",
            width: "60%",
            fontSize: "16px",
            borderRadius: "5px",
            marginRight: "10px",
          }}
        />
        <button
          onClick={handleTextSubmit}
          style={{
            padding: "10px 20px",
            fontSize: "16px",
            borderRadius: "5px",
            background: "#00FFD1",
            color: "#000",
            marginRight: "10px",
            cursor: "pointer",
          }}
        >
          Generate
        </button>

        <button
          onClick={handleVoiceInput}
          style={{
            padding: "10px 20px",
            fontSize: "16px",
            borderRadius: "5px",
            background: "#ff4d4d",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          🎙️ Voice Input
        </button>
      </div>

      <CanvasArea widgets={widgets} />
    </>
  );
}

export default App;
