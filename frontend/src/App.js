import React from 'react';
import './App.css';
import Header from './components/header'
import Message from './components/Message'
class App extends React.Component {
  render()
  {
    return (
      <div  className="App">
        <Header />
        <Message/>
      </div>
    );
  }
}

export default App;
