<template>
<div class="create-post">
<BlogCoverPreview v-show="showPreview" @close-preview="closePreview" />
<Loading v-show="loading" />
<div class="container">
<div :class="{ invisible: !error }" class="err-message">
<p><span>Error:</span>{{ this.errorMsg }}</p>
</div>
<div class="blog-info">
<input type="text" placeholder="Poner título" v-model="blogTitle" />


<div class="upload-file">
<label for="blog-photo">Subir foto principal</label>
<input type="file" ref="blogPhoto" id="blog-photo" @change="fileChange" accept=".png, .jpg, ,jpeg" />
<button @click="togglePreview" class="preview"
:class="{ 'button-inactive': !this.$store.state.blogPhotoFileURL }">
Visualizar foto
</button>

<span>Imagen principal: {{ this.$store.state.blogPhotoName }}</span>


</div>
<span id="item1">Palabras Clave:</span>
<input type="text" v-model="tags" placeholder="Separado por comas" />
</div>


<div class="editor">
<vue-editor :editorOptions="editorSettings" v-model="blogHTML" useCustomImageHandler
@image-added="imageHandler" />
</div>
<div class="blog-actions">
<button @click="uploadBlog">Crear noticia</button>
<router-link class="router-button1" :to="{ name: 'BlogPreview' }">Visualizar noticia</router-link>
</div>
</div>
</div>
</template>

<script>
import BlogCoverPreview from "../components/BlogCoverPreview";
import Loading from "../components/Loading";
import firebase from "firebase/app";
import "firebase/storage";
import db from "../firebase/firebaseInit";
import Quill from "quill";
window.Quill = Quill;
const ImageResize = require("quill-image-resize-module").default;
Quill.register("modules/imageResize", ImageResize);

export default {
name: "CreatePost",
data() {
return {
file: null,
error: null,
errorMsg: null,
loading: null,
editorSettings: {
modules: {
imageResize: {},
},
},
showPreview: false, // Control local para la vista previa
};
},
components: {
BlogCoverPreview,
Loading,
},
methods: {
resetFields() {
this.$store.commit("updateBlogTitle", "");
this.$store.commit("newBlogPost", "");
this.$store.commit("fileNameChange", "");
this.$store.commit("createFileURL", "");
this.$store.commit("openPhotoPreview", false);
this.$store.commit("updateBlogTags", "");
this.$store.commit("setBlogPhotoFile", null);
this.showPreview = false; // Resetear vista previa local
},
fileChange() {
this.file = this.$refs.blogPhoto.files[0];
const fileName = this.file.name;
this.$store.commit("fileNameChange", fileName);
this.$store.commit("createFileURL", URL.createObjectURL(this.file));
this.$store.commit("setBlogPhotoFile", this.file);
this.showPreview = false; // Ocultar vista previa al cambiar archivo
},
togglePreview() {
// Solo mostrar vista previa si hay una URL de imagen
if (this.$store.state.blogPhotoFileURL) {
this.showPreview = !this.showPreview;
// Sincronizar con el store
this.$store.commit("openPhotoPreview", this.showPreview);
}
},
closePreview() {
this.showPreview = false;
this.$store.commit("openPhotoPreview", false);
},
imageHandler(file, Editor, cursorLocation, resetUploader) {
const storageRef = firebase.storage().ref();
const docRef = storageRef.child(`documents/blogPostPhotos/${file.name}`);
docRef.put(file).on(
"state_changed",
(snapshot) => {
console.log(snapshot);
},
(err) => {
console.log(err);
},
async () => {
const downloadURL = await docRef.getDownloadURL();
Editor.insertEmbed(cursorLocation, "image", downloadURL);
resetUploader();
}
);
},
uploadBlog() {
if (this.blogTitle.length !== 0 && this.blogHTML.length !== 0) {
const file = this.$store.state.blogPhotoFile;
if (file) {
this.loading = true;
const storageRef = firebase.storage().ref();
const docRef = storageRef.child(`documents/BlogCoverPhotos/${this.$store.state.blogPhotoName}`);
docRef.put(file).on(
"state_changed",
(snapshot) => {
console.log(snapshot);
},
(err) => {
console.log(err);
this.loading = false;
},
async () => {
const downloadURL = await docRef.getDownloadURL();
const timestamp = await Date.now();
const tagsArray = this.tags.split(",").map(tag => tag.trim());
const dataBase = await db.collection("blogPosts").doc();

await dataBase.set({
blogID: dataBase.id,
blogHTML: this.blogHTML,
blogCoverPhoto: downloadURL,
blogCoverPhotoName: this.blogCoverPhotoName,
blogTitle: this.blogTitle,
profileId: this.profileId,
date: timestamp,
tags: tagsArray,
});
await this.$store.dispatch("getPost");
this.loading = false;
this.$router.push({ name: "ViewBlog", params: { blogid: dataBase.id } });
}
);
return;
}
this.error = true;
this.errorMsg = "Please ensure you uploaded a cover photo!";
setTimeout(() => {
this.error = false;
}, 5000);
return;
}
this.error = true;
this.errorMsg = "Please ensure Blog Title & Blog Post has been filled!";
setTimeout(() => {
this.error = false;
}, 5000);
return;
},
},
computed: {
profileId() {
return this.$store.state.profileId;
},
blogCoverPhotoName() {
return this.$store.state.blogPhotoName;
},
blogTitle: {
get() {
return this.$store.state.blogTitle;
},
set(payload) {
this.$store.commit("updateBlogTitle", payload);
},
},
blogHTML: {
get() {
return this.$store.state.blogHTML;
},
set(payload) {
this.$store.commit("newBlogPost", payload);
},
},
tags: {
get() {
return this.$store.state.blogTags;
},
set(payload) {
this.$store.commit("updateBlogTags", payload);
},
},
},
beforeRouteEnter(to, from, next) {
next(vm => {
// No cerrar la vista previa al volver de BlogPreview
if (from.name !== 'BlogPreview') {
vm.resetFields();
}
// Asegurar que la vista previa local esté cerrada al entrar
vm.showPreview = false;
});
},
created() {
// Asegurar que la vista previa local esté cerrada al crear el componente
this.showPreview = false;
},
};
</script>

