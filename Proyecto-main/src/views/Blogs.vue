<template>
    <div class="blog-card-wrap">
        <div class="blog-cards container">
            <!-- Barra de búsqueda y modo de edición -->
            <div class="toggle-edit">
                <input 
                    type="text" 
                    v-model="searchQuery" 
                    placeholder="Buscar por título..." 
                    class="search-input" 
                />
                <span>Editar Noticias</span>
                <input type="checkbox" v-model="editPost" />
            </div>

            <!-- Mostrar publicaciones filtradas -->
            <BlogCard 
                :post="post" 
                v-for="(post, index) in filteredPosts" 
                :key="index" 
            />
        </div>
    </div>
</template>

<script>
import BlogCard from "../components/BlogCard";

export default {
    name: "Cards",
    components: { BlogCard },
    data() {
        return {
            searchQuery: "", // Reactivo para almacenar la búsqueda del usuario
        };
    },
    computed: {
        // Accede a las publicaciones desde Vuex
        blogPosts() {
            return this.$store.state.blogPosts;
        },
        // Sincroniza el estado de edición
        editPost: {
            get() {
                return this.$store.state.editPost;
            },
            set(payload) {
                this.$store.commit("toggleEditPost", payload);
            },
        },
        // Filtrar publicaciones según el texto ingresado
        filteredPosts() {
        return this.blogPosts.filter(post => {
            const blogTitle = post.blogTitle || "";
            const tags = post.tags ? post.tags.join(", ").toLowerCase() : "";

            // Filtrar por título o por tags
            return blogTitle.toLowerCase().includes(this.searchQuery.toLowerCase()) || 
                   tags.includes(this.searchQuery.toLowerCase());
        });
        },
    },
    beforeDestroy() {
        // Restaurar el estado de edición al desmontar el componente
        this.$store.commit("toggleEditPost", false);
    },
};
</script>

<style lang="scss" scoped>
.blog-cards {
    position: relative;

    .toggle-edit {
        display: flex;
        align-items: center;
        position: absolute;
        top: -70px;
        right: 0;
        gap: 1rem; // Espaciado uniforme

        span {
            margin-right: 8px;
        }

        /* 🔹 Estilo del input de búsqueda */
        .search-input {
            width: 100%;
            max-width: 220px;
            height: 45px;
            padding: 12px;
            border-radius: 12px;
            border: 1.5px solid lightgrey;
            outline: none;
            transition: all 0.3s cubic-bezier(0.19, 1, 0.22, 1);
            box-shadow: 0px 0px 20px -18px;
            font-size: 0.95rem;
        }

        .search-input:hover {
            border: 2px solid lightgrey;
            box-shadow: 0px 0px 20px -17px;
        }

        .search-input:active {
            transform: scale(0.95);
        }

        .search-input:focus {
            border: 2px solid grey;
        }

        /* 🔹 Checkbox toggle */
        input[type="checkbox"] {
            position: relative;
            border: none;
            -webkit-appearance: none;
            background: #fff;
            outline: none;
            width: 80px;
            height: 30px;
            border-radius: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                        0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        input[type="checkbox"]:before {
            content: "";
            position: absolute;
            width: 30px;
            height: 30px;
            border-radius: 20px;
            top: 0;
            left: 0;
            background: #303030;
            transform: scale(1.1);
            transition: 750ms ease all;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                        0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        input:checked[type="checkbox"]:before {
            background: #fff;
            left: 52px;
        }
    }
}

</style>
