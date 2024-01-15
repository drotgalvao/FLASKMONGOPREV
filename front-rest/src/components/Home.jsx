import React from 'react';
import './Home.css'; // Importando o arquivo CSS

function Home() {
 return (
   <div className="home">
     <h1>Welcome to our App!</h1>
     <nav>
       <ul>
         <li><a href="/register">Register</a></li>
         <li><a href="/login">Login</a></li>
       </ul>
     </nav>
   </div>
 );
}

export default Home;