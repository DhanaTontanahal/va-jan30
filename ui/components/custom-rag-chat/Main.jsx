import React, { useState, useEffect } from "react";
import "./Main.css";
import Image from "next/image";
import userIcon from "../../public/icons/user_icon.png";
import SpeechRecognitionComponent from "./SpeechRecognitionComponent";
import runChat from "./config/gemini";
import PDFUploader from "./PDFUploader";
import ChatResponse from "./ChatResponse";

const Main = (props) => {
  useEffect(() => {}, []);

  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState([
    {
      sender: "assistant",
      message:
        "Hello, I’m your Virtual Assistant. How can I help you today? You can ask me about credit cards, application process, eligibility, and more!",
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const [selectedImage, setSelectedImage] = useState(null); // State for modal image

  const onSent = async () => {
    if (!input.trim()) return;

    setChatHistory((prev) => [
      ...prev,
      { sender: "user", message: input, images: [] }, // Include images array
    ]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });

      const data = await response.json();

      if (data.images) {
        // If images exist, add them to chat history
        setChatHistory((prev) => [
          ...prev,
          {
            sender: "assistant",
            message: data.answer, // Update to use "answer"
            images: data.images,
          },
        ]);
        setIsTyping(false);
        return;
      }

      let typingMessage = "";
      const interval = setInterval(() => {
        const nextChar = data?.answer?.[typingMessage.length];
        if (nextChar) {
          typingMessage += nextChar;
          setChatHistory((prev) =>
            prev.map((item, idx) =>
              idx === prev.length - 1
                ? { ...item, message: typingMessage }
                : item
            )
          );
        } else {
          clearInterval(interval);
          setIsTyping(false);
        }
      }, 50);

      setChatHistory((prev) => [...prev, { sender: "assistant", message: "" }]);
    } catch (error) {
      setChatHistory((prev) => [
        ...prev,
        {
          sender: "assistant",
          message: "An error occurred. Please try again.",
        },
      ]);
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      onSent();
    }
  };

  const listenTranscript = async (data) => {
    const prompt = `The following text is a raw voice transcription:
    "${data}"
    Please convert this input into a meaningful, grammatically correct sentence.
    If the transcription is incomplete or unclear, complete it to the best of your ability.`;

    try {
      const processedResponse = await runChat(prompt);
      setInput(processedResponse);
    } catch (error) {
      console.error("Error processing voice input:", error);
    }
  };

  const handleMinimizeClick = () => {
    props.closeClick();
  };

  const [showModal, setShowModal] = useState(false);

  const showPDFUploader = () => {
    setShowModal(true);
  };

  const openImageModal = (imgSrc) => {
    setSelectedImage(imgSrc);
  };

  const closeImageModal = () => {
    setSelectedImage(null);
  };

  return (
    <div className="main">
      {/* Chat Header */}
      <div className="chat-header">
        <h3>Hi, Russel !</h3>
        <div style={{ display: "inline-flex" }}>
          <span onClick={handleMinimizeClick} className="minimize-icon">
            -
          </span>
          <span onClick={handleMinimizeClick} className="close-icon">
            x
          </span>
        </div>
      </div>

      <div className="chat-container">
        <div className="chat-history">
          {chatHistory.map((chat, index) => (
            <div
              key={index}
              className={`chat-message ${
                chat.sender === "user" ? "user-message" : "assistant-message"
              }`}
            >
              <Image
                width={40}
                height={40}
                src={
                  chat.sender === "user"
                    ? userIcon
                    : "/icons/lloyds_response_icon.png"
                }
                alt={`${chat.sender} icon`}
                className="chat-icon1"
              />
              <ChatResponse message={chat.message} />

              {/* Image Display */}
              {chat.images && (
                <div className="image-container">
                  {chat.images.map((img, idx) => (
                    <Image
                      key={idx}
                      src={img}
                      alt="Credit Card"
                      width={150}
                      height={150}
                      className="chat-image"
                      onClick={() => openImageModal(img)}
                    />
                  ))}
                </div>
              )}
            </div>
          ))}

          {isTyping && (
            <div className="chat-message assistant-message">
              <Image
                width={40}
                height={40}
                src={"/icons/lloyds_response_icon.png"}
                alt="Assistant Typing"
                className="chat-icon"
              />
              <p>...</p>
            </div>
          )}
        </div>

        <div className="chat-input">
          <input
            id="msgInput"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything..."
          />
          <button onClick={onSent}>
            <Image
              src={"/icons/send_icon.png"}
              alt="send"
              width={40}
              height={40}
            />
          </button>
          <SpeechRecognitionComponent
            sendTranscript={(d) => listenTranscript(d)}
          />
          <button onClick={showPDFUploader}>
            <Image
              src={"/icons/attach.png"}
              alt="attach"
              width={40}
              height={40}
            />
          </button>
        </div>
      </div>

      {showModal && <PDFUploader onClose={() => setShowModal(false)} />}

      {/* Image Modal */}
      {selectedImage && (
        <div className="image-modal" onClick={closeImageModal}>
          <div className="modal-content">
            <span className="close-button" onClick={closeImageModal}>
              &times;
            </span>
            <img
              src={selectedImage}
              alt="Expanded View"
              className="modal-image"
            />
          </div>
        </div>
      )}

      <p className="bottom-info">
        Lloyds Bank plc is a major British retail and commercial bank with a
        significant presence across England and Wales. It has traditionally been
        regarded as one of the "Big Four" clearing banks.
      </p>
    </div>
  );
};

export default Main;
