// Aqui esta el llamado a la base de firebase y el proceso que se llama
import firebase from "firebase/app";
import "firebase/firestore";
import "firebase/auth";
import "firebase/functions"; // Añadir esta línea

var firebaseConfig = {
  apiKey: "AIzaSyCpEOhbMrjBJ9-KmPfhrQU8QZW5n-en2kc",
  authDomain: "fir-proyect-a6737.firebaseapp.com",
  projectId: "fir-proyect-a6737",
  storageBucket: "fir-proyect-a6737.appspot.com",
  messagingSenderId: "207399251514",
  appId: "1:207399251514:web:0583bd566073fc08c5cf03",
  measurementId: "G-R6VDZ1JHQV"
};

const firebaseApp = firebase.initializeApp(firebaseConfig);
const timestamp = firebase.firestore.FieldValue.serverTimestamp;
const functions = firebaseApp.functions(); // Añadir esta línea

export { timestamp, functions }; // Exportar functions
export default firebaseApp.firestore();