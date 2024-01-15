import React from 'react'
import { Link } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
 return (
  <div className="dashboard">
    Dashboard
    <Link to="/game">Enter Game</Link>
  </div>
 )
}

export default Dashboard