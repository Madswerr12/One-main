<template>
  <div class="form-wrap">
    <form class="login">
      <h2>Ingresa a PropSyng</h2>
      <div class="inputs">
        <div class="input">
          <input type="text" placeholder="Email" v-model="email" />
          <email class="icon" />
        </div>
        <div class="input">
          <input type="password" placeholder="Password" v-model="password" />
          <password class="icon" />
        </div>
      </div>
      <router-link class="forgot-password" :to="{ name: '' }">Olvidaste la contraseña, reporta a administración</router-link>
      <button @click.prevent="signIn" :disabled="loading">
        {{ loading ? 'Procesando...' : 'Ingresa' }}
      </button>
      <div class="angle"></div>
    </form>
    <div class="background"></div>
  </div>
</template>

<script>
import email from "../assets/Icons/envelope-regular.svg";
import password from "../assets/Icons/lock-alt-solid.svg";
import firebase from "firebase/app";
import "firebase/auth";
import db from "../firebase/firebaseInit";

export default {
  name: "Login",
  components: {
    email,
    password,
  },
  data() {
    return {
      email: "",
      password: "",
      loading: false,
      isSigningIn: false,
      error: null,
    };
  },
  methods: {
    async signIn() {
      // Evitar múltiples intentos de inicio de sesión
      if (this.isSigningIn) return;
      
      this.isSigningIn = true;
      this.loading = true;
      this.error = null;
      
      try {
        // Validación básica de campos
        if (!this.email || !this.password) {
          this.error = "Por favor ingresa email y contraseña";
          return;
        }

        // Intentar iniciar sesión con Firebase Authentication
        const userCredential = await firebase
          .auth()
          .signInWithEmailAndPassword(this.email, this.password);
        
        // Obtener el usuario autenticado
        const user = userCredential.user;
        
        // Verificar si el usuario está deshabilitado en Firestore
        const userDoc = await db.collection("users").doc(user.uid).get();
        
        if (!userDoc.exists) {
          this.error = "No se encontró información del usuario. Contacta al administrador.";
          await firebase.auth().signOut();
          return;
        }
        
        const userData = userDoc.data();
        
        // Si el usuario está deshabilitado en Firestore, cerrar sesión y mostrar alerta
        if (userData.disabled === true) {
          console.log("Usuario deshabilitado detectado");
          await firebase.auth().signOut();
          
          this.error = "Usuario deshabilitado. Contacta al administrador.";
          return;
        }
        
        // Si el usuario está habilitado, redirigir al home
        this.$router.push({ name: "Home" });
        
      } catch (err) {
        console.error("Error en signIn:", err);
        
        // Manejo de errores específicos con mensajes claros
        if (err.code) {
          switch (err.code) {
            case "auth/user-not-found":
              this.error = "Usuario no encontrado. Verifica tu email.";
              break;
            case "auth/wrong-password":
              this.error = "Contraseña incorrecta. Intenta nuevamente.";
              break;
            case "auth/user-disabled":
              this.error = "Usuario deshabilitado. Contacta al administrador.";
              break;
            case "auth/invalid-email":
              this.error = "Email inválido. Verifica el formato.";
              break;
            case "auth/too-many-requests":
              this.error = "Demasiados intentos fallidos. Intenta más tarde.";
              break;
            case "auth/network-request-failed":
              this.error = "Error de red. Verifica tu conexión.";
              break;
            case "auth/internal-error":
              // Manejar específicamente el error de credenciales inválidas
              this.error = "Email o contraseña incorrectos. Por favor, inténtalo de nuevo.";
              break;
            default:
              this.error = "Error al iniciar sesión. Por favor, inténtalo más tarde.";
          }
        } else if (err.message && err.message.includes("INVALID_LOGIN_CREDENTIALS")) {
          // Manejar específicamente el mensaje de credenciales inválidas
          this.error = "Email o contraseña incorrectos. Por favor, inténtalo de nuevo.";
        } else {
          this.error = "Error desconocido. Por favor, contacta al administrador.";
        }
      } finally {
        this.loading = false;
        this.isSigningIn = false;
        
        // Mostrar el error si existe y recargar la página después de aceptar
        if (this.error) {
          alert(this.error);
          // Recargar la página después de que el usuario acepte el mensaje de error
          window.location.reload();
        }
      }
    }
  }
}
</script>

<style lang="scss">
.form-wrap {
  overflow: hidden;
  display: flex;
  height: 100vh;
  justify-content: center;
  align-self: center;
  margin: 0 auto;
  width: 100%;

  @media (min-width: 900px) {
    width: 100%;
  }

  .login-register {
    margin-bottom: 32px;

    .router-link {
      color: #000;
    }
  }

  form {
    padding: 0 10px;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    flex: 1;

    @media (min-width: 900px) {
      padding: 0 50px;
    }

    h2 {
      text-align: center;
      font-size: 32px;
      color: #303030;
      margin-bottom: 40px;

      @media (min-width: 900px) {
        font-size: 40px;
      }
    }

    .inputs {
      width: 100%;
      max-width: 350px;

      .input {
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 8px;

        input {
          width: 100%;
          border: none;
          background-color: #f2f7f6;
          padding: 4px 4px 4px 30px;
          height: 50px;

          &:focus {
            outline: none;
          }
        }

        .icon {
          width: 12px;
          position: absolute;
          left: 6px;
        }
      }
    }

    .forgot-password {
      text-decoration: none;
      color: #000;
      cursor: pointer;
      font-size: 14px;
      margin: 16px 0 32px;
      border-bottom: 1px solid transparent;
      transition: 0.5s ease all;

      &:hover {
        border-color: #303030;
      }
    }

    button {
      transition: 0.5s ease all;
      cursor: pointer;
      padding: 12px 24px;
      background-color: #303030;
      color: #fff;
      border-radius: 20px;
      border: none;
      text-transform: uppercase;
      
      &:hover {
        background-color: rgba(48, 48, 48, 0.7);
      }
      
      &:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
      }
    }

    .angle {
      display: none;
      position: absolute;
      background-color: #fff;
      transform: rotateZ(3deg);
      width: 60px;
      right: -30px;
      height: 101%;

      @media (min-width: 900px) {
        display: initial;
      }
    }
  }
}
</style>