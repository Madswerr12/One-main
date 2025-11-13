<template>
    <div class="blog-card">
        <div v-show="editPost" class="icons">
            <div v-if="admin" @click="editBlog" class="icon">
                <Edit class="edit"></Edit>
            </div>
            <div v-if="admin" @click="deletePost" class="icon">
                <Delete class="delete"></Delete>
            </div>
        </div>
        <img :src="post.blogCoverPhoto" alt="">
        <div class="info">
            <h4>{{ post.blogTitle }}</h4>

            <div class="tags-display">
                <span>Tag:</span>
                <span v-for="(tag, index) in (post.tags ? post.tags.join(', ').split(', ') : [])" :key="index"
                    class="tag">
                    "{{ tag.trim() }}"
                </span>
            </div>

            <h6>Publicado: {{ new Date(post.blogDate).toLocaleString("es-ES", { dateStyle: "long" }) }}</h6>

            <router-link class="link" :to="{ name: 'ViewBlog', params: { blogid: this.post.blogID } }">Ver
                <Arrow class="arrow" />
            </router-link>
        </div>
    </div>
</template>

<script>
import Arrow from "../assets/Icons/arrow-right-light.svg";
import Edit from "../assets/Icons/edit-regular.svg";
import Delete from "../assets/Icons/trash-regular.svg";

export default {
    name: "blogCard",
    props: ["post"],
    components: {
        Arrow,
        Edit,
        Delete,
    },
    mounted() {
       // Verifica que los datos del post, incluyendo los tags, estén presentes
    },
    methods: {
        deletePost() {
            this.$store.dispatch("deletePost", this.post.blogID);
        },

        editBlog() {
            this.$router.push({ name: "EditBlog", params: { blogid: this.post.blogID } });
        },
    },
    computed: {
        editPost() {
            return this.$store.state.editPost;
        },

        user() {
            return this.$store.state.user;
        },
        admin() {
              return this.$store.state.profileRole === 'admin' || this.$store.state.profileRole === 'nomina';
        },
    }
};
</script>

<style lang="scss" scoped>
.blog-card {
    position: relative;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    border-radius: 8px;
    background-color: #fff;
    /* Ajustado el alto mínimo y máximo para controlar la dimensión vertical */
    min-height: 380px;
    max-height: 500px;
    transition: 0.5s ease all;

    &:hover {
        transform: rotateZ(-1deg) scale(1.01);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    .icons {
        display: flex;
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 99;

        .icon {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            background-color: #fff;
            transition: 0.5s ease all;

            &:hover {
                background-color: #303030;

                .edit,
                .delete {
                    path {
                        fill: #fff;
                    }
                }
            }

            &:nth-child(1) {
                margin-right: 8px;
            }

            .edit,
            .delete {
                pointer-events: none;
                height: 15px;
                width: auto;
            }
        }
    }

    img {
        display: block;
        border-radius: 8px 8px 0 0;
        z-index: 1;
        width: 100%;
        /* Limitar la altura de la imagen para evitar que se estire demasiado */
        height: 180px;
        object-fit: cover;
    }

    .info {
        display: flex;
        flex-direction: column;
        /* Ajustar la altura para que ocupe el espacio restante */
        flex: 1;
        z-index: 3;
        /* Reducir el padding para optimizar el espacio */
        padding: 20px 16px;
        color: #000;
        /* Permitir scroll si el contenido es demasiado largo */
        overflow-y: auto;

        h4 {
            padding-bottom: 8px;
            font-size: 20px;
            font-weight: bold;
        }

        h6 {
            font-weight: 400;
            font-size: 14px;
            padding-top: 12px;
            padding-bottom: 12px;
            margin-top: 12px;
            color: #777;
        }

        .tags-display {
            margin-top: 8px;
            font-size: 16px;

            span:first-child {
                font-weight: bold;
            }

            .tag {
                font-size: 16px; /* Reducido ligeramente */
                margin-left: 8px;
                padding: 2px 6px; /* Reducido el padding */
                background-color: #e0e0e0;
                border-radius: 4px;
            }
        }

        .link {
            display: inline-flex;
            align-items: center;
            margin-top: auto;
            font-weight: 500;
            padding-top: 16px;
            font-size: 12px;
            padding-bottom: 4px;
            transition: 0.5s ease-in all;

            &:hover {
                color: rgba(48, 48, 48, 0.8);
            }

            .arrow {
                width: 10px;
            }
        }
    }
}
</style>