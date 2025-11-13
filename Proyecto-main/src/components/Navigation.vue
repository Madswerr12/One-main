<template>
  <header>
    <nav class="container">
      <div class="branding">
        <router-link class="header" :to="{ name: 'Home' }">
          <img src="@/assets/blogPhotos/PropSyng.png" alt="PropSyng Logo" class="logo" />
        </router-link>
      </div>
      <div class="nav-links">
        <ul v-show="!mobile">
          <router-link class="link" :to="{ name: 'Home' }">Inicio</router-link>
          <router-link v-if="user" class="link" :to="{ name: 'Cards' }">Noticias</router-link>

          <!-- Crear Noticias visible para admin y nomina -->
          <a v-if="admin || isNomina" class="link" href="/create-post">Crear Noticias</a>

          <!-- Crear Usuarios solo visible para admin -->
          <router-link v-if="admin" class="link" :to="{ name: 'Register' }">Usuarios</router-link>

          <router-link v-if="!user" class="link" :to="{ name: 'Login' }">Ingresar</router-link>

          <!-- Pagos visible para todos los usuarios autenticados -->
          <router-link v-if="user && !isCasos && !isNomina" class="link" :to="{ name: 'Pagos' }">Pagar</router-link>

          <router-link v-if="user" class="link" :to="{ name: 'Tickets' }">Casos</router-link>

          <!-- Asignar pagos solo visible para admin -->
          <a v-if="admin || isNomina" class="link" href="/Precios">Asignar pagos</a>
        </ul>

        <div v-if="user" :class="{ 'mobile-user-menu': mobile }" @click="toggleProfileMenu" class="profile"
          ref="profile">
          <span>{{ this.$store.state.profileInitials }}</span>
          <div v-show="profileMenu" class="profile-menu">
            <div class="info">
              <p class="initials">{{ this.$store.state.profileInitials }}</p>
              <div class="right">
                <p>{{ this.$store.state.profileFirstName }} {{ this.$store.state.profileLastName }}</p>
                <p>{{ this.$store.state.profileUsername }}</p>
                <p>{{ this.$store.state.profileEmail }}</p>
              </div>
            </div>
            <div class="options">
              <div class="option">
                <router-link class="option" :to="{ name: 'Profile' }">
                  <userIcon class="icon" />
                  <p>Perfil</p>
                </router-link>
              </div>
              <div @click="signOut" class="option">
                <signOutIcon class="icon" />
                <p>Cerrar Sesion</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
    <menuIcon @click="toggleMobileNav" class="menu-icon" v-show="mobile" />
    <transition name="mobile-nav">
      <ul class="mobile-nav" v-show="mobileNav">
        <router-link class="link" :to="{ name: 'Home' }">Inicio</router-link>
        <router-link v-if="user" class="link" :to="{ name: 'Cards' }">Noticias</router-link>

        <!-- Crear Noticias visible para admin y nomina -->
        <a v-if="admin || isNomina" class="link" href="/create-post">Crear Noticias</a>

        <!-- Crear Usuarios solo visible para admin -->
        <router-link v-if="admin" class="link" :to="{ name: 'Register' }">Usuarios</router-link>

        <router-link v-if="!user" class="link" :to="{ name: 'Login' }">Ingresar</router-link>

        <!-- Pagos visible para todos los usuarios autenticados -->
        <router-link v-if="user && !isCasos && !isNomina" class="link" :to="{ name: 'Pagos' }">Pagar</router-link>

        <router-link v-if="user" class="link" :to="{ name: 'Tickets' }">Casos</router-link>

        <!-- Asignar pagos solo visible para admin -->
        <a v-if="admin || isNomina" class="link" href="/Precios">Asignar pagos</a>
      </ul>
    </transition>
  </header>
</template>

<script>
import menuIcon from "../assets/Icons/bars-regular.svg";
import userIcon from "../assets/Icons/user-alt-light.svg";
import signOutIcon from "../assets/Icons/sign-out-alt-regular.svg";
import firebase from "firebase/app";
import "firebase/auth";
import db from "../firebase/firebaseInit";