<style lang="scss">
/* CSS más limpio y compatible */
/* Selector específico para tu elemento */
#item1 {
  font-size: 15px;
  margin-top: 14px;
  font-family: "Quicksand", sans-serif;

  
}

.create-post {
position: relative;
height: 100%;

button {
margin-top: 0;
}

.router-button {
color: #fff;
text-decoration: capitalize;
}

label,
button,
.router-button1 {
transition: 0.5s ease-in-out all;
align-self: center;
font-size: 14px;
cursor: pointer;
border-radius: 20px;
padding: 12px 24px;
color: #fff;
background-color: #16baf4;
text-decoration: capitalize;
text-decoration: none;

&:hover {
background-color: #16baf4;
}
}

.container {
position: relative;
height: 100%;
padding: 10px 25px 60px;
}

// error styling
.invisible {
opacity: 0 !important;
}

.err-message {
width: 100%;
padding: 12px;
border-radius: 8px;
color: #fff;
margin-bottom: 10px;
background-color: #16baf4;
opacity: 1;
transition: 0.5s ease all;

p {
font-size: 14px;
}

span {
font-weight: 600;
}
}

.blog-info {
display: flex;
margin-bottom: 32px;

input:nth-child(1) {
min-width: 300px;
}

input {
transition: 0.5s ease-in-out all;
padding: 10px 4px;
border: none;
border-bottom: 1px solid #16baf4;

&:focus {
outline: none;
box-shadow: 0 1px 0 0 #16baf4;
}
}

.upload-file {
flex: 1;
margin-left: 16px;
position: relative;
display: flex;

input {
display: none;
}

.preview {
margin-left: 16px;
text-transform: initial;
}

span, [id="1"] {
font-size: 12px;
margin-left: 16px;
align-self: center;
}
}
}

.editor {
height: 60vh;
display: flex;
flex-direction: column;

.quillWrapper {
position: relative;
display: flex;
flex-direction: column;
height: 100%;
}

.ql-container {
display: flex;
flex-direction: column;
height: 100%;
overflow: scroll;
}

.ql-editor {
padding: 20px 16px 30px;
}
}

.blog-actions {
margin-top: 32px;
text-transform: capitalize;
button {
margin-right: 16px;
text-transform: capitalize;
}
}
}

.router-button {
color: #fff;
text-decoration: capitalize;
}

/* Agrega esta media query específica para 1200px */
@media (max-width: 1200px) {
.blog-info {
flex-wrap: wrap;
gap: 16px;
}

.blog-info input:nth-child(1) {
min-width: 250px;
flex: 1;
}

.tags-input {
flex: 1;
min-width: 200px;
}

.upload-file {
flex-basis: 100%;
margin-left: 0;
display: flex;
flex-wrap: wrap;
gap: 10px;
align-items: center;
}

.upload-file .preview {
margin-left: 0;
order: 2;
}

.upload-file span {
margin-left: 0;
order: 3;
flex-basis: 100%;
}
}

/* Mantén la media query existente para 768px */
@media (max-width: 1200px) {
.blog-info {
flex-direction: column;
align-items: flex-start;
}

.upload-file {
margin-top: 16px;
width: 100%;
}
}
</style>