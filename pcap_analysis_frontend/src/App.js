import React, { useState } from 'react';
import axios from 'axios';
import Upload from './upload';


function App() {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file_pcap', file);
    axios.post('http://localhost:8000/upload/', formData)
      .then((response) => {
        // Traitez les résultats de l'analyse ici
        console.log(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  return (
    <div>
      <h1>PCAP Analysis</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" name="file_pcap" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
    </div>
  );
}

export default App;
