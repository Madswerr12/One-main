<!-- Aqui esta la pagina principal-->
<template>
  <div class="home">
    <BlogPost :post="welcomeScreen"/>
 
 

    <div v-if="!user" class="space-above-updates">
      <div class="updates">
        <div class="container">
          <h2>Ingresa a PropSyng para ver todas las noticias y pagos de la copropiedad</h2>
          <router-link class="router-button" :to="{ name: 'Login' }">
            Ingresa ahora <Arrow class="arrow arrow-light"/>
          </router-link>
        </div>
      </div>
    </div>
    
    <div class="blog-card-wrap">
      <div class="container">
        <h3>Últimas noticias</h3>
        <div class="blog-cards"> 
          <BlogCard :post="post" v-for="(post, index) in blogPostsCards" :key="index" />
        </div>
        </div>
      </div>

     
  </div>
</template>

<script>
import BlogPost from "../components/BlogPost";
import BlogCard from "../components/BlogCard";
import Arrow from "../assets/Icons/arrow-right-light.svg";


export default {
  name: "Home",
  components: {BlogPost, BlogCard, Arrow},
  data() {
    return {
      welcomeScreen: {
        title: "Bienvenido a PropSyng",
        blogPost:
          "Aquí puedes ver las noticias más recientes de tu comunidad, para poder ver más noticias y realizar pagos.",
        welcomeScreen: true,
        photo: "1",
      },

    };
  },

  computed: {
    blogPostsFeed(){
      return this.$store.getters.blogPostsFeed;
    },
    blogPostsCards(){
      return this.$store.getters.blogPostsCards;
    },

      user(){
        return this.$store.state.user;
      },
   
  },
};
</script>

<style lang="scss" scoped>
.blog-card-wrap {
  h3 {
    font-weight: bold;
    font-size: 28px;
    margin-bottom: 10px;
  }
}

.updates {
  .container {
    padding: 100px 25px;
    display: flex;
    flex-direction: column;
    align-items: center;
    @media (min-width: 800px) {
      padding: 125px 25px;
      flex-direction: row;
    }

    .router-button {
  display: flex;
  font-size: 14px;
  text-decoration: none;
  padding: 10px 20px; // Añade un poco de relleno para un mejor aspecto
  border: 2px solid #00e1ff; // Cambia esto al color del contorno que desees
  border-radius: 5px; // Ajusta el radio de los bordes
  text-transform: capitalize;
  color: #f8f8f8; // Cambia esto al color de la fuente que desees
  transition: background-color 0.3s, color 0.3s; // Transición suave para efectos

  // Efecto hover
  &:hover {
    background-color: #706e6e; // Cambia esto al color que desees al pasar el mouse
    color: rgb(255, 255, 255); // Cambia el color del texto al pasar el mouse
  }

  @media (min-width: 800px) {
    margin-left: auto;
  }
}

    h2 {

      font-weight: bold;
      font-size: 32px;
      max-width: 425px;
      width: 100%;
      text-align: center;
      color: #000000;
      @media (min-width: 800px) {
        text-align: initial;
        font-size: 40px;
      }
    }
  }
}

.space-above-updates {
  background-color: rgb(255, 255, 255);
  padding: 20px 0; // Ajusta el padding según sea necesario
  
}

.welcome-title {
  font-weight: bold; // Make it bold
}

</style>