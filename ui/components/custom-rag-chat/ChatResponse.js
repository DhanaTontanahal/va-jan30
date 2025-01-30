import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { motion } from "framer-motion";
import Image from "next/image";
import "./Main.css";

const ChatResponse = ({ message }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState("");

  if (!message) return null;

  console.log("Inside chat response");
  console.log(message);

  // Check if the response contains an image link
  const isImage = message.trim().match(/\.(jpeg|jpg|gif|png)$/);

  // Function to open image in a popup modal
  const openImageModal = (imgSrc) => {
    alert("open");
    setSelectedImage(imgSrc);
    setIsOpen(true);
  };

  // Function to close the modal
  const closeModal = () => {
    setIsOpen(false);
    setSelectedImage("");
  };

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="p-4 bg-gray-100 border border-gray-300 rounded-md shadow-md mt-2"
      >
        {isImage ? (
          <div className="image-wrapper">
            {/* Clickable Image */}
            <Image
              width={300}
              height={300}
              src={message}
              alt="Response Image"
              className="chat-image cursor-pointer"
              unoptimized={true}
              onClick={() => openImageModal(message)}
            />
          </div>
        ) : (
          <ReactMarkdown className="text-gray-800 leading-relaxed">
            {message}
          </ReactMarkdown>
        )}
      </motion.div>

      {/* Image Modal */}
      {isOpen && (
        <div className="image-modal" onClick={closeModal}>
          <div className="modal-content">
            <span className="close-button" onClick={closeModal}>
              &times;
            </span>
            <Image
              width={300}
              height={300}
              src={selectedImage}
              alt="Expanded View"
              className="modal-image"
            />
          </div>
        </div>
      )}
    </>
  );
};

export default ChatResponse;
