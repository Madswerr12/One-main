<template>
  <div class="prices-tab">
    <header class="header">
      <h3>Asignar Estados de Cuenta</h3>
      <div class="header-actions">
        <div class="search-wrap" role="search">
          <input
            v-model.trim="searchTerm"
            type="text"
            class="search-input"
            placeholder="Buscar por nombre, apellido o usuario…"
            aria-label="Buscar personas"
          />
          <button v-if="searchTerm" class="btn ghost" @click="searchTerm = ''" aria-label="Limpiar búsqueda">
            Limpiar
          </button>
        </div>
        <button class="btn primary download-btn" @click="downloadAllUsers">
          <span class="icon"></span> Descargar todos
        </button>
      </div>
    </header>

    <div v-if="filteredUsers.enabled.length === 0 && filteredUsers.disabled.length === 0" class="empty-state">
      <p>No hay resultados para "{{ searchTerm }}".</p>
    </div>

    <!-- Usuarios Habilitados -->
    <div v-if="filteredUsers.enabled.length > 0">
      <h4 class="section-title">Usuarios Habilitados</h4>
      <ul class="users-list">
        <li v-for="u in filteredUsers.enabled" :key="u.id" class="user-card">
          <div class="row between">
            <div class="user-id">
              <div class="name">{{ u.firstName }} {{ u.lastName }}</div>
              <div class="username">@{{ u.username }}</div>
              <div class="username">Apartamento:{{ u.apartment }}</div>
            </div>

            <div class="inputs">
              <label class="field">
                <span class="label">Precio asignado</span>
                <input type="number" v-model.number="u.assignedPrice" class="input" />
              </label>
              <label class="field reason">
                <span class="label">Razón del cambio</span>
                <input type="text" v-model="u.reason" class="input" placeholder="Ej: Ajuste mensual" />
              </label>
              <button class="btn primary" @click="savePrice(u)">Guardar</button>
              <button class="btn ghost download-btn" @click="downloadUser(u)">
                <span class="icon"></span> Descargar
              </button>
            </div>
          </div>

          <div class="history-wrap" v-if="u.history && u.history.length">
            <button class="toggle" :aria-expanded="u._showHistory" @click="u._showHistory = !u._showHistory">
              <span class="chev" :class="{ open: u._showHistory }">▸</span>
              <span class="toggle-text">Historial ({{ u.history.length }})</span>
            </button>

            <transition name="collapse">
              <div v-show="u._showHistory" class="history">
                <ul>
                  <li v-for="(h, idx) in u.history" :key="h.id || idx" class="history-item">
                    <span class="date">{{ formatDate(h.date) }}</span>

                    <template v-if="h.type === 'priceChange'">
                      <span class="pill blue">Cambio</span>
                      <span class="detail">
                        {{ signed(h.diff) }} ({{ h.oldValue }} → {{ h.newValue }})
                        • Razón: <strong>{{ h.reason }}</strong>
                        • Por: {{ h.changedBy }}
                      </span>
                    </template>

                    <template v-else-if="h.type === 'payment'">
                      <span class="pill green">Pago</span>
                      <span class="detail">
                        💰 {{ h.amount }}  • Estado: {{ h.status }} • Por: {{ h.changedBy || h.userName }}
                      </span>
                    </template>
                  </li>
                </ul>
              </div>
            </transition>
          </div>
        </li>
      </ul>
    </div>

    <!-- Usuarios Deshabilitados -->
    <div v-if="filteredUsers.disabled.length > 0">
      <h4 class="section-title disabled-title">Usuarios Deshabilitados</h4>
      <ul class="users-list disabled-list">
        <li v-for="u in filteredUsers.disabled" :key="u.id" class="user-card disabled-card">
          <div class="row between">
            <div class="user-id">
              <div class="name">{{ u.firstName }} {{ u.lastName }}</div>
              <div class="username">@{{ u.username }}</div>
              <div class="username">Apartamento:{{ u.apartment }}</div>
              <div class="disabled-badge">Deshabilitado</div>
            </div>

            <div class="inputs">
              <label class="field">
                <span class="label">Precio asignado</span>
                <input type="number" v-model.number="u.assignedPrice" class="input" disabled />
              </label>
              <label class="field reason">
                <span class="label">Razón del cambio</span>
                <input type="text" v-model="u.reason" class="input" placeholder="Ej: Ajuste mensual" disabled />
              </label>
              <button class="btn primary" disabled>No se puede guardar</button>
              <button class="btn ghost download-btn" @click="downloadUser(u)">
                <span class="icon"></span> Descargar
              </button>
            </div>
          </div>

          <div class="history-wrap" v-if="u.history && u.history.length">
            <button class="toggle" :aria-expanded="u._showHistory" @click="u._showHistory = !u._showHistory">
              <span class="chev" :class="{ open: u._showHistory }">▸</span>
              <span class="toggle-text">Historial ({{ u.history.length }})</span>
            </button>

            <transition name="collapse">
              <div v-show="u._showHistory" class="history">
                <ul>
                  <li v-for="(h, idx) in u.history" :key="h.id || idx" class="history-item">
                    <span class="date">{{ formatDate(h.date) }}</span>

                    <template v-if="h.type === 'priceChange'">
                      <span class="pill blue">Cambio</span>
                      <span class="detail">
                        {{ signed(h.diff) }} ({{ h.oldValue }} → {{ h.newValue }})
                        • Razón: <strong>{{ h.reason }}</strong>
                        • Por: {{ h.changedBy }}
                      </span>
                    </template>

                    <template v-else-if="h.type === 'payment'">
                      <span class="pill green">Pago</span>
                      <span class="detail">
                        💰 {{ h.amount }}  • Estado: {{ h.status }} • Por: {{ h.changedBy || h.userName }}
                      </span>
                    </template>
                  </li>
                </ul>
              </div>
            </transition>
          </div>
        </li>
      </ul>
    </div>

    <Modal v-if="modalActive" :modalMessage="modalMessage" @close-modal="closeModal" />
  </div>
