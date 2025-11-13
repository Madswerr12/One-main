<template>
  <div> <!-- 👈 único root -->

    <!-- CONTENEDOR DEL PLAN -->
    <div class="planContainer">
      <div class="plan">
        <div class="titleContainer">
          <div class="title">Pagar Precio Asignado</div>
        </div>

        <div class="infoContainer">
          <p v-if="assignedPrice !== null" class="price">
            ${{ assignedPrice }}
          </p>

          <p v-if="lastReason" class="reason">
            Motivo: {{ lastReason }}
          </p>

          <div id="paypal-button-container" v-show="canPay"></div>

          <p v-if="!canPay" class="noPayMessage">
            {{ noPayMessage }}
          </p>

          <!-- Botón para expandir/collapse -->
          <button class="toggleHistory" @click="showHistory = !showHistory">
            {{ showHistory ? 'Ocultar Historial' : 'Mostrar Historial' }}
          </button>

          <!-- Historial expandible -->
          <transition name="fade">
            <ul v-if="showHistory">
              <li v-for="p in payments" :key="p.id">
                ${{ p.amount }} - {{ p.date.toDate().toLocaleString() }} - {{ p.status }}
              </li>
            </ul>
          </transition>
        </div>
      </div>
    </div>

    <!-- MODAL SEPARADO PERO DENTRO DEL ROOT -->
    <Modal
      v-if="modalActive"
      :modalMessage="modalMessage"
      @close-modal="closeModal"
      class="modalSection"
    />

  </div>
</template>




<script>
import firebase from "firebase/app";
import "firebase/firestore";
import "firebase/auth";
import Modal from "../components/Modal";

export default {
  components: { Modal },
  data() {
    return {
      assignedPrice: null,
      lastReason: "",
      payments: [],
      modalActive: false,
      modalMessage: "",
      exchangeRate: 4000,
      paypalRendered: false,
      showHistory: false
    };
  },
  computed: {
    minCop() {
      return Math.ceil(0.01 * this.exchangeRate);
    },
    canPay() {
      return (
        typeof this.assignedPrice === "number" &&
        this.assignedPrice >= this.minCop
      );
    },
    noPayMessage() {
      if (this.assignedPrice === 0) {
        return "No tienes saldo pendiente por pagar.";
      }
      if (this.assignedPrice < 0) {
        return "El saldo es negativo. Revisa tus movimientos.";
      }
      if (this.assignedPrice > 0 && this.assignedPrice < this.minCop) {
        return `El monto mínimo para pagar por PayPal es ~${this.minCop} COP (equivale a 0.01 USD).`;
      }
      return "";
    }
  },
  methods: {
    async fetchAssignedPrice() {
      const user = firebase.auth().currentUser;
      if (!user) return;

      const doc = await firebase.firestore().collection("users").doc(user.uid).get();
      this.assignedPrice = Number(doc.data()?.assignedPrice || 0);

      // ⚡ Si ya está en 0, quitamos el motivo
      if (this.assignedPrice === 0) {
        this.lastReason = "";
      } else {
        // Traer último motivo del historial solo si hay saldo pendiente
        const historySnap = await firebase.firestore()
          .collection("users")
          .doc(user.uid)
          .collection("priceHistory")
          .orderBy("date", "desc")
          .limit(1)
          .get();

        this.lastReason = historySnap.empty ? "" : historySnap.docs[0].data().reason || "";
      }

      // Traer historial de pagos
      const paymentsSnap = await firebase
        .firestore()
        .collection("users")
        .doc(user.uid)
        .collection("payments")
        .orderBy("date", "desc")
        .get();

      this.payments = paymentsSnap.docs.map(d => ({ id: d.id, ...d.data() }));
    },

    async registerPayment(status, usdValue) {
      const user = firebase.auth().currentUser;
      if (!user || this.assignedPrice === null) return;

      const userRef = firebase.firestore().collection("users").doc(user.uid);

      await userRef.collection("payments").add({
        amount: this.assignedPrice,
        amountUSD: usdValue,
        date: firebase.firestore.Timestamp.now(),
        status
      });

      if (status === "aprobado") {
        await userRef.update({
          assignedPrice: firebase.firestore.FieldValue.increment(-this.assignedPrice)
        });
        this.modalMessage = "✅ Pago registrado correctamente!";
        this.modalActive = true;
      } else if (status === "cancelado") {
        this.modalMessage = "ℹ️ El pago fue cancelado.";
        this.modalActive = true;
      } else if (status === "error") {
        this.modalMessage = "⚠️ Ocurrió un error al procesar el pago.";
        this.modalActive = true;
      }

      await this.fetchAssignedPrice();
      this.cleanupPayPalContainer();
      this.maybeRenderPayPal();
    },

    closeModal() {
      this.modalActive = false;
    },

    usdFromCop(cop) {
      const usd = cop / this.exchangeRate;
      return Number(usd.toFixed(2));
    },

    cleanupPayPalContainer() {
      const el = document.getElementById("paypal-button-container");
      if (el) el.innerHTML = "";
      this.paypalRendered = false;
    },

    renderPayPalButtons() {
      if (!window.paypal || !this.canPay || this.paypalRendered) return;
      this.cleanupPayPalContainer();
      const usdValue = this.usdFromCop(this.assignedPrice);

      window.paypal.Buttons({
        style: { layout: "vertical", color: "gold", shape: "rect", label: "paypal" },
        createOrder: (data, actions) => {
          if (usdValue < 0.01) throw new Error("El monto en USD debe ser al menos 0.01");
          return actions.order.create({
            purchase_units: [{ amount: { currency_code: "USD", value: usdValue.toFixed(2) } }]
          });
        },
        onApprove: async (data, actions) => {
          const details = await actions.order.capture();
          console.log("Detalles del pago:", details);
          await this.registerPayment("aprobado", usdValue);
        },
        onCancel: async () => {
          await this.registerPayment("cancelado", usdValue);
        },
        onError: async (err) => {
          console.error("Error en PayPal:", err);
          if (this.assignedPrice && this.paypalRendered) {
            await this.registerPayment("error", usdValue);
          }
        }
      }).render("#paypal-button-container");

      this.paypalRendered = true;
    },

    async maybeRenderPayPal() {
      await this.$nextTick();
      const tick = () => { if (window.paypal && this.canPay) this.renderPayPalButtons(); };
      tick();
      const id = setInterval(() => {
        if (this.paypalRendered || !this.canPay) return clearInterval(id);
        tick();
        if (this.paypalRendered) clearInterval(id);
      }, 300);
    }
  },

  watch: {
    assignedPrice() {
      if (!this.canPay) {
        this.cleanupPayPalContainer();
      } else {
        this.maybeRenderPayPal();
      }
    }
  },

  async mounted() {
    await this.fetchAssignedPrice();
    this.maybeRenderPayPal();
  }
};
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css?family=Open+Sans:400,600,700,800');

