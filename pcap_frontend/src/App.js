import React from 'react';
import AnalysisComponent from './components/AnalysisComponent';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        {/* Vous pouvez conserver le logo et le lien si vous le souhaitez */}
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
      <main>
        <h1>Mon Application</h1>
        <AnalysisComponent /> {/* Affichez le composant d'analyse ici */}
        {/* Autres contenus */}
      </main>
      <footer>
        {/* Pied de page */}
      </footer>
    </div>
  );
}

export default App;
