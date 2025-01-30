import React from "react";
import ReactMarkdown from "react-markdown";
import { motion } from "framer-motion";
import Image from "next/image";
import "./Main.css";

const ChatResponse = ({ message }) => {
  if (!message) return null;

  console.log("Inside chat response");
  console.log(message);
  // Check if the response contains an image link
  const isImage = message.trim().match(/\.(jpeg|jpg|gif|png)$/);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-4 bg-gray-100 border border-gray-300 rounded-md shadow-md mt-2"
    >
      {isImage ? (
        <Image
          width={300}
          height={300}
          src={message}
          alt="Response Image"
          className="chat-image"
          unoptimized={true}
        />
      ) : (
        <ReactMarkdown className="text-gray-800 leading-relaxed">
          {message}
        </ReactMarkdown>
      )}
    </motion.div>
  );
};

export default ChatResponse;
