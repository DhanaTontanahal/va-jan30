"use client";

import { useEffect } from "react";

const DialogflowWidget2 = (props: any) => {
  useEffect(() => {
    const loadDialogflowMessenger = () => {
      if (
        !document.querySelector(
          'script[src="https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1"]'
        )
      ) {
        const script = document.createElement("script");
        script.src =
          "https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1";
        script.async = true;
        document.body.appendChild(script);
      }

      // Listen for when the widget is fully loaded
      window.addEventListener("dfMessengerLoaded", () => {
        console.log("Dialogflow Messenger loaded");
        applyCustomStyles();
      });
    };

    const applyCustomStyles = () => {
      const dfMessenger = document.querySelector("df-messenger");
      if (dfMessenger) {
        // Apply custom CSS to the chat icon
        const style = document.createElement("style");
        style.textContent = `
          df-messenger .df-chat-icon {
            background-image: url('https://tse1.mm.bing.net/th?id=OIP.MqvM9FNd-34H25i25M1mEQHaGZ&pid=Api&P=0&h=180');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            width: 56px; /* Match default icon size */
            height: 56px; /* Match default icon size */
          }
        `;
        document.head.appendChild(style);
        console.log("Custom styles applied");
      } else {
        console.error("df-messenger element not found");
      }
    };

    loadDialogflowMessenger();

    return () => {
      //window.removeEventListener("dfMessengerLoaded", applyCustomStyles);
    };
  }, []);

  return (
    <df-messenger
      intent="WELCOME"
      chat-title={`Hi, ${props.userName || "Guest"}!`}
      agent-id="24525646-4d95-4e6b-ab99-758e6ae136b9"
      language-code="en"
    ></df-messenger>
  );
};

export default DialogflowWidget2;
