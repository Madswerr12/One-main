<template>
  <div class="tickets-container">
    <div class="planContainer">
      <div class="plan">
        <div class="titleContainer">
          <div class="title">Sistema de Casos</div>
        </div>

        <div class="infoContainer">
          <!-- Crear Ticket (solo cliente) -->
          <form v-if="!isAdmin" class="ticket-form" @submit.prevent="createTicket">
            <input v-model="title" type="text" placeholder="Título del caso" required />
            <textarea v-model="description" placeholder="Descripción inicial" required></textarea>

            <!-- Campo para adjuntar documento -->
            <div class="file-upload-container">
              <label for="document" class="file-label"> Adjuntar documento</label>
              <input type="file" id="document" @change="handleDocumentUpload" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                class="file-input" />
              <span v-if="documentName" class="file-name">{{ documentName }}</span>
            </div>

            <button type="submit" class="btn-create">➕ Crear Caso</button>
          </form>

          <!-- Buscador -->
          <div class="search-bar">
            <input type="text" v-model="search" placeholder=" Buscar por número o título..." />
          </div>

          <div class="main-grid">
            <!-- Lista de Tickets -->
            <div class="tickets-list">
              <h3 class="subtitle">
                {{ isAdmin ? " Todos los Casos" : "Mis Casos" }}
              </h3>

              <!-- Si es admin, agrupamos por estado -->
              <template v-if="isAdmin">
                <div v-for="estado in ['Abierto', 'En progreso', 'Cerrado']" :key="estado">
                  <h4 class="estado-title"> {{ estado }}</h4>
                  <div class="tickets-group">
                    <div v-for="ticket in ticketsByStatus(estado)" :key="ticket.id" class="ticket-card"
                      @click="selectTicket(ticket)">
                      <div class="ticket-header">
                        <span class="ticket-id">#{{ ticket.caseNumber }}</span>
                        <span class="status" :class="statusClass(ticket.status)">
                          {{ ticket.status }}
                        </span>
                      </div>
                      <h4 class="ticket-title">{{ ticket.title }}</h4>
                      <p class="description">{{ ticket.initialDescription }}</p>
                      <small class="meta">
                        {{ ticket.createdAt.toDate().toLocaleString() }}
                      </small>
                      <br />
                      <small>👤 {{ ticket.userName }}</small>
                    </div>
                  </div>
                  <hr />
                </div>
              </template>

              <!-- Si no es admin, lista normal -->
              <template v-else>
                <div class="tickets-group">
                  <div v-for="ticket in filteredTickets" :key="ticket.id" class="ticket-card"
                    @click="selectTicket(ticket)">
                    <div class="ticket-header">
                      <span class="ticket-id">#{{ ticket.caseNumber }}</span>
                      <span class="status" :class="statusClass(ticket.status)">
                        {{ ticket.status }}
                      </span>
                    </div>
                    <h4 class="ticket-title">{{ ticket.title }}</h4>
                    <p class="description">{{ ticket.initialDescription }}</p>
                    <small class="meta">
                      {{ ticket.createdAt.toDate().toLocaleString() }}
                    </small>
                  </div>
                </div>
              </template>
            </div>

            <!-- Detalle del caso seleccionado -->
            <div v-if="selectedTicket" class="ticket-detail">
              <div class="detail-header">
                <h3 class="detail-title">
                  Seguimientos de:
                </h3>
                <h4 class="case-title">{{ selectedTicket.title }} (#{{ selectedTicket.caseNumber }})</h4>
              </div>

              <!-- Mostrar documento adjunto si existe -->
              <div v-if="selectedTicket.documentUrl" class="ticket-document">
                <p><strong>Documento adjunto:</strong></p>
                <a :href="selectedTicket.documentUrl" target="_blank" class="document-link">
                  {{ selectedTicket.documentName }}
                </a>
              </div>

              <!-- Estado (solo admin puede cambiar) -->
              <div v-if="isAdmin" class="estado-control">
                <label for="status">Estado:</label>
                <select v-model="selectedTicket.status" @change="updateStatus">
                  <option>Abierto</option>
                  <option>En progreso</option>
                  <option>Cerrado</option>
                </select>
              </div>
              <div v-else>
                <strong>Estado:</strong> {{ selectedTicket.status }}
              </div>

              <!-- Lista de seguimientos -->
              <div class="updates-list">
                <div v-for="u in updates" :key="u.id" class="update-card"
                  :class="{ internal: u.internal, 'my-message': u.author === userEmail }">
                  <p class="update-text">{{ u.text }}</p>
                  <!-- Imagen adjunta -->
                  <div v-if="u.imageUrl" class="image-container">
                    <img :src="u.imageUrl" class="update-image" @click="openImageModal(u.imageUrl)" />
                  </div>
                  <small>
                    {{ u.author }} - {{ u.date.toDate().toLocaleString() }}
                    <span v-if="u.internal && isAdmin" class="tag-internal">INTERNAL</span>
                  </small>
                </div>
              </div>

              <!-- Añadir seguimiento -->
              <form v-if="selectedTicket.status !== 'Cerrado'" class="update-form" @submit.prevent="addUpdate">
                <textarea v-model="newUpdate" placeholder="Añadir seguimiento..." required></textarea>
                <!-- Input para imagen -->
                <input type="file" @change="handleFileUpload" accept="image/*" />
                <div class="actions">
                  <button type="submit" class="btn-update"> Añadir</button>
                  <label v-if="isAdmin" class="internal-check container">
                    <input type="checkbox" v-model="internalNote" />
                    <span class="checkmark"></span>
                    Nota interna
                  </label>
                </div>
              </form>
              <div v-else class="closed-msg">
                Este caso está cerrado. No se pueden añadir más seguimientos.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para ver imágenes completas -->
    <div v-if="showImageModal" class="image-modal" @click="closeImageModal">
      <div class="modal-content" @click.stop>
        <span class="close-modal" @click="closeImageModal">&times;</span>
        <img :src="modalImageUrl" class="modal-image" />
      </div>
    </div>
  </div>
</template>

<script>
import firebase from "firebase/app";
import "firebase/auth";
import "firebase/storage";
import db from "../firebase/firebaseInit";

export default {
  name: "Tickets",
  data() {
    return {
      title: "",
      description: "",
      tickets: [],
      userId: null,
      userEmail: null,
      isAdmin: false,
      selectedTicket: null,
      updates: [],
      newUpdate: "",
      internalNote: false,
      search: "",
      lastCaseNumber: 0,
      selectedFile: null, // Para actualizaciones
      documentFile: null, // Para creación de tickets
      documentName: "", // Nombre del documento a mostrar
      showImageModal: false,
      modalImageUrl: "",
      fromChatbot: false, // Para saber si viene del chatbot
    };
  },
  computed: {
    filteredTickets() {
      let list = this.isAdmin ? this.tickets : this.tickets.filter((t) => t.userId === this.userId);
      if (this.search.trim()) {
        const term = this.search.toLowerCase();
        list = list.filter(
          (t) => t.title.toLowerCase().includes(term) || String(t.caseNumber).includes(term)
        );
      }
      // Admin: casos cerrados al final
      if (this.isAdmin) {
        return list.sort((a, b) => {
          if (a.status === "Cerrado" && b.status !== "Cerrado") return 1;
          if (a.status !== "Cerrado" && b.status === "Cerrado") return -1;
          return b.createdAt.seconds - a.createdAt.seconds;
        });
      }
      return list;
    },
  },
  methods: {
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
    },
    handleDocumentUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.documentFile = file;
        this.documentName = file.name;
      } else {
        this.documentFile = null;
        this.documentName = "";
      }
    },
    async createTicket() {
      if (!this.title || !this.description) return;
      const user = firebase.auth().currentUser;

      // Incrementar número de caso
      const newCaseNumber = this.lastCaseNumber + 1;

      let documentUrl = null;

      // Subir documento a Storage si existe
      if (this.documentFile) {
        const storageRef = firebase.storage().ref();
        const documentRef = storageRef.child(
          `tickets/documents/${newCaseNumber}_${Date.now()}_${this.documentFile.name}`
        );
        await documentRef.put(this.documentFile);
        documentUrl = await documentRef.getDownloadURL();
      }

      // Crear el ticket
      const newTicketRef = await db.collection("tickets").add({
        title: this.title,
        initialDescription: this.description,
        status: "Abierto",
        createdAt: new Date(),
        userId: user.uid,
        userName: user.email,
        caseNumber: newCaseNumber,
        documentUrl: documentUrl,
        documentName: this.documentName,
      });

      // Crear el seguimiento inicial con la descripción
      await db.collection("tickets").doc(newTicketRef.id).collection("updates").add({
        text: this.description,
        author: user.email,
        date: new Date(),
        internal: false,
        imageUrl: null,
      });

      this.lastCaseNumber = newCaseNumber;
      this.title = "";
      this.description = "";
      this.documentFile = null;
      this.documentName = "";
      this.fromChatbot = false; // Reiniciar el flag
      this.loadTickets();

      // Abrir detalle directamente
      const doc = await db.collection("tickets").doc(newTicketRef.id).get();
      this.selectTicket({ id: doc.id, ...doc.data() });
    },
    async loadTickets() {
      const snapshot = await db
        .collection("tickets")
        .orderBy("createdAt", "desc")
        .get();
      this.tickets = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));
      // Obtener último número de caso
      if (this.tickets.length > 0) {
        this.lastCaseNumber = Math.max(
          ...this.tickets.map((t) => t.caseNumber || 0)
        );
      }
    },
    async selectTicket(ticket) {
      this.selectedTicket = ticket;
      this.loadUpdates(ticket.id);
    },
    async loadUpdates(ticketId) {
      const snapshot = await db
        .collection("tickets")
        .doc(ticketId)
        .collection("updates")
        .orderBy("date", "asc")
        .get();
      this.updates = snapshot.docs
        .map((doc) => ({
          id: doc.id,
          ...doc.data()
        }))
        .filter((u) => {
          if (this.isAdmin) return true;
          if (u.author === this.userEmail) return true;
          return u.internal === false;
        });
    },
    async addUpdate() {
      if (!this.newUpdate && !this.selectedFile) return;
      const user = firebase.auth().currentUser;
      let imageUrl = null;

      // Subir archivo a Storage si existe
      if (this.selectedFile) {
        const storageRef = firebase.storage().ref();
        const fileRef = storageRef.child(
          `tickets/${this.selectedTicket.id}/${Date.now()}_${this.selectedFile.name}`
        );
        await fileRef.put(this.selectedFile);
        imageUrl = await fileRef.getDownloadURL();
      }

      await db
        .collection("tickets")
        .doc(this.selectedTicket.id)
        .collection("updates")
        .add({
          text: this.newUpdate,
          author: user.email,
          date: new Date(),
          internal: this.isAdmin ? this.internalNote : false,
          imageUrl: imageUrl,
        });

      // Reset
      this.newUpdate = "";
      this.internalNote = false;
      this.selectedFile = null;
      this.loadUpdates(this.selectedTicket.id);
    },
    async updateStatus() {
      await db.collection("tickets").doc(this.selectedTicket.id).update({
        status: this.selectedTicket.status,
      });
      this.loadTickets();
    },
    ticketsByStatus(status) {
      return this.filteredTickets.filter((t) => t.status === status);
    },
    statusClass(status) {
      return {
        abierto: status === "Abierto",
        progreso: status === "En progreso",
        cerrado: status === "Cerrado",
      };
    },
    openImageModal(imageUrl) {
      this.modalImageUrl = imageUrl;
      this.showImageModal = true;
    },
    closeImageModal() {
      this.showImageModal = false;
      this.modalImageUrl = "";
    },
  },
  async mounted() {
    const user = firebase.auth().currentUser;
    this.userId = user.uid;
    this.userEmail = user.email;
    const userDoc = await db.collection("users").doc(user.uid).get();
    this.isAdmin = userDoc.exists && (userDoc.data().role === "admin" || userDoc.data().role === "Casos" || userDoc.data().role === "nomina");
    
    // Verificar si viene una pregunta desde el chatbot
    if (this.$route.query.question) {
      this.title = this.$route.query.question.substring(0, 50); // Tomar los primeros 50 caracteres para el título
    
      this.fromChatbot = true;
      
      // Si viene del chatbot, mostrar un mensaje
      if (this.$route.query.fromChat) {
        this.$nextTick(() => {
          // Usar un mensaje más amigable que una alerta
          const notification = document.createElement('div');
          notification.className = 'chatbot-notification';
          notification.textContent = 'Puedes editar el título y descripción antes de crear el caso';
          document.querySelector('.ticket-form').prepend(notification);
          
          // Eliminar la notificación después de 5 segundos
          setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
              notification.remove();
            }, 500);
          }, 5000);
        });
      }
    }
    
    this.loadTickets();
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css?family=Open+Sans:400,600,700,800');