</template>

<script>
import firebase from "firebase/app";
import "firebase/firestore";
import Modal from "../components/Modal";
import * as XLSX from 'xlsx'; // Importamos la librería XLSX

export default {
  name: "PricesTab",
  components: { Modal },
  data() {
    return {
      users: [],
      modalActive: false,
      modalMessage: "Precio guardado!",
      searchTerm: "",
    };
  },
  computed: {
    filteredUsers() {
      const q = this.searchTerm.toLowerCase();
      let enabledUsers = this.users.filter(u => !u.disabled);
      let disabledUsers = this.users.filter(u => u.disabled);

      if (q) {
        enabledUsers = enabledUsers.filter((u) => {
          const name = `${u.firstName || ""} ${u.lastName || ""}`.toLowerCase();
          const username = (u.username || "").toLowerCase();
          const apartment = (u.apartment || "").toString().toLowerCase();
          return (
            name.includes(q) ||
            username.includes(q) ||
            apartment.includes(q)
          );
        });

        disabledUsers = disabledUsers.filter((u) => {
          const name = `${u.firstName || ""} ${u.lastName || ""}`.toLowerCase();
          const username = (u.username || "").toLowerCase();
          const apartment = (u.apartment || "").toString().toLowerCase();
          return (
            name.includes(q) ||
            username.includes(q) ||
            apartment.includes(q)
          );
        });
      }

      return { enabled: enabledUsers, disabled: disabledUsers };
    },
  },
  methods: {
    signed(n) {
      if (typeof n !== "number") return n;
      return n > 0 ? `+${n}` : `${n}`;
    },
    formatDate(ts) {
      try {
        const d = ts?.toDate ? ts.toDate() : ts instanceof Date ? ts : null;
        return d ? d.toLocaleString() : "(sin fecha)";
      } catch (e) {
        return "(sin fecha)";
      }
    },

    async fetchUsers() {
      const query = await firebase.firestore().collection("users").where("role", "==", "user").get();

      this.users = await Promise.all(
        query.docs.map(async (doc) => {
          const userData = doc.data();
          const user = { 
            id: doc.id, 
            ...userData, 
            reason: "", 
            _showHistory: false,
            disabled: userData.disabled || false // Aseguramos que exista la propiedad
          };

          // Historial de cambios de precio
          const priceHistorySnap = await firebase
            .firestore()
            .collection("users")
            .doc(user.id)
            .collection("priceHistory")
            .orderBy("date", "desc")
            .get();

          const priceHistory = priceHistorySnap.docs.map((d) => ({ id: d.id, type: "priceChange", ...d.data() }));

          // Sólo pagos aprobados
          const paymentsSnap = await firebase
            .firestore()
            .collection("users")
            .doc(user.id)
            .collection("payments")
            .where("status", "==", "aprobado")
            .orderBy("date", "desc")
            .get();

          const payments = paymentsSnap.docs.map((d) => ({ id: d.id, type: "payment", userName: `${user.firstName} ${user.lastName}`.trim(), ...d.data() }));

          const history = [...priceHistory, ...payments].sort((a, b) => (a?.date?.seconds || 0) < (b?.date?.seconds || 0) ? 1 : -1);

          return { ...user, history };
        })
      );
    },

    async savePrice(user) {
      // Verificar si el usuario está deshabilitado
      if (user.disabled) {
        alert("No se puede asignar precios a usuarios deshabilitados");
        return;
      }
      
      if (!user.reason) {
        alert("Debes ingresar una razón para el cambio");
        return;
      }

      try {
        const userRef = firebase.firestore().collection("users").doc(user.id);

        // Valor actual antes de actualizar
        const userSnap = await userRef.get();
        const oldValue = userSnap.data().assignedPrice || 0;
        const newValue = user.assignedPrice;

        if (oldValue === newValue) {
          alert("El precio no cambió");
          return;
        }

        await userRef.update({ assignedPrice: newValue });

        await userRef.collection("priceHistory").add({
          oldValue,
          newValue,
          diff: newValue - oldValue,
          reason: user.reason,
          changedBy: firebase.auth().currentUser?.email || "admin",
          date: firebase.firestore.Timestamp.now(),
        });

        user.reason = "";
        this.modalMessage  = "Precio guardado!";
        this.modalActive = true;
        await this.fetchUsers();
      } catch (err) {
        console.error("Error guardando precio:", err);
        alert("Ocurrió un error guardando el precio");
      }
    },

    closeModal() {
      this.modalActive = false;
    },

    // Método para descargar datos de un usuario específico
    downloadUser(user) {
      // Preparamos los datos del usuario
      const userData = [{
        'ID': user.id,
        'Nombre': user.firstName,
        'Apellido': user.lastName,
        'Usuario': user.username,
        'Apartamento': user.apartment,
        'Precio Asignado': user.assignedPrice,
        'Estado': user.disabled ? 'Deshabilitado' : 'Habilitado'
      }];

      // Preparamos los datos del historial
      const historyData = user.history.map(h => {
        const item = {
          'Fecha': this.formatDate(h.date),
          'Tipo': h.type === 'priceChange' ? 'Cambio de Precio' : 'Pago',
          'Realizado por': h.changedBy || (h.type === 'payment' ? h.userName : '')
        };

        if (h.type === 'priceChange') {
          item['Valor Anterior'] = h.oldValue;
          item['Valor Nuevo'] = h.newValue;
          item['Diferencia'] = h.diff;
          item['Razón'] = h.reason;
        } else if (h.type === 'payment') {
          item['Monto'] = h.amount;
          item['Estado'] = h.status;
        }

        return item;
      });

      // Creamos el libro de Excel
      const wb = XLSX.utils.book_new();
      
      // Hoja con datos del usuario
      const userSheet = XLSX.utils.json_to_sheet(userData);
      XLSX.utils.book_append_sheet(wb, userSheet, "Datos del Usuario");
      
      // Hoja con historial
      const historySheet = XLSX.utils.json_to_sheet(historyData);
      XLSX.utils.book_append_sheet(wb, historySheet, "Historial");

      // Descargamos el archivo
      const fileName = `usuario_${user.username}_${new Date().toISOString().slice(0, 10)}.xlsx`;
      XLSX.writeFile(wb, fileName);
    },

    // Método para descargar todos los usuarios
    downloadAllUsers() {
      // Preparamos los datos de todos los usuarios
      const allUsersData = this.users.map(u => ({
        'ID': u.id,
        'Nombre': u.firstName,
        'Apellido': u.lastName,
        'Usuario': u.username,
        'Apartamento': u.apartment,
        'Precio Asignado': u.assignedPrice,
        'Estado': u.disabled ? 'Deshabilitado' : 'Habilitado'
      }));

      // Creamos el libro de Excel
      const wb = XLSX.utils.book_new();
      
      // Hoja con todos los usuarios
      const usersSheet = XLSX.utils.json_to_sheet(allUsersData);
      XLSX.utils.book_append_sheet(wb, usersSheet, "Todos los Usuarios");

      // Descargamos el archivo
      const fileName = `todos_usuarios_${new Date().toISOString().slice(0, 10)}.xlsx`;
      XLSX.writeFile(wb, fileName);
    }
  },
  mounted() {
    this.fetchUsers();
  },
};
</script>

