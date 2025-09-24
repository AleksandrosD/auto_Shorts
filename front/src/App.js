import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        responseType: "blob", 
        withCredentials: false
      });

      // ✅ Use response.data directly; no need for new Blob()
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "video_with_subs.mp4"); // filename
      document.body.appendChild(link);
      link.click();
      link.remove();

      // Release memory
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Upload failed:", err);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <button onClick={handleUpload} style={{ marginLeft: "10px" }}>
        Upload & Download
      </button>
    </div>
  );
}

export default App;
