import React from "react";

const FetchSpeechToText = async () => {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/speech-to-text", {
      method: "POST",
    });
    const data = await response.json();

    if (data.status === "success") {
      console.log("Transcript:", data.transcript);
      // Update chatbot input
      setInput(data.transcript);
    } else {
      console.error("Error:", data.message);
    }
  } catch (error) {
    console.error("Error fetching speech-to-text:", error);
  }
};

return (
  <div>
    <button onClick={fetchSpeechToText}>Start Voice Input</button>
  </div>
);