<style scoped>
/* Layout base */
.prices-tab {
  --bg: #0f172a;         /* slate-900 */
  --card: #111827;       /* gray-900 */
  --muted: #94a3b8;      /* slate-400 */
  --text: #e5e7eb;       /* gray-200 */
  --primary: #22d3ee;    /* cyan-400 */
  --primary-700: #0e7490;/* cyan-700 */
  --ring: rgba(34, 211, 238, 0.35);
  --green: #34d399;      /* emerald-400 */
  --blue: #60a5fa;       /* blue-400 */
  --disabled: #4b5563;   /* gray-600 */

  min-height: 100%;
  background: radial-gradient(1200px 800px at 10% -10%, rgba(34,211,238,0.12), transparent),
              radial-gradient(1200px 800px at 110% 10%, rgba(96,165,250,0.10), transparent),
              var(--bg);
  color: var(--text);
  padding: 24px;
}

.header {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}
.header h3 {
  font-size: 1.375rem;
  font-weight: 700;
  letter-spacing: 0.2px;
}
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.search-wrap {
  flex: 1;
  min-width: 250px;
  display: flex;
  gap: 8px;
  align-items: center;
}
.search-input {
  flex: 1;
  background: var(--card);
  border: 1px solid rgba(148,163,184,0.25);
  border-radius: 14px;
  padding: 10px 14px;
  color: var(--text);
  outline: none;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.search-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px var(--ring);
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 20px 0 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid rgba(148,163,184,0.25);
}

