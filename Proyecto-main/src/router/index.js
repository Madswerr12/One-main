import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";
import Blogs from "../views/Blogs.vue";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import Tickets from "../views/Tickets.vue";
import Profile from "../views/Profile.vue";
import CreatePost from "../views/CreatePost.vue";
import BlogPreview from "../views/BlogPreview.vue";
import ViewBlog from "../views/ViewBlog.vue";
import EditBlog from "../views/EditBlog.vue";
import PricesTab from "@/views/PricesTab.vue";
import PaymentsTab from "@/views/PaymentsTab.vue";
import firebase from "firebase/app";
import "firebase/auth";
import "firebase/firestore";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
    meta: {
      title: "Inicio",
    },
  },
  {
    path: "/Cards",
    name: "Cards",
    component: Blogs,
    meta: {
      title: "Noticias",
      requiresAuth: true,
    },
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: {
      title: "Login",
      requiresAuth: false,
    },
  },
  {
    path: "/register",
    name: "Register",
    component: Register,
    meta: {
      title: "Crear Usuarios",
      requiresAuth: true,
      requiresAdmin: true,
    },
  },
  {
    path: "/tickets",
    name: "Tickets",
    component: Tickets,
    meta: {
      title: "Tickets",
      requiresAuth: true,
      requiresCasos: true,
    },
  },
  {
    path: "/profile",
    name: "Profile",
    component: Profile,
    meta: {
      title: "Profile",
      requiresAuth: true,
    },
  },
  {
    path: "/create-post",
    name: "CreatePost",
    component: CreatePost,
    meta: {
      title: "Crear Noticias",
      requiresAuth: true,
      // Cambiamos la lógica: en lugar de requiresNomina, usamos requiresAnyRole
      requiresAnyRole: ['admin', 'nomina']
    },
  },
  {
    path: "/post-preview",
    name: "BlogPreview",
    component: BlogPreview,
    meta: {
      title: "Preview",
      requiresAuth: true,
    },
  },
  {
    path: "/Card:blogid",
    name: "ViewBlog",
    component: ViewBlog,
    meta: {
      title: "Card",
      requiresAuth: true,
    },
  },
  {
    path: "/precios",
    name: "Precios",
    component: PricesTab,
    meta: {
      title: "Precios",
      requiresAuth: true,
      requiresAnyRole: ['admin', 'nomina']
    }
  },
  {
    path: "/pagos",
    name: "Pagos",
    component: PaymentsTab,
    meta: { 
      requiresAuth: true,
      title: "Pagos",
      
    }
  },
  {
    path: "/Editar-Card/:blogid",
    name: "EditBlog",
    component: EditBlog,
    meta: {
      title: "Editar-Card",
      requiresAuth: true,
      requiresAnyRole: ['admin', 'nomina']
    },
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

router.beforeEach(async (to, from, next) => {
  document.title = `${to.meta.title} | PropSyng`;

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin);
  const requiresAnyRole = to.matched.some(record => record.meta.requiresAnyRole);
  
  const user = firebase.auth().currentUser;

  if (requiresAuth && !user) {
    next({ name: 'Login' });
  } else if (user) {
    try {
      const userDoc = await firebase.firestore().collection('users').doc(user.uid).get();

      if (!userDoc.exists) {
        console.error("Documento del usuario no encontrado");
        next({ name: 'Home' });
        return;
      }

      const userData = userDoc.data();
      // Convertimos el rol a minúsculas para evitar problemas de mayúsculas/minúsculas
      const userRole = userData.role ? userData.role.toLowerCase() : '';
 

      // Verificar si la ruta requiere admin y el usuario no es admin
      if (requiresAdmin && userRole !== 'admin') {
        console.log("Acceso denegado: se requiere rol de admin");
        next({ name: 'Home' });
      } 
      // Verificar si la ruta requiere cualquiera de los roles especificados
      else if (requiresAnyRole) {
        const allowedRoles = to.matched.reduce((roles, record) => {
          if (record.meta.requiresAnyRole) {
            return [...roles, ...record.meta.requiresAnyRole];
          }
          return roles;
        }, []);
        
        if (!allowedRoles.includes(userRole)) {
          console.log(`Acceso denegado: se requiere uno de los siguientes roles: ${allowedRoles.join(', ')}. Rol del usuario: ${userRole}`);
          next({ name: 'Home' });
        } else {
          next();
        }
      } 
      else {
        next();
      }
    } catch (error) {
      console.error("Error al verificar el rol:", error);
      next({ name: 'Home' });
    }
  } else {
    next();
  }
});

export default router;