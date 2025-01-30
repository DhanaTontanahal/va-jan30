import React, { useEffect, useState } from "react";
import Image from "next/image";
import "./SpeechRecognitionComponent.css";

const SpeechRecognitionComponent = (props) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if the browser supports SpeechRecognition
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setError("Speech Recognition API is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true; // Keep listening for speech continuously
    recognition.interimResults = true; // Get partial results while speaking
    recognition.lang = "en-US"; // Set the language

    // Handle speech start
    recognition.onstart = () => {
      console.log("Speech recognition started");
      setIsListening(true);
    };

    // Handle speech end
    recognition.onend = () => {
      console.log("Speech recognition stopped");
      setIsListening(false);
    };

    // Handle errors
    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setError(event.error);
    };

    // Process results
    recognition.onresult = (event) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptChunk = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcriptChunk;
        } else {
          interimTranscript += transcriptChunk;
        }
      }

      // console.log(interimTranscript);
      setTranscript(finalTranscript || interimTranscript);
      props.sendTranscript(interimTranscript);
    };

    // Start or stop recognition based on `isListening` state
    if (isListening) {
      recognition.start();
    } else {
      recognition.stop();
    }

    // Cleanup
    return () => {
      recognition.abort();
    };
  }, [isListening]);

  const handleMicOn = () => {
    setIsListening((prev) => !prev);
  };
  return (
    <>
      <div
        className={!isListening ? "mic-container" : "mic-container active"}
        style={{
          cursor: "pointer",
          display: "inline-block",
        }}
        onClick={handleMicOn}
      >
        <div className="mic-icon">
          <Image
            width={30}
            height={20}
            src={isListening ? "/icons/mic_icon.png" : "/icons/mic_icon.png"}
            alt="Mic Icon"
            style={{
              background: "transparent",
              width: "20px",
              height: "30px",
              transition: "all 0.3s ease",
            }}
          />
        </div>
      </div>
    </>
  );
};

export default SpeechRecognitionComponent;
