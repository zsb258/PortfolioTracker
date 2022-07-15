import React from 'react';

import logo from './logo.svg';
import './App.css';
import LivePortfolio from './components/LivePortfolio/LivePortfolio';
import ReportExporter from './components/ReportExporter/ReportExporter';
import Header from './components/Header/Header';
import CashLevelPortfolio from './components/CashLevelPortfolio/CashLevelPortfolio';

function App() {
  return (
    <div className="App">
      <ReportExporter />
      <Header />
      <CashLevelPortfolio />
      <LivePortfolio />
      {/* <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.tsx</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header> */}
    </div>
  );
}

export default App;
