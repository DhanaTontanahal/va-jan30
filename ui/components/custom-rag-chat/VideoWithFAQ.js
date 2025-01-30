import React, { useState, useEffect } from "react";

const VideoWithFAQ = () => {
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch FAQ data from API
  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/faqs") // Adjust API URL
      .then((response) => response.json())
      .then((data) => {
        setFaqs(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching FAQs:", error);
        setLoading(false);
      });
  }, []);

  return (
    <div className="container">
      {/* Video Player */}
      <video width="100%" controls>
        <source src="https://your-video-url.com/video.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      <h2>Frequently Asked Questions (FAQs)</h2>

      {/* FAQ Section */}
      {loading ? (
        <p>Loading FAQs...</p>
      ) : (
        <ul>
          {faqs.map((faq, index) => (
            <li key={index}>
              <strong>Q: {faq.question}</strong>
              <p>A: {faq.answer}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default VideoWithFAQ;
