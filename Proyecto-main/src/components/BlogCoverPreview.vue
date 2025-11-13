<template>
  <div class="blog-cover-preview">
    <div class="preview-container">
      <img :src="blogPhotoFileURL" alt="Preview" />
      <button class="close-button" @click="closePreview">X</button>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    closePreview() {
      this.$emit('close-preview');
    }
  },
  computed: {
    blogPhotoFileURL() {
      return this.$store.state.blogPhotoFileURL;
    }
  }
}
</script>

<style scoped>
.blog-cover-preview {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  overflow: auto; /* Permite hacer scroll si la imagen es más grande que la pantalla */
}

.preview-container {
  position: relative;
  max-width: 90%; /* Limitar el ancho máximo del contenedor */
  max-height: 90vh; /* Limitar la altura máxima del contenedor */
}

.preview-container img {
  max-width: 100%; /* La imagen no excederá el ancho del contenedor */
  max-height: 90vh; /* La imagen no excederá el 90% de la altura de la ventana */
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  object-fit: contain; /* Mantiene la relación de aspecto */
}

.close-button {
  position: fixed; /* Cambiamos de absolute a fixed para que sea relativo a la ventana */
  top: 20px;
  right: 20px;
  background-color: #fff;
  color: #333;
  border: none;
  border-radius: 50%;
  width: 40px; /* Aumentamos un poco el tamaño para mejor visibilidad */
  height: 40px;
  font-size: 18px; /* Aumentamos el tamaño de la fuente */
  font-weight: bold;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  z-index: 1001; /* Aseguramos que esté por encima de todo */
}

.close-button:hover {
  background-color: #f0f0f0;
  transform: scale(1.1);
}
</style>