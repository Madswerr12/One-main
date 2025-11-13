<!-- Aqui esta el footer utilizado en todas las paginas-->
<template>
  <footer>
    <div class="container">
      <div class="left">
        <div class="col-1">
          <router-link :to="{ name: 'Home' }" class="logo-link">
  <img src="@/assets/blogPhotos/PropSyng.png" alt="PropSyng Logo" class="logo" />
</router-link>
          <ul>
            <li>
              <a href="#">
                <youTube class="svg-icon" />
              </a>
            </li>
            <li>
              <a href="#">
                <twitter class="svg-icon" />
              </a>
            </li>
            <li>
              <a href="#">
                <instagram class="svg-icon" />
              </a>
            </li>
            <li>
              <a href="#">
                <linkedin class="svg-icon" />
              </a>
            </li>
          </ul>
        </div>
        <div class="col-2">
          <ul>
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
        </div>
      </div>
      <div class="right">
        <p>@Copyright 2025 Todos los derechos reservados</p>
      </div>
    </div>
  </footer>
</template>

<!-- Aqui esta los iconos-->
<script>
import youTube from "../assets/Icons/youtube-brands.svg";
import twitter from "../assets/Icons/twitter-brands.svg";
import instagram from "../assets/Icons/instagram-brands.svg";
import linkedin from "../assets/Icons/linkedin-brands.svg";
export default {
  name: "footer-vue",
  components: {
    youTube,
    twitter,
    instagram,
    linkedin,
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

<!-- Aqui esta los estilos-->
<style lang="scss" scoped>
.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none; // quita el subrayado de link
  margin-bottom: 16px;

  @media (min-width: 800px) {
    margin-bottom: 0;
  }
}

.logo {
  height: 90px; // ajusta según lo grande que quieras el logo
  width: auto;
  display: block;
}
footer {
  margin-top: auto;
  padding: 100px 25px;
  background-color: #265381;

  .container {
    display: flex;
    flex-direction: column;
    gap: 32px;

    @media (min-width: 800px) {
      flex-direction: row;
      gap: 0px;
    }

    >div {
      display: flex;
      flex: 1;
    }

    .left {
      gap: 32px;
      color: #fff;
      display: flex;
      flex-direction: column;
      align-items: center;

      @media (min-width: 800px) {
        flex-direction: row;
        align-items: initial;
        gap: 0;
      }

      .header {
        text-align: center;
        font-size: 24px;
        color: #11bcd5;
        margin-bottom: 16px;
        text-decoration: none;
        font-weight: 600;

        @media (min-width: 800px) {
          text-align: initial;
        }
      }

      ul {
        gap: 16px;
        list-style: none;
        display: flex;
      }

      .col-1,
      .col-2 {
        gap: 32px;
        display: flex;
        flex: 1;

        @media (min-width: 800px) {
          gap: 0;
        }
      }

      .col-1 {
        flex-direction: column;

        h2 {
          text-align: center;

          @media (min-width: 800px) {
            text-align: initial;
          }
        }

        ul {
          margin-top: auto;

          li {
            display: flex;
            align-items: center;

            .svg-icon {
              width: 24px;
              height: auto;
              color: #fff;
            }
          }
        }
      }

      .col-2 {
  ul {
    height: 100%;
    justify-content: center;
    flex-direction: row;
    flex-wrap: wrap;

    @media (min-width: 800px) {
      flex-direction: column;
    }

    .link {
      font-size: 16px;
      font-weight: 500;
      color: #fff;
      text-decoration: none;
      transition: color 0.3s ease; // animación suave

      &:hover {
        color: #11bcd5; // el color que quieras al hacer hover
      }
    }
  }
}
    }

    .right {
      gap: 32px;
      color: #fff;
      align-items: center;
      flex-direction: column;

      @media (min-width: 800px) {
        align-items: flex-end;
        gap: 0;
      }
    }

    p {
      margin-top: auto;
    }
  }
}
</style>