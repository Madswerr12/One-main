<template>
  <div class="chatbot-container">
    <VueBotUI :messages="data" :options="botOptions" :input-disable="isWaitingResponse"
      @msg-send="messageSendHandler" />

    <!-- Modal para crear ticket -->
    <div v-if="showTicketModal" class="ticket-modal">
      <div class="modal-content">
        <h3>¿Esta respuesta te fue útil?</h3>
        <p>{{ currentAnswer }}</p>
        <div class="modal-buttons">
          <button @click="answerIsHelpful" class="modal-btn primary">
            Sí, es lo que buscaba
          </button>
          <button @click="answerIsNotHelpful" class="modal-btn secondary">
            No, crear caso
          </button>
          <button @click="continueConversation" class="modal-btn primary">
            Continuar conversando
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { VueBotUI } from 'vue-bot-ui';
import botAvatar from '../assets/blogPhotos/1.jpg';
import firebase from "firebase/app";
import "firebase/auth";

export default {
  components: { VueBotUI },
  data() {
    return {
      data: [
        {
          agent: 'bot',
          type: 'text',
          text: 'Hola, soy tu asistente virtual. ¿En qué puedo ayudarte hoy?',
        },
      ],
      botOptions: {
        botTitle: 'Chatbot',
        colorScheme: '#1b53d0',
        inputPlaceholder: 'Escribe un mensaje...',
        avatar: botAvatar,
        position: 'right',
      },
      isWaitingResponse: false,
      showTicketModal: false,
      lastQuestion: '',
      currentAnswer: '',
      lastResponse: null,
    };
  },
  methods: {
    async messageSendHandler(value) {
      const userMessage = value.text;
      this.lastQuestion = userMessage;
      this.isWaitingResponse = true;

      this.data.push({
        agent: 'user',
        type: 'text',
        text: userMessage,
      });

      const caseKeywords = ["crear caso", "generar ticket", "hacer ticket", "abrir caso", "nuevo caso"];
      const wantsToCreateCase = caseKeywords.some(keyword =>
        userMessage.toLowerCase().includes(keyword)
      );

      if (wantsToCreateCase) {
        this.createTicketFromQuestion(userMessage);
        this.isWaitingResponse = false;
        return;
      }

      const loadingMessage = {
        agent: 'bot',
        type: 'text',
        text: 'Cargando',
        loading: true,
      };
      this.data.push(loadingMessage);

      const interval = setInterval(() => {
        if (!loadingMessage.loading) {
          clearInterval(interval);
        } else {
          loadingMessage.text += '.';
          if (loadingMessage.text.length > 10) loadingMessage.text = 'Cargando';
        }
      }, 500);

      await this.botResponse(userMessage, loadingMessage);
    },

    async botResponse(userMessage, loadingMessage) {
      try {
        const response = await fetch('http://127.0.0.1:5000/ask', { 
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: userMessage }),
        });

        const data = await response.json();
        this.lastResponse = data;

        let cleanAnswer = this.cleanResponse(data.answer || 'Lo siento, no tengo una respuesta para eso.');

        Object.assign(loadingMessage, {
          text: cleanAnswer,
          loading: false,
        });

        this.currentAnswer = cleanAnswer;

        if (data.basic_greeting) {
          return;
        }

        // Mostrar modal si se sugiere crear ticket o se pide confirmación
        if (data.suggest_ticket || data.ask_confirmation) {
          this.showTicketModal = true;
        } else if (data.create_ticket) {
          this.createTicketFromQuestion(userMessage);
        }
      } catch (error) {
        console.error('Error al obtener la respuesta del bot:', error);
        Object.assign(loadingMessage, {
          text: 'Lo siento, ocurrió un error al procesar tu pregunta.',
          loading: false,
        });
      } finally {
        this.isWaitingResponse = false;
      }
    },

    cleanResponse(response) {
      const unwantedPhrases = [
        "Según los documentos proporcionados, ",
        "Según los documentos, ",
        "Basado en los documentos proporcionados, ",
        "Basado en los documentos, ",
        "De acuerdo con los documentos proporcionados, ",
        "De acuerdo con los documentos, ",
        "Según la información proporcionada, ",
        "Basado en la información proporcionada, ",
        "En los documentos proporcionados, ",
        "En los documentos, ",
        "La información proporcionada indica que, ",
        "Los documentos mencionan que, "
      ];

      let cleanResponse = response;
      for (const phrase of unwantedPhrases) {
        cleanResponse = cleanResponse.replace(phrase, "");
      }

      return cleanResponse.trim();
    },

    answerIsHelpful() {
      this.closeTicketModal();
      this.data.push({
        agent: 'bot',
        type: 'text',
        text: '¡Me alegra haber sido de ayuda! Si necesitas algo más, estoy aquí para asistirte.'
      });
    },

    continueConversation() {
      this.closeTicketModal();
    },
    
    answerIsNotHelpful() {
      this.closeTicketModal();
      this.createTicketFromQuestion(this.lastQuestion);
    },

    createTicketFromQuestion(question) {
      const user = firebase.auth().currentUser;
      if (!user) {
        this.data.push({
          agent: 'bot',
          type: 'text',
          text: 'Debes iniciar sesión para crear un caso. Por favor, inicia sesión e intenta nuevamente.'
        });
        return;
      }

      this.data.push({
        agent: 'bot',
        type: 'text',
        text: 'Redirigiendo a la creación de casos...'
      });

      setTimeout(() => {
        this.$router.push({
          name: 'Tickets',
          query: {
            question: question,
            fromChat: true
          }
        });
      }, 1000);
    },

    closeTicketModal() {
      this.showTicketModal = false;
    }
  },
};
</script>

