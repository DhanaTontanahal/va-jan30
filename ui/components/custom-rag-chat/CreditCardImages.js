import Image from "next/image";
import React, { useState, useEffect } from "react";

const CreditCardImages = () => {
  const [images, setImages] = useState([]);

  useEffect(() => {
    // Fetch extracted images from the backend
    fetch("http://127.0.0.1:8000/api/extract-images")
      .then((response) => response.json())
      .then((data) => {
        if (data.images) {
          setImages(data.images);
        }
      })
      .catch((error) => console.error("Error fetching images:", error));
  }, []);

  return (
    <div>
      <h2>Credit Card Images</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
        {images.length > 0 ? (
          images.map((img, index) => (
            <Image
              width={40}
              height={40}
              key={index}
              src={img}
              alt={`Credit Card ${index + 1}`}
              style={{ width: "200px", borderRadius: "10px" }}
            />
          ))
        ) : (
          <p>No images found.</p>
        )}
      </div>
    </div>
  );
};

export default CreditCardImages;
