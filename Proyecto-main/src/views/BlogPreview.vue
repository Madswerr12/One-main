<!-- PostPreview.vue -->
<template>
  <div class="post-view">
    <div class="container quillWrapper">
      <!-- Botón de volver -->
      <button class="back-btn" @click="goBack">
        <span class="arrow">←</span> Volver
      </button>

      <h2>{{ blogTitle }}</h2>
      <img :src="blogCoverPhoto" alt="Imagen de portada" />
      <div class="post-content ql-editor" v-html="blogHTML"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PostPreview",
  computed: {
    blogTitle() {
      return this.$store.state.blogTitle;
    },
    blogHTML() {
      return this.$store.state.blogHTML;
    },
    blogCoverPhoto() {
      return this.$store.state.blogPhotoFileURL;
    },
  },
  methods: {
    goBack() {
      window.history.back();
    },
  },
};
</script>

<style lang="scss">
.post-view {
  min-height: 100%;
  background-color: #f9fafb;

  .container {
    max-width: 1000px;
    padding: 60px 25px;
    margin: auto;
    position: relative;
  }

  .back-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background-color: #16baf4; /* Azul elegante */
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 18px;
    font-size: 15px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 8px rgba(37, 99, 235, 0.2);
    margin-bottom: 25px;

    &:hover {
      background-color: #bcdbe6;
      transform: translateY(-2px);
      box-shadow: 0 6px 12px rgba(37, 99, 235, 0.3);
    }

    .arrow {
      font-size: 18px;
      font-weight: bold;
    }
  }

  h2 {
    margin-bottom: 16px;
    font-weight: 400;
    font-size: 32px;
    color: #1e293b;
  }

  .container > img {
    width: 100%;
    border-radius: 8px;
    margin-bottom: 32px;
  }

  .post-content img {
    max-width: 100%;
    height: auto;
  }
}
</style>