body {
  background: linear-gradient(135deg, #1e3c72, #2a5298);
  font-family: 'Open Sans', sans-serif;
  margin: 0;
  min-height: 100vh;
}

.tickets-container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  box-sizing: border-box;
}

.planContainer {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.plan {
  background: #eef3ff;
  width: 100%;
  max-width: 1100px;
  box-sizing: border-box;
  text-align: center;
  border-radius: 16px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  margin: 20px;
}

.titleContainer {
  background: #2a5298;
  padding: 1.2em;
}

.title {
  font-size: clamp(1.8rem, 3vw, 2.5rem);
  text-transform: uppercase;
  color: #fff;
  font-weight: 800;
  letter-spacing: 1px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.infoContainer {
  padding: 1.5em;
  color: #2d3b48;
}

/* Formulario de creación */
.ticket-form {
  background: #e7f9ff;
  padding: 1.5rem;
  border-radius: 12px;
  margin: 0 auto 2rem auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  max-width: 600px;
  width: 100%;
  box-sizing: border-box;
  position: relative;
}

.ticket-form input,
.ticket-form textarea {
  padding: 0.9rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  width: 100%;
  font-family: 'Open Sans', sans-serif;
  box-sizing: border-box;
}

.ticket-form textarea {
  resize: none;
  height: 120px;
}

.btn-create,
.btn-update {
  background: #2a5298;
  color: white;
  border: none;
  padding: 0.9rem;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  transition: 0.3s;
  width: 100%;
  box-sizing: border-box;
}

.btn-create:hover,
.btn-update:hover {
  background: #1e3c72;
}

/* Notificación del chatbot */
.chatbot-notification {
  background-color: #4CAF50;
  color: white;
  padding: 10px 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  font-weight: 500;
  transition: opacity 0.5s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  position: relative;
}

.chatbot-notification::before {
  content: "ℹ️";
  margin-right: 8px;
}

/* Estilos para la carga de documentos */
.file-upload-container {
  margin: 1rem 0;
  text-align: left;
}

.file-label {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  background: #f0f7ff;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  color: #2a5298;
  transition: background 0.3s;
}

.file-label:hover {
  background: #e0efff;
}

.file-input {
  display: none;
}

.file-name {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #555;
  font-style: italic;
  word-break: break-all;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Mostrar documento adjunto en el detalle del ticket */
.ticket-document {
  margin: 1rem 0;
  padding: 1rem;
  background: #f0f7ff;
  border-radius: 8px;
  border-left: 4px solid #2a5298;
  box-sizing: border-box;
}

.document-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #2a5298;
  text-decoration: none;
  font-weight: 600;
  margin-top: 0.5rem;
  word-break: break-all;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

.document-link:hover {
  text-decoration: underline;
}

/* Buscador */
.search-bar {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.search-bar input {
  width: 60%;
  max-width: 600px;
  padding: 0.9rem;
  border-radius: 10px;
  border: 1px solid #bbb;
  font-size: 1rem;
  text-align: center;
  font-family: 'Open Sans', sans-serif;
  box-sizing: border-box;
}

.main-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 2rem;
  align-items: flex-start;
}

@media (max-width: 900px) {
  .main-grid {
    grid-template-columns: 1fr;
  }

  .search-bar input {
    width: 90%;
  }
}

/* Lista de tickets */
.tickets-list {
  background: #e7f9ff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 80vh;
  overflow-y: auto;
  box-sizing: border-box;
}

.subtitle {
  font-size: 1.5rem;
  color: #2a5298;
  margin: 0 0 1rem 0;
  font-weight: 700;
  text-align: center;
}

.estado-title {
  font-size: 1.2rem;
  color: #1e3c72;
  margin: 1.5rem 0 0.8rem 0;
  font-weight: 600;
  text-align: left;
}

.tickets-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ticket-card {
  background: white;
  padding: 1.2rem;
  border-radius: 12px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  border-left: 6px solid #2a5298;
  transition: transform 0.2s, box-shadow 0.2s;
  text-align: left;
  box-sizing: border-box;
  overflow: hidden;
}

.ticket-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.ticket-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.7rem;
}

.ticket-id {
  font-weight: bold;
  font-size: 1.1rem;
  color: #333;
}

/* Título del ticket en la lista */
.ticket-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: #2a5298;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

/* Descripción del ticket en la lista */
.description {
  margin: 0;
  font-size: 0.9rem;
  color: #555;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  text-overflow: ellipsis;
  max-height: 3.6em;
  line-height: 1.4;
  word-wrap: break-word;
}

.meta {
  font-size: 0.8rem;
  color: #777;
  display: block;
  margin-top: 0.5rem;
}

/* Estados */
.status {
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
  text-transform: uppercase;
  min-width: 100px;
  text-align: center;
  white-space: nowrap;
}

.status.abierto {
  background: #eaf1ff;
  color: #2a5298;
}

.status.progreso {
  background: #fff3cd;
  color: #e6a700;
}

.status.cerrado {
  background: #e6ffe6;
  color: #188038;
}

/* Separador entre grupos de estado */
hr {
  border: none;
  border-top: 1px solid #d0e1f9;
  margin: 1.5rem 0;
}

/* Detalle del caso */
.ticket-detail {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  min-height: 70vh;
  box-sizing: border-box;
  overflow: hidden;
}

.detail-header {
  margin-bottom: 1.5rem;
}

.detail-title {
  font-size: 1.5rem;
  color: #2a5298;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
  text-align: left;
}

.case-title {
  font-size: 1.2rem;
  color: #1e3c72;
  margin: 0;
  font-weight: 600;
  word-wrap: break-word;
  overflow-wrap: break-word;
  text-align: left;
  line-height: 1.4;
}

/* Control de estado */
.estado-control {
  margin: 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.estado-control label {
  font-weight: bold;
  font-size: 0.9rem;
  color: #333;
}

.estado-control select {
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  border: 1.5px solid #ccc;
  font-size: 0.85rem;
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
  background: #fff;
  font-weight: bold;
  text-transform: uppercase;
  min-width: 120px;
  font-family: 'Open Sans', sans-serif;
}

.estado-control select:hover {
  border-color: #2a5298;
  background: #f8faff;
}

/* Lista de actualizaciones */
.updates-list {
  flex: 1;
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-height: 50vh;
  overflow-y: auto;
  box-sizing: border-box;
}

.update-card {
  padding: 1.2rem;
  border-radius: 10px;
  background: #e4fbff;
  max-width: 85%;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  text-align: left;
  align-self: flex-start;
  box-sizing: border-box;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow: visible;
}

.update-card.my-message {
  align-self: flex-end;
  background: #e6f7ff;
  text-align: right;
}

.update-card.my-message small {
  text-align: right;
  display: block;
}

.update-card.internal {
  background: #fff8e1;
}

.update-text {
  margin: 0 0 0.8rem 0;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  word-break: break-word;
  max-width: 100%;
}

.image-container {
  margin: 0.8rem 0;
  text-align: center;
}

.update-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  object-fit: contain;
  cursor: pointer;
  transition: transform 0.3s;
}

.update-image:hover {
  transform: scale(1.02);
}

.tag-internal {
  background: #ff9800;
  color: white;
  font-size: 0.7rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  margin-left: 0.4rem;
}

/* Formulario de actualización */
.update-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.update-form textarea {
  width: 100%;
  padding: 0.9rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  resize: none;
  height: 120px;
  font-size: 1rem;
  font-family: 'Open Sans', sans-serif;
  box-sizing: border-box;
}

.update-form input[type="file"] {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  background: white;
  box-sizing: border-box;
}

.actions {
  margin-top: 0.6rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.internal-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: #2d3b48;
  font-weight: 600;
}

.closed-msg {
  padding: 1rem;
  background: #f1f1f1;
  border-radius: 8px;
  margin-top: 1rem;
  font-style: italic;
  color: #666;
  text-align: center;
}

/* Modal para imágenes */
.image-modal {
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
}

.modal-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
}

.close-modal {
  position: absolute;
  top: -40px;
  right: 0;
  color: white;
  font-size: 30px;
  font-weight: bold;
  cursor: pointer;
}

.modal-image {
  max-width: 100%;
  max-height: 90vh;
  border-radius: 8px;
  object-fit: contain;
}

/* Checkbox personalizado */
.container input {
  display: none;
}

.container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  font-weight: 600;
  color: #2d3b48;
}

.checkmark {
  position: relative;
  height: 1.3em;
  width: 1.7em;
  background-color: transparent;
  border-radius: 0.25em;
  transition: all 0.25s;
  margin-left: 12px;
}

/* borde cuadrado del checkbox */
.checkmark:after {
  content: "";
  position: absolute;
  transform: rotate(0deg);
  border: 0.1em solid #2a5298;
  /* azul a juego con tu diseño */
  left: 0;
  top: 0;
  width: 1.05em;
  height: 1.05em;
  border-radius: 0.25em;
  transition: all 0.25s, border-width 0.1s;
}

/* estado checked */
.container input:checked~.checkmark {
  background-color: #2a5298;
}

.container input:checked~.checkmark:after {
  left: 0.45em;
  top: 0.25em;
  width: 0.25em;
  height: 0.5em;
  border-color: white;
  border-width: 0 0.15em 0.15em 0;
  border-radius: 0em;
  transform: rotate(45deg);
}
</style>