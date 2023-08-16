import React, { useState, useEffect } from 'react';
import axios from 'axios';

function AnalysisComponent() {
  const [analysisResults, setAnalysisResults] = useState(null);

  useEffect(() => {
    // Appel à l'API pour récupérer les résultats d'analyse
    axios.get('/api/analysis/')
      .then(response => {
        setAnalysisResults(response.data);
      })
      .catch(error => {
        console.error('Erreur lors de la récupération des données d\'analyse:', error);
      });
  }, []);

  if (!analysisResults) {
    return <p>Chargement en cours...</p>;
  }

  return (
    <div>
      <h2>Résultats d'Analyse</h2>
      <p>Nombre de paquets: {analysisResults.packet_count}</p>
      {/* Affichez d'autres données d'analyse selon vos besoins */}
    </div>
  );
}

export default AnalysisComponent;