.disabled-title {
  color: var(--disabled);
  border-bottom-color: var(--disabled);
}

.users-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  list-style: none;
  padding: 0;
  margin: 0;
}

.disabled-list {
  opacity: 0.85;
}

.user-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.0));
  border: 1px solid rgba(148,163,184,0.18);
  border-radius: 18px;
  padding: 16px;
  box-shadow: 0 10px 20px rgba(2,8,23,0.35);
}

.disabled-card {
  border-color: var(--disabled);
  background: linear-gradient(180deg, rgba(75,85,99,0.1), rgba(75,85,99,0.05));
}

.row.between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.user-id .name {
  font-weight: 700;
  font-size: 1.05rem;
}
.user-id .username {
  font-size: 0.9rem;
  color: var(--muted);
}

.disabled-badge {
  display: inline-block;
  background-color: var(--disabled);
  color: #1f2937;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  margin-top: 5px;
}

.inputs {
  display: grid;
  grid-template-columns: repeat(4, minmax(120px, 1fr));
  gap: 10px;
  align-items: end;
  width: 100%;
}

.field {
  display: grid;
  gap: 6px;
}
.label {
  font-size: 0.78rem;
  color: var(--muted);
}
.input {
  background: var(--card);
  border: 1px solid rgba(148,163,184,0.25);
  border-radius: 12px;
  padding: 10px 12px;
  color: var(--text);
  outline: none;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px var(--ring);
}
.input:disabled {
  background-color: rgba(75,85,99,0.3);
  color: var(--disabled);
  cursor: not-allowed;
}

.reason { grid-column: span 1; }

@media (max-width: 960px) {
  .inputs { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 640px) {
  .inputs { grid-template-columns: 1fr; }
}

.btn {
  border: 1px solid rgba(148,163,184,0.25);
  background: var(--card);
  color: var(--text);
  padding: 10px 14px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.05s ease, box-shadow 0.2s, border-color 0.2s, background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.btn:hover { border-color: var(--primary); box-shadow: 0 8px 20px rgba(2,8,23,0.35); }
.btn:active { transform: translateY(1px); }
.btn:disabled {
  background-color: rgba(75,85,99,0.3);
  color: var(--disabled);
  cursor: not-allowed;
  border-color: var(--disabled);
}
.btn:disabled:hover {
  box-shadow: none;
  transform: none;
}

.btn.primary {
  background: linear-gradient(180deg, var(--primary), rgba(34,211,238,0.85));
  color: #05202a;
  border: none;
}
.btn.primary:disabled {
  background: linear-gradient(180deg, var(--disabled), rgba(75,85,99,0.85));
  color: #1f2937;
}

.btn.ghost { background: transparent; }

.download-btn {
  font-size: 0.9rem;
}
.download-btn .icon {
  font-size: 1.1rem;
}

.history-wrap { margin-top: 12px; }
.toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: transparent;
  border: 1px dashed rgba(148,163,184,0.35);
  border-radius: 10px;
  color: var(--text);
  cursor: pointer;
}
.chev { display: inline-block; transition: transform 0.2s ease; }
.chev.open { transform: rotate(90deg); }
.toggle-text { font-weight: 600; }

.history {
  margin-top: 10px;
  padding: 12px;
  background: rgba(17,24,39,0.6);
  border: 1px solid rgba(148,163,184,0.18);
  border-radius: 14px;
}
.history ul { list-style: none; padding: 0; margin: 0; }
.history-item {
  display: grid;
  grid-template-columns: 160px auto;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px dashed rgba(148,163,184,0.18);
}
.history-item:last-child { border-bottom: 0; }
.date { color: var(--muted); font-size: 0.86rem; }
.detail { font-size: 0.95rem; }

.pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  margin-right: 8px;
  border: 1px solid rgba(148,163,184,0.25);
}
.pill.green { background: rgba(52, 211, 153, 0.15); color: #bbf7d0; border-color: rgba(52,211,153,0.35); }
.pill.blue  { background: rgba(96, 165, 250, 0.15); color: #bfdbfe; border-color: rgba(96,165,250,0.35); }

/* Animación de colapso */
.collapse-enter-active, .collapse-leave-active { transition: height 0.22s ease, opacity 0.22s ease; }
.collapse-enter-from, .collapse-leave-to { height: 0; opacity: 0; overflow: hidden; }

.empty-state { color: var(--muted); margin-top: 10px; }
</style>