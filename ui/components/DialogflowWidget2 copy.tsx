"use client";

import { useEffect } from "react";

const DialogflowWidget2 = (props: any) => {
  useEffect(() => {
    if (
      !document.querySelector(
        'script[src="https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1"]'
      )
    ) {
      const script = document.createElement("script");
      script.src = "/assets/bootstrap.js";
      script.async = true;
      document.body.appendChild(script);

      // Second script: another-script.js
      if (
        !document.querySelector(
          'script[src="/assets/custom-elements-es5-adapter.js"]'
        )
      ) {
        const script2 = document.createElement("script");
        script2.src = "/assets/custom-elements-es5-adapter.js";
        script2.async = true;
        document.body.appendChild(script2);
      }

      // Third script: another-script.js
      if (
        !document.querySelector('script[src="/assets/webcomponents-loader.js"]')
      ) {
        const script3 = document.createElement("script");
        script3.src = "/assets/webcomponents-loader.js";
        script3.async = true;
        document.body.appendChild(script3);
      }

      const styleLink = document.createElement("link");
      styleLink.rel = "stylesheet";
      styleLink.href = "/assets/df-messenger-default.css";
      document.head.appendChild(styleLink);
    }

    // Add event listener to inject userName into the payload
    const dfMessenger = document.querySelector("df-messenger");
    if (dfMessenger) {
      dfMessenger.addEventListener("df-request-sent", (event: any) => {
        console.log("Event fired");
        console.log(props.userName);
        // Modify queryParams to include userName
        event.detail.requestBody.queryParams = {
          payload: {
            userName: "Dhana", // Dynamically pass the userName
          },
        };
      });
    }

    const handleRequestSent = (event: any) => {
      console.log("Global df-request-sent event fired");
      console.log("Props userName:", props.userName);

      // Modify the payload
      if (event.detail && event.detail.requestBody) {
        event.detail.requestBody.queryParams = {
          payload: {
            userName: props.userName || "Guest",
          },
        };
        console.log("Modified requestBody:", event.detail.requestBody);
      }
    };

    // Add event listener to window
    window.addEventListener("df-request-sent", handleRequestSent);

    // Cleanup
    return () => {
      window.removeEventListener("df-request-sent", handleRequestSent);
    };
  }, [props.userName]);

  return (
    <df-messenger
      intent="WELCOME"
      style={{}}
      chat-title={`Hi, ${props.userName} !`}
      agent-id="24525646-4d95-4e6b-ab99-758e6ae136b9"
      language-code="en"
    ></df-messenger>
  );
};

export default DialogflowWidget2;
