import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Cookies from 'js-cookie';
import "./Login.css";

function Login() {
 const [email, setEmail] = useState("");
 const [password, setPassword] = useState("");
 const navigate = useNavigate();

 const instance = axios.create({
  baseURL: 'http://127.0.0.1:5000/api',
  withCredentials: true,
 });
 
 const handleSubmit = async (event) => {
  event.preventDefault();
 
  const data = {
    email: email,
    password: password,
  };
 
  try {
    const response = await instance.post("/login", data);
    const token = response.data.token;
    Cookies.set('token', token);
    alert("Login successful!");
    navigate('/dashboard');
  } catch (error) {
    if (error.response) {
      console.log(error.response.data);
      console.log(error.response.status);
      console.log(error.response.headers);
    } else if (error.request) {
      console.log(error.request);
    } else {
      console.log('Error', error.message);
    }
    console.log(error.config);
  }
 };

 return (
<div className="login">
 <form onSubmit={handleSubmit}>
   <label>
     Email:
     <input
       type="email"
       value={email}
       onChange={(e) => setEmail(e.target.value)}
       required
     />
   </label>
   <label>
     Password:
     <input
       type="password"
       value={password}
       onChange={(e) => setPassword(e.target.value)}
       required
     />
   </label>
   <button type="submit">Login</button>
 </form>
</div>
 );
}

export default Login;