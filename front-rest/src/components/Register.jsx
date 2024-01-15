import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./Register.css";

function Register() {
 const [nome, setNome] = useState("");
 const [email, setEmail] = useState("");
 const [password, setPassword] = useState("");
 const navigate = useNavigate();

 const handleSubmit = async (event) => {
   event.preventDefault();

   const data = {
     nome: nome,
     email: email,
     password: password,
   };

   try {
     await axios.post("http://127.0.0.1:5000/api/register", data);
     alert("Registration successful!");
     navigate('/login');
   } catch (error) {
    if (error.response) {
        const errors = error.response.data;
        Object.keys(errors).forEach((key) => {
          errors[key].forEach((errMsg) => {
            alert(`${key}: ${errMsg}`);
          });
        });
       } else if (error.request) {
      console.log(error.request);
    } else {
      console.log('Error', error.message);
    }
    console.log(error.config);
   }
 };

  return (
    <div className="register">
    <form onSubmit={handleSubmit}>
      <label>
        Nome:
        <input
          type="text"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          required
        />
      </label>
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
      <button type="submit">Register</button>
    </form>
  </div>
  );
}

export default Register;