<style lang="scss">
@import url("https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap");

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Quicksand", sans-serif;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.container {
  max-width: 1440px;
  margin: 0 auto;
}

.link {
  cursor: pointer;
  text-decoration: none;
  text-transform: uppercase;
  color: black;
}

.link-light {
  color: #fff;
}

.arrow {
  margin-left: 8px;
  width: 12px;
  path {
    fill: #000;
  }
}
.arrow-light {
  path {
    fill: #fff;
  }
}

button,
.router-button {
  transition: 500ms ease all;
  cursor: pointer;
  margin-top: 24px;
  padding: 12px 24px;
  background-color: #16baf4;
  color: #fff;
  border-radius: 20px;
  border: none;
  text-transform: uppercase;

  &:focus {
    outline: none;
  }

  &:hover {
    background-color: rgba(48, 48, 48, 0.7);
  }
}

.button-ghost {
  color: #000;
  padding: 0;
  border-radius: 0;
  margin-top: 50px;
  font-size: 15px;
  font-weight: 500;
  background-color: transparent;
  @media (min-width: 700px) {
    margin-top: 0;
    margin-left: auto;
  }

  i {
    margin-left: 8px;
  }
}

.button-light {
  background-color: transparent;
  border: 2px solid #fff;
  color: #fff;
}

.button-inactive {
  pointer-events: none !important;
  cursor: none !important;
  background-color: rgba(128, 128, 128, 0.5) !important;
}

.blog-card-wrap {
  position: relative;
  padding: 80px 16px;
  background-color: #f1f1f1;
  @media (min-width: 500px) {
    padding: 100px 16px;
  }

  .blog-cards {
    display: grid;
    gap: 32px;
    grid-template-columns: 1fr;

    @media (min-width: 500px) {
      grid-template-columns: repeat(2, 1fr);
    }
    @media (min-width: 900px) {
      grid-template-columns: repeat(3, 1fr);
    }
    @media (min-width: 1200px) {
      grid-template-columns: repeat(4, 1fr);
    }
  }
}

/* Estilos para el chatbot existente (VueBotUI) - Ollama */
.qkb-bubble-btn {
  width: 50px !important;
  height: 50px !important;
  background-color: #1b53d0 !important;
  border-radius: 50% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  position: fixed !important;
  bottom: 29px !important;
  right: 100px !important;
  z-index: 1001 !important;
}

.qkb-bubble-btn img {
  width: 30px !important;
  height: 30px !important;
}

.qkb-action-item.qkb-action-item--send {
  margin-top: 0 !important;
}

/* Contenedor del chatbot de Ollama cuando está abierto */
.qkb-board {
  position: fixed !important;
  bottom: 100px !important;
  right: 100px !important;
  width: 350px !important;
  max-height: 70vh !important;
  z-index: 1000 !important;
}

/* Estilos para el chatbot de Botpress */
#bp-web-widget {
  position: fixed !important;
  bottom: 40px !important;
  left: 100px !important;
  right: auto !important;
  z-index: 999 !important;
}

/* Ajustes para el contenedor del chatbot de Botpress */
#bp-web-widget-container {
  position: fixed !important;
  bottom: 40px !important;
  left: 100px !important;
  right: auto !important;
  z-index: 999 !important;
  max-height: 70vh !important;
  width: 350px !important;
}

/* Asegurar que el chatbot de Ollama esté siempre visible */
.qkb-board.bubble-active {
  z-index: 1001 !important;
}

/* Ajustes para pantallas más pequeñas */
@media (max-width: 768px) {
  .qkb-bubble-btn {
    right: 90px !important;
    bottom: 28px !important;
  }
  
  .qkb-board {
    right: 20px !important;
    bottom: 80px !important;
    width: 90% !important;
    max-width: 350px !important;
  }
  
  #bp-web-widget,
  #bp-web-widget-container {
    left: 20px !important;
    bottom: 20px !important;
    width: 90% !important;
    max-width: 350px !important;
  }
}

/* Estilos para el modal del ticket */
.ticket-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  gap: 10px;
}

.modal-btn {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  flex: 1;
  
  &.primary {
    background-color: #1b53d0;
    color: white;
    
    &:hover {
      background-color: #0d3d8f;
    }
  }
  
  &.secondary {
    background-color: #f1f1f1;
    color: #333;
    
    &:hover {
      background-color: #e1e1e1;
    }
  }
}
</style>