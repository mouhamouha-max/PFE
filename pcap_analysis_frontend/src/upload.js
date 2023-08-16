import React, { useState } from 'react';
import axios from 'axios';

const Upload = () => {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleFormSubmit = (event) => {
    event.preventDefault();

    if (selectedFile) {
      const formData = new FormData();
      formData.append('pcapFile', selectedFile);

      axios
        .post('/api/upload_pcap/', formData)
        .then((response) => {
          console.log(response.data);
          // Traitez les résultats de l'analyse ici
        })
        .catch((error) => {
          console.error(error);
        });
    }
  };

  return (
    <div>
      <h2>Upload .pcap File</h2>
      <form onSubmit={handleFormSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
    </div>
  );
};

export default Upload;