export default {
  name: "navigation",
  components: {
    menuIcon,
    userIcon,
    signOutIcon,
  },
  data() {
    return {
      profileMenu: null,
      mobile: null,
      mobileNav: null,
      windownWidth: null,
    };
  },
  created() {
    window.addEventListener("resize", this.checkScreen);
    this.checkScreen();
    this.checkUserRole();
  },
  methods: {
    checkScreen() {
      this.windownWidth = window.innerWidth;
      if (this.windownWidth <= 1096) {
        this.mobile = true;
        return;
      }
      this.mobile = false;
      this.mobileNav = false;
      return;
    },

    toggleMobileNav() {
      this.mobileNav = !this.mobileNav;
    },

    toggleProfileMenu(e) {
      if (e.target === this.$refs.profile) {
        this.profileMenu = !this.profileMenu;
      }
    },

    async checkUserRole() {
      const userId = firebase.auth().currentUser?.uid;
      if (userId) {
        const userDoc = await db.collection("users").doc(userId).get();
        const userData = userDoc.data();
        this.$store.commit('setProfileRole', userData.role || 'user'); // Establecer rol por defecto como 'user'
      }
    },

    signOut() {
      firebase.auth().signOut();
      window.location.reload();
    },
  },
  computed: {
    user() {
      return this.$store.state.user;
    },
    admin() {
      return this.$store.state.profileRole === 'admin';
    },
    // Agregar propiedad computada para verificar si es nomina
    isNomina() {
      return this.$store.state.profileRole === 'nomina';
    },
    isCasos() {
      return this.$store.state.profileRole === 'Casos';
    },
  },
};
</script>

<style lang="scss" scoped>
header {
  background-color: #265381;
  color: #fff;
  padding: 0 25px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  z-index: 99;

  .link {
    font-weight: 500;
    padding: 0 8px;
    transition: 0.3s color ease;
    color: #fff;

    &:hover {
      color: #11bcd5;
    }
  }

  nav {
    display: flex;
    padding: 18px 0;

    .branding {
      display: flex;
      align-items: center;

      .logo {
        height: 60px;
        width: auto;
      }
    }

    .nav-links {
      position: relative;
      display: flex;
      flex: 1;
      align-items: center;
      justify-content: flex-end;

      ul {
        margin-right: 32px;

        .link {
          margin-right: 32px;
        }

        .link:last-child {
          margin-right: 0;
        }
      }

      .profile {
        position: relative;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        color: #fff;
        background-color: #303030;

        span {
          pointer-events: none;
        }

        .profile-menu {
          position: absolute;
          top: 60px;
          right: 0;
          width: 300px; /* Aumentado de 250px a 300px */
          max-width: 90vw; /* Limitar ancho máximo */
          background-color: #303030;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);

          .info {
            display: flex;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #fff;
            width: 100%;
            box-sizing: border-box;

            .initials {
              position: initial;
              width: 40px !important;
              height: 40px !important;
              background-color: #fff;
              color: #303030;
              display: flex;
              align-items: center;
              justify-content: center;
              border-radius: 50%;
              box-sizing: border-box;
              overflow: hidden;
              flex-shrink: 0;
              aspect-ratio: 1/1;
              padding: 0;
              margin: 0;
            }

            .right {
              flex: 1;
              margin-left: 24px;
              min-width: 0; /* Importante para truncamiento */
              overflow: hidden; /* Ocultar desbordamiento */

              p {
                white-space: nowrap; /* Mantener en una línea */
                overflow: hidden; /* Ocultar desbordamiento */
                text-overflow: ellipsis; /* Agregar puntos suspensivos */
                width: 100%;
                margin: 0; /* Eliminar márgenes */
              }

              p:nth-child(1) {
                font-size: 14px;
                color: #fff;
                font-weight: bold;
              }

              p:nth-child(2),
              p:nth-child(3) {
                font-size: 12px;
                color: #fff;
              }
            }
          }

          .options {
            padding: 15px;

            .option {
              text-decoration: none;
              color: #fff;
              display: flex;
              align-items: center;
              margin-bottom: 12px;

              .icon {
                width: 18px;
                height: auto;
              }

              p {
                font-size: 14px;
                margin-left: 12px;
              }

              &:last-child {
                margin-bottom: 0px;
              }
            }
          }
        }
      }
    }

    .mobile-user-menu {
      margin-right: 40px;
    }
  }

  .menu-icon {
    cursor: pointer;
    position: absolute;
    top: 32px;
    right: 25px;
    height: 25px;
    width: auto;
  }

  .mobile-nav {
    padding: 20px;
    width: 70%;
    max-width: 250px;
    display: flex;
    flex-direction: column;
    position: fixed;
    height: 100%;
    background-color: #265381;
    top: 0;
    left: 0;

    .link {
      padding: 15px 0;
      color: #fff;
    }
  }

  .mobile-nav-enter-active,
  .mobile-nav-leave-active {
    transition: all 1s ease;
  }

  .mobile-nav-enter {
    transform: translateX(-250px);
  }

  .mobile-nav-enter-to {
    transform: translateX(0);
  }

  .mobile-nav-leave-to {
    transform: translateX(-250px);
  }
}
</style>