import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/Home';
import Register from './components/Register';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Game from './components/Game';


function App() {
 return (
   <Router>
     <Routes>
       <Route path="/" element={<Home />} />
       <Route path="register" element={<Register />} />
       <Route path="login" element={<Login />} />
       <Route path="dashboard" element={<Dashboard />} />
       <Route path="game" element={<Game />} />
     </Routes>
   </Router>
 );
}

export default App;