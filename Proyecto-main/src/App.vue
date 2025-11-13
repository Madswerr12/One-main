<template>
  <div id="app">
    <div class="app-wrapper">
      <div class="app" v-if="$store.state.postLoaded">
        <Navigation v-if="!navigation" />
        <router-view />
        <Footer v-if="!navigation" />
        <!-- Chatbot debe estar dentro del app-wrapper pero después del contenido principal -->
        <Chatbot />
      </div>
    </div>
  </div>
</template>

<script>
import Navigation from "./components/Navigation";
import Footer from "./components/Footer";
import firebase from "firebase/app";
import Chatbot from './components/Chatbot.vue'; 
import "firebase/auth";
export default {
  name: "app",
  components: {Navigation, Footer, Chatbot},
  data() {
    return {
      navigation: false
    };
  },
  created() {
   firebase.auth().onAuthStateChanged((user)=>{ 
    this.$store.commit("updateUser", user);
    if (user){ 
      this.$store.dispatch ("getCurrentUser");
    }
   });
    this.checkRoute();
    this.$store.dispatch("getPost");
  },
  mounted() {},
  methods: {
    checkRoute(){
      if (
      this.$route.name ==="ForgotPasswords" 
      ){
        this.navigation = true;
        return;
      }
      this.navigation = false;
    },

  },
  watch: {
    $route(){
      this.checkRoute();
    },
  },
};
</script>

<style lang="scss">
@import url("https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap");

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Quicksand", sans-serif;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative; /* Importante para el posicionamiento del chatbot */
}

.container {
  max-width: 1440px;
  margin: 0 auto;
}

.link {
  cursor: pointer;
  text-decoration: none;
  text-transform: uppercase;
  color: black;
}

.link-light {
  color: #fff;
}

.arrow {
  margin-left: 8px;
  width: 12px;
  path {
    fill: #000;
  }
}
.arrow-light {
  path {
    fill: #fff;
  }
}

button,
.router-button {
  transition: 500ms ease all;
  cursor: pointer;
  margin-top: 24px;
  padding: 12px 24px;
  background-color: #16baf4;
  color: #fff;
  border-radius: 20px;
  border: none;
  text-transform: uppercase;

  &:focus {
    outline: none;
  }

  &:hover {
    background-color: rgba(48, 48, 48, 0.7);
  }
}

.button-ghost {
  color: #000;
  padding: 0;
  border-radius: 0;
  margin-top: 50px;
  font-size: 15px;
  font-weight: 500;
  background-color: transparent;
  @media (min-width: 700px) {
    margin-top: 0;
    margin-left: auto;
  }

  i {
    margin-left: 8px;
  }
}

.button-light {
  background-color: transparent;
  border: 2px solid #fff;
  color: #fff;
}

.button-inactive {
  pointer-events: none !important;
  cursor: none !important;
  background-color: rgba(128, 128, 128, 0.5) !important;
}


.blog-card-wrap {
  position: relative;
  padding: 80px 16px;
  background-color: #f1f1f1;
  @media (min-width: 500px) {
    padding: 100px 16px;
  }

  .blog-cards {
    display: grid;
    gap: 32px;
    grid-template-columns: 1fr;

    @media (min-width: 500px) {
      grid-template-columns: repeat(2, 1fr);
    }
    @media (min-width: 900px) {
      grid-template-columns: repeat(3, 1fr);
    }
    @media (min-width: 1200px) {
      grid-template-columns: repeat(4, 1fr);
    }
  }
}

.qkb-bubble-btn {
  width: 62px !important; /* Sobrescribe el ancho */
  height: 62px !important; /* Sobrescribe la altura */
  background-color: #1b53d0 !important; /* Cambia el color de fondo */
  border-radius: 50% !important; /* Mantiene el borde redondo */
  display: flex !important; /* Asegúrate de que el display sea flex */
  align-items: center !important; /* Centra el contenido verticalmente */
  justify-content: center !important; /* Centra el contenido horizontalmente */
  margin: -0px 0 0 -0px !important;
  z-index: 9999 !important; /* Asegura que esté por encima de todo */
}

.qkb-bubble-btn img {
  width: 30px !important; /* Ajusta el tamaño de la imagen */
  height: 30px !important;
  /* Ajusta el tamaño de la imagen */
}

.qkb-action-item.qkb-action-item--send {
  margin-top: 0 !important; /* Elimina el margen superior */
}

/* Estilos para asegurar que el modal del chatbot esté por encima de todo */
.modal-overlay {
  z-index: 99999 !important; /* Z-index muy alto para asegurar que esté por encima */
}

.qkb-board {
  z-index: 9998 !important; /* Asegura que el chatbot esté por encima de otros elementos */
}
</style>