body {
  background-color: #1abc9c;
  font-family: 'Open Sans', sans-serif;
  margin: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px; /* espacio en móviles */
}

.planContainer {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.plan {
  background: white;
  width: clamp(24em, 55vw, 32em); /* más grande que antes */
  box-sizing: border-box;
  text-align: center;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  overflow: hidden;
  margin: 30px 0;
}

.titleContainer {
  background-color: #f3f3f3;
  padding: 1em;
}

.title {
  font-size: clamp(1.4rem, 2.5vw, 2rem); /* más grande */
  text-transform: uppercase;
  color: #1abc9c;
  font-weight: 700;
}

.infoContainer {
  padding: 1.5em; /* un poco más de padding */
  color: #2d3b48;
}

.price {
  font-size: clamp(3rem, 6vw, 5rem); /* más grande y ajustable */
  font-weight: 700;
  color: #2ecc71;
  margin: 20px 0;
}

.reason {
  font-style: italic;
  color: #444;
  margin: 8px 0;
  font-size: clamp(1rem, 2.2vw, 1.4rem);
}

.noPayMessage {
  color: #666;
  margin-top: 12px;
  font-size: clamp(1rem, 2.2vw, 1.4rem);
}

.toggleHistory {
  background: none;
  border: 2px solid #1abc9c;
  border-radius: 6px;
  color: #1abc9c;
  padding: 8px 14px;
  margin: 15px 0;
  cursor: pointer;
  font-size: clamp(1rem, 2.2vw, 1.2rem);
  font-weight: 600;
  transition: 0.3s;
}

.toggleHistory:hover {
  background-color: #1abc9c;
  color: white;
}

ul {
  list-style: none; /* Quita puntos */
  padding: 0;
  margin: 15px 0 0 0;
  font-size: clamp(1rem, 2vw, 1.3rem); /* más grande y legible */
  max-width: 100%; /* que ocupe todo el ancho del cuadro */
}

li {
  margin-bottom: 8px;
  word-break: break-word; /* evita que se salga de la tarjeta */
}

/* transición para expandible */
.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  max-height: 0;
}
.fade-enter-to, .fade-leave-from {
  opacity: 1;
  max-height: 500px; /* ajustable según pagos */
}

.modal-overlay {
  position: fixed;   /* <-- importante, no absolute */
  top: 0;
  left: 0;
  width: 100%;       /* ocupa todo el ancho */
  height: 100%;      /* ocupa todo el alto */
  background: rgba(0, 0, 0, 0.6);  /* semi transparente */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;     /* que quede siempre por encima */
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  z-index: 10000;
}

</style>