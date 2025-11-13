<template>
  <div class="form-wrap">
    <div class="register-container">
      <!-- Formulario de creación -->
      <form class="register">
        <h2>Crear usuario</h2>
        <div class="inputs">
          <div class="input">
            <input type="text" placeholder="Primer nombre" v-model="firstName" />
            <user class="icon" />
          </div>
          <div class="input">
            <input type="text" placeholder="Apellidos" v-model="lastName" />
            <user class="icon" />
          </div>
          <div class="input">
            <input 
              type="text" 
              placeholder="Username" 
              v-model="username"
              :class="{ invalid: !isUsernameAvailable && username }"
            />
            <user class="icon" />
            <div v-if="!isUsernameAvailable && username" class="error-message">
              {{ usernameError }}
            </div>
          </div>
          <div class="input">
            <input 
              type="text" 
              placeholder="Email" 
              v-model="email"
              :class="{ invalid: !isEmailAvailable && email }"
            />
            <email class="icon" />
            <div v-if="!isEmailAvailable && email" class="error-message">
              {{ emailError }}
            </div>
          </div>
          <div class="input">
            <input 
              type="password" 
              placeholder="Contraseña temporal" 
              v-model="password" 
              @input="validatePassword"
            />
            <password class="icon" />
          </div>
          <!-- Indicadores de validación de contraseña -->
          <div class="password-requirements" v-if="password">
            <div class="requirement" :class="{ valid: hasNumber }">
              <span class="requirement-icon">{{ hasNumber ? '✓' : '✗' }}</span>
              Contiene al menos un número
            </div>
            <div class="requirement" :class="{ valid: hasLowercase }">
              <span class="requirement-icon">{{ hasLowercase ? '✓' : '✗' }}</span>
              Contiene al menos una letra minúscula
            </div>
            <div class="requirement" :class="{ valid: hasUppercase }">
              <span class="requirement-icon">{{ hasUppercase ? '✓' : '✗' }}</span>
              Contiene al menos una letra mayúscula
            </div>
            <div class="requirement" :class="{ valid: hasSpecialChar }">
              <span class="requirement-icon">{{ hasSpecialChar ? '✓' : '✗' }}</span>
              Contiene al menos un carácter especial
            </div>
          </div>
          <div class="input">
            <input type="text" placeholder="Apartamento" v-model="apartment" />
            <user class="icon" />
          </div>
          <div class="input">
            <select v-model="role" class="role-select">
              <option value="user">Usuario</option>
              <option value="admin">Admin</option>
              <option value="nomina">Contabilidad</option>
              <option value="Casos">Casos</option>
            </select>
          </div>
        </div>
        <button @click.prevent="openModal" :disabled="!isFormValid">Crear</button>
        <div v-show="error" class="error">{{ errorMsg }}</div>
      </form>

      <!-- Campo de búsqueda -->
      <div class="search-container">
        <input 
          type="text" 
          v-model="searchTerm" 
          placeholder="Buscar usuarios..." 
          class="search-input"
        />
      </div>

      <!-- Lista de usuarios activos -->
      <div class="users-list active-users">
        <h3>Usuarios Activos</h3>
        <div class="users-list-container">
          <ul v-if="filteredActiveUsers.length > 0">
            <li v-for="user in filteredActiveUsers" :key="user.id" class="user-item">
              <div class="user-info">
                <div class="user-name">{{ user.firstName }} {{ user.lastName }}</div>
                <div class="user-details">
                  <div>{{ user.email }}</div>
                  <div>Usuario: {{ user.username }} | Apartamento: {{ user.apartment }}</div>
                  <div class="user-status">
                    <span class="role-badge" :class="user.role">{{ getRoleLabel(user.role) }}</span>
                    <span class="status-badge active">Activo</span>
                  </div>
                </div>
              </div>
              
              <div class="user-actions">
                <button class="btn-small" @click="editUser(user)">Editar</button>
                <button class="btn-small reset" @click="sendReset(user.email)">Reset</button>
                <button class="btn-small disable" @click="toggleUserStatus(user)">
                  Deshabilitar
                </button>
              </div>
            </li>
          </ul>
          <div v-else class="no-users">No hay usuarios activos que coincidan con la búsqueda</div>
        </div>
      </div>

      <!-- Lista de usuarios deshabilitados -->
      <div class="users-list disabled-users">
        <h3>Usuarios Deshabilitados</h3>
        <div class="users-list-container">
          <ul v-if="filteredDisabledUsers.length > 0">
            <li v-for="user in filteredDisabledUsers" :key="user.id" class="user-item">
              <div class="user-info">
                <div class="user-name">{{ user.firstName }} {{ user.lastName }}</div>
                <div class="user-details">
                  <div>{{ user.email }}</div>
                  <div>Usuario: {{ user.username }} | Apartamento: {{ user.apartment }}</div>
                  <div class="user-status">
                    <span class="role-badge" :class="user.role">{{ getRoleLabel(user.role) }}</span>
                    <span class="status-badge disabled">Deshabilitado</span>
                  </div>
                </div>
              </div>
              
              <div class="user-actions">
                <button class="btn-small enable" @click="toggleUserStatus(user)">
                  Habilitar
                </button>
              </div>
            </li>
          </ul>
          <div v-else class="no-users">No hay usuarios deshabilitados que coincidan con la búsqueda</div>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación para crear usuario -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal">
        <h3>Confirmar acción</h3>
        <p>Ingrese su contraseña de administrador:</p>
        <input class="admin-input" type="password" v-model="adminPass" placeholder="Contraseña admin" />
        <div class="modal-actions">
          <button class="button" @click="confirmCreate">Confirmar</button>
          <button class="button" @click="closeModal">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- Modal para editar usuario -->
    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal edit-modal">
        <h3>Editar Usuario</h3>
        <div class="edit-form">
          <div class="input">
            <input type="text" class="admin-input" placeholder="Apartamento" v-model="editingUser.apartment" />
           
          </div>
          <div class="input">
            <select class="role-select" v-model="editingUser.role">
              <option value="user">Usuario normal</option>
              <option value="admin">Admin</option>
              <option value="nomina">Contabilidad</option>
              <option value="Casos">Casos</option>
            </select>
          </div>
        </div>
        <div class="modal-actions">
          <button class="button" @click="saveUserEdit">Guardar</button>
          <button class="button" @click="closeEditModal">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import email from "../assets/Icons/envelope-regular.svg";
import password from "../assets/Icons/lock-alt-solid.svg";
import user from "../assets/Icons/user-alt-light.svg";
import firebase from "firebase/app";
import "firebase/auth";
import db from "../firebase/firebaseInit";

export default {
  name: "RegisterAdmin",
  components: { email, password, user },
  data() {
    return {
      firstName: "",
      lastName: "",
      username: "",
      email: "",
      password: "",
      apartment: "",
      role: "user",
      error: null,
      errorMsg: "",
      activeUsers: [],
      disabledUsers: [],
      adminEmail: "",
      adminPass: "",
      showModal: false,
      showEditModal: false,
      editingUser: {},
      searchTerm: "",
      hasNumber: false,
      hasLowercase: false,
      hasUppercase: false,
      hasSpecialChar: false,
      isPasswordValid: false,
      // Nuevas variables para validación
      isUsernameAvailable: true,
      isEmailAvailable: true,
      usernameError: "",
      emailError: "",
    };
  },
  computed: {
    filteredActiveUsers() {
      if (!this.searchTerm) return this.activeUsers;
      
      const term = this.searchTerm.toLowerCase();
      return this.activeUsers.filter(user => 
        user.firstName.toLowerCase().includes(term) || 
        user.lastName.toLowerCase().includes(term) || 
        user.username.toLowerCase().includes(term) || 
        user.email.toLowerCase().includes(term) ||
        user.apartment.toLowerCase().includes(term)
      );
    },
    filteredDisabledUsers() {
      if (!this.searchTerm) return this.disabledUsers;
      
      const term = this.searchTerm.toLowerCase();
      return this.disabledUsers.filter(user => 
        user.firstName.toLowerCase().includes(term) || 
        user.lastName.toLowerCase().includes(term) || 
        user.username.toLowerCase().includes(term) || 
        user.email.toLowerCase().includes(term) ||
        user.apartment.toLowerCase().includes(term)
      );
    },
    // Nueva computed para verificar si el formulario es válido
    isFormValid() {
      return this.firstName && 
             this.lastName && 
             this.username && 
             this.email && 
             this.password && 
             this.apartment && 
             this.isPasswordValid && 
             this.isUsernameAvailable && 
             this.isEmailAvailable;
    }
  },
  watch: {
    // Observadores para verificar disponibilidad de username y email
    async username(newUsername) {
      if (newUsername) {
        const isAvailable = await this.checkUsernameAvailability(newUsername);
        this.isUsernameAvailable = isAvailable;
        this.usernameError = isAvailable ? "" : "Este nombre de usuario ya está en uso";
      } else {
        this.isUsernameAvailable = true;
        this.usernameError = "";
      }
    },
    async email(newEmail) {
      if (newEmail) {
        const isAvailable = await this.checkEmailAvailability(newEmail);
        this.isEmailAvailable = isAvailable;
        this.emailError = isAvailable ? "" : "Este correo electrónico ya está en uso";
      } else {
        this.isEmailAvailable = true;
        this.emailError = "";
      }
    }
  },
  methods: {
    validatePassword() {
      this.hasNumber = /\d/.test(this.password);
      this.hasLowercase = /[a-z]/.test(this.password);
      this.hasUppercase = /[A-Z]/.test(this.password);
      this.hasSpecialChar = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(this.password);
      this.isPasswordValid = this.hasNumber && this.hasLowercase && this.hasUppercase && this.hasSpecialChar;
    },
    // Nuevo método para verificar disponibilidad de username
    async checkUsernameAvailability(username) {
      try {
        const snapshot = await db.collection("users").where("username", "==", username).get();
        return snapshot.empty;
      } catch (error) {
        console.error("Error checking username availability:", error);
        return false;
      }
    },
    // Nuevo método para verificar disponibilidad de email
    async checkEmailAvailability(email) {
      try {
        const snapshot = await db.collection("users").where("email", "==", email).get();
        return snapshot.empty;
      } catch (error) {
        console.error("Error checking email availability:", error);
        return false;
      }
    },
    openModal() {
      if (!this.isFormValid) {
        this.error = true;
        this.errorMsg = "Por favor, complete todos los campos correctamente.";
        return;
      }
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.adminPass = "";
    },
    async confirmCreate() {
      if (!this.adminPass) {
        alert("Debes ingresar tu contraseña de administrador");
        return;
      }
      
      // Verificación final antes de crear
      const usernameAvailable = await this.checkUsernameAvailability(this.username);
      const emailAvailable = await this.checkEmailAvailability(this.email);
      
      if (!usernameAvailable || !emailAvailable) {
        this.error = true;
        this.errorMsg = !usernameAvailable 
          ? "El nombre de usuario ya está en uso." 
          : "El correo electrónico ya está en uso.";
        this.showModal = false;
        this.adminPass = "";
        return;
      }
      
      this.showModal = false;
      await this.createUser();
    },
    async createUser() {
      try {
        this.error = false;
        this.errorMsg = "";

        const currentUser = firebase.auth().currentUser;
        this.adminEmail = currentUser.email;

        const credential = firebase.auth.EmailAuthProvider.credential(
          this.adminEmail,
          this.adminPass
        );
        await currentUser.reauthenticateWithCredential(credential);

        const createUser = await firebase
          .auth()
          .createUserWithEmailAndPassword(this.email, this.password);

        const result = await createUser;
        const dataBase = db.collection("users").doc(result.user.uid);

        await dataBase.set({
          firstName: this.firstName,
          lastName: this.lastName,
          username: this.username,
          email: this.email,
          apartment: this.apartment,
          role: this.role,
          disabled: false,
        });

        await firebase.auth().signInWithEmailAndPassword(this.adminEmail, this.adminPass);
        this.loadUsers();

        // Limpiar formulario
        this.firstName = "";
        this.lastName = "";
        this.username = "";
        this.email = "";
        this.password = "";
        this.apartment = "";
        this.role = "user";
        this.adminPass = "";
        
        // Reiniciar validaciones
        this.hasNumber = false;
        this.hasLowercase = false;
        this.hasUppercase = false;
        this.hasSpecialChar = false;
        this.isPasswordValid = false;
        this.isUsernameAvailable = true;
        this.isEmailAvailable = true;
        this.usernameError = "";
        this.emailError = "";
      } catch (err) {
        this.error = true;
        this.errorMsg = err.message;
      }
    },
    async loadUsers() {
      const snapshot = await db.collection("users").get();
      const allUsers = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      
      this.activeUsers = allUsers.filter(user => !user.disabled);
      this.disabledUsers = allUsers.filter(user => user.disabled);
    },
    async sendReset(email) {
      try {
        await firebase.auth().sendPasswordResetEmail(email);
        alert(`Correo de reset enviado a ${email}`);
      } catch (err) {
        alert("Error: " + err.message);
      }
    },
    editUser(user) {
      this.editingUser = { ...user };
      this.showEditModal = true;
    },
    closeEditModal() {
      this.showEditModal = false;
      this.editingUser = {};
    },
    async saveUserEdit() {
      try {
        await db.collection("users").doc(this.editingUser.id).update({
          apartment: this.editingUser.apartment,
          role: this.editingUser.role,
        });
        
        const index = this.activeUsers.findIndex(u => u.id === this.editingUser.id);
        if (index !== -1) {
          this.activeUsers[index] = { ...this.editingUser };
        }
        
        this.closeEditModal();
        alert("Usuario actualizado correctamente");
      } catch (err) {
        alert("Error al actualizar usuario: " + err.message);
      }
    },
    async toggleUserStatus(user) {
      try {
        const newStatus = !user.disabled;
        await db.collection("users").doc(user.id).update({
          disabled: newStatus,
        });
        
        if (newStatus) {
          const index = this.activeUsers.findIndex(u => u.id === user.id);
          if (index !== -1) {
            const disabledUser = { ...this.activeUsers[index], disabled: true };
            this.activeUsers.splice(index, 1);
            this.disabledUsers.push(disabledUser);
          }
        } else {
          const index = this.disabledUsers.findIndex(u => u.id === user.id);
          if (index !== -1) {
            const activeUser = { ...this.disabledUsers[index], disabled: false };
            this.disabledUsers.splice(index, 1);
            this.activeUsers.push(activeUser);
          }
        }
        
        alert(`Usuario ${newStatus ? 'deshabilitado' : 'habilitado'} correctamente`);
      } catch (err) {
        alert("Error al cambiar estado: " + err.message);
      }
    },
    getRoleLabel(role) {
      switch(role) {
        case 'admin': return 'Admin';
        case 'nomina': return 'Gestor';
        case 'Casos': return 'Casos';
        default: return 'Usuario';
      }
    }
  },
  mounted() {
    this.loadUsers();
  },
};
</script>

<style scoped lang="scss">
// Variables de colores
 $primary-color: #4a6cf7;
 $secondary-color: #6bcb77;
 $danger-color: #ef476f;
 $warning-color: #ffd166;
 $info-color: #4d96ff;
 $light-color: #f8f9fa;
 $dark-color: #343a40;
 $text-color: #495057;
 $border-color: #dee2e6;
 $shadow-sm: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
 $shadow-md: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
 $shadow-lg: 0 1rem 3rem rgba(0, 0, 0, 0.175);

// Estilos generales
.form-wrap {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  overflow-y: auto;
}

.register-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  min-height: calc(100vh - 4rem);
}

// Formulario de creación
.register {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: $shadow-md;
  flex: none;
  
  h2 {
    color: $dark-color;
    margin-bottom: 1.5rem;
    font-weight: 700;
    font-size: 1.75rem;
    text-align: center;
    position: relative;
    
    &::after {
      content: '';
      position: absolute;
      bottom: -10px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 4px;
      background: $primary-color;
      border-radius: 2px;
    }
  }
  
  .inputs {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
    margin-bottom: 1.5rem;
  }
  
  .input {
    position: relative;
    
    input, select {
      width: 100%;
      padding: 1rem 1rem 1rem 3rem;
      border: 2px solid $border-color;
      border-radius: 12px;
      font-size: 1rem;
      transition: all 0.3s ease;
      background: $light-color;
      
      &:focus {
        border-color: $primary-color;
        background: white;
        box-shadow: 0 0 0 0.25rem rgba(74, 108, 247, 0.25);
        outline: none;
      }
      
      // Estilo para campos inválidos
      &.invalid {
        border-color: $danger-color;
        background: rgba(239, 71, 111, 0.05);
      }
    }
    
    .icon {
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      color: #6c757d;
      width: 20px;
      height: 20px;
    }
    
    // Mensajes de error debajo de los inputs
    .error-message {
      position: absolute;
      bottom: -22px;
      left: 0;
      font-size: 0.75rem;
      color: $danger-color;
      display: flex;
      align-items: center;
      
      &::before {
        content: '⚠️';
        margin-right: 4px;
      }
    }
  }
  
  button {
    background: $primary-color;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 1rem 2rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: $shadow-sm;
    
    &:hover:not(:disabled) {
      background: #3a5bd9;
      transform: translateY(-2px);
      box-shadow: $shadow-md;
    }
    
    &:disabled {
      background: #adb5bd;
      cursor: not-allowed;
      opacity: 0.7;
    }
  }
  
  .error {
    color: $danger-color;
    margin-top: 1rem;
    padding: 0.75rem;
    background: rgba(239, 71, 111, 0.1);
    border-radius: 8px;
    border-left: 4px solid $danger-color;
  }
}

// Validación de contraseña
.password-requirements {
  margin-top: 0.5rem;
  padding: 1rem;
  background: rgba(74, 108, 247, 0.05);
  border-radius: 12px;
  border-left: 4px solid $primary-color;
  
  .requirement {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: $text-color;
    
    &.valid {
      color: $secondary-color;
    }
    
    .requirement-icon {
      margin-right: 0.5rem;
      font-weight: bold;
    }
  }
}

// Campo de búsqueda
.search-container {
  width: 100%;
  margin-bottom: 0.5rem;
  
  .search-input {
    width: 100%;
    padding: 1rem 1.5rem;
    border: 2px solid $border-color;
    border-radius: 50px;
    font-size: 1rem;
    background: white;
    box-shadow: $shadow-sm;
    transition: all 0.3s ease;
    
    &:focus {
      border-color: $primary-color;
      box-shadow: 0 0 0 0.25rem rgba(74, 108, 247, 0.25);
      outline: none;
    }
  }
}

// Listas de usuarios
.users-list {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: $shadow-md;
  flex: 1;
  display: flex;
  flex-direction: column;
  max-height: 500px;
  
  h3 {
    color: $dark-color;
    margin: 0 0 1.5rem 0;
    font-weight: 700;
    font-size: 1.5rem;
    display: flex;
    align-items: center;
    
    &::before {
      content: '';
      display: inline-block;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      margin-right: 12px;
    }
  }
  
  &.active-users {
    border-top: 5px solid $secondary-color;
    
    h3::before {
      background-color: $secondary-color;
    }
  }
  
  &.disabled-users {
    border-top: 5px solid $danger-color;
    
    h3::before {
      background-color: $danger-color;
    }
  }
  
  .users-list-container {
    flex: 1;
    overflow-y: auto;
    padding-bottom: 1rem;
  }
  
  .no-users {
    text-align: center;
    color: #6c757d;
    padding: 2rem;
    font-style: italic;
    background: rgba(108, 117, 125, 0.05);
    border-radius: 12px;
  }
}

// Items de usuario
.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  margin-bottom: 1rem;
  background: $light-color;
  border-radius: 12px;
  box-shadow: $shadow-sm;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: $shadow-md;
    border-left-color: $primary-color;
  }
  
  .user-info {
    flex: 1;
  }
  
  .user-name {
    font-weight: 700;
    font-size: 1.1rem;
    color: $dark-color;
    margin-bottom: 0.5rem;
  }
  
  .user-details {
    font-size: 0.9rem;
    color: $text-color;
    
    div {
      margin-bottom: 0.25rem;
    }
  }
  
  .user-status {
    margin-top: 0.75rem;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  
  .user-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-left: 1rem;
  }
}

// Badges
.role-badge, .status-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.role-badge {
  &.admin {
    background-color: rgba(255, 107, 107, 0.15);
    color: #ff6b6b;
  }
  &.nomina {
    background-color: rgba(77, 150, 255, 0.15);
    color: #4d96ff;
  }
  &.user {
    background-color: rgba(107, 203, 119, 0.15);
    color: $secondary-color;
  }
  &.Casos {
    background-color: rgba(155, 93, 229, 0.15);
    color: #9b5de5;
  }
}

.status-badge {
  &.active {
    background-color: rgba(107, 203, 119, 0.15);
    color: $secondary-color;
  }
  
  &.disabled {
    background-color: rgba(211, 211, 211, 0.3);
    color: #6c757d;
  }
}

// Botones pequeños
.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: $shadow-sm;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-md;
  }
  
  &.reset {
    background-color: $warning-color;
    color: $dark-color;
  }
  
  &.disable {
    background-color: $danger-color;
    color: white;
  }
  
  &.enable {
    background-color: $secondary-color;
    color: white;
  }
}

// Modal
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  width: 350px;
  text-align: center;
  box-shadow: $shadow-lg;
  animation: modalFadeIn 0.3s ease;
  
  h3 {
    color: $dark-color;
    margin-bottom: 1rem;
    font-weight: 700;
  }
  
  p {
    color: $text-color;
    margin-bottom: 1.5rem;
  }
  
  .admin-input {
    width: 100%;
    padding: 1rem;
    border: 2px solid $border-color;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
    
    &:focus {
      border-color: $primary-color;
      box-shadow: 0 0 0 0.25rem rgba(74, 108, 247, 0.25);
      outline: none;
    }
  }
  
  .modal-actions {
    display: flex;
    justify-content: space-around;
    gap: 1rem;
    
    .button {
      flex: 1;
      padding: 0.75rem 1.5rem;
      border-radius: 12px;
      border: none;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:first-child {
        background: $primary-color;
        color: white;
        
        &:hover {
          background: #3a5bd9;
        }
      }
      
      &:last-child {
        background: #e9ecef;
        color: $dark-color;
        
        &:hover {
          background: #dee2e6;
        }
      }
    }
  }
}

.edit-modal {
  width: 400px;
  
  .edit-form {
    margin: 1.5rem 0;
    
    .input {
      margin-bottom: 1rem;
    }
  }
  
  .role-select {
    width: 100%;
    padding: 1rem 1rem 1rem 3rem;
    border: 2px solid $border-color;
    border-radius: 12px;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: $light-color;
    appearance: none;
    background-repeat: no-repeat;
    background-position: right 1rem center;
    background-size: 1em;
    
    &:focus {
      border-color: $primary-color;
      background: white;
      box-shadow: 0 0 0 0.25rem rgba(74, 108, 247, 0.25);
      outline: none;
    }
  }
  
  .input {
    position: relative;
    
    .icon {
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      color: #6c757d;
      width: 20px;
      height: 20px;
    }
  }
}

// Animaciones
@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Estilos responsive
@media (min-width: 768px) {
  .register-container {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: flex-start;
  }
  
  .register {
    flex: 1 1 45%;
    min-width: 350px;
  }
  
  .search-container {
    flex: 1 1 100%;
  }
  
  .users-list {
    flex: 1 1 45%;
    min-width: 350px;
  }
}

@media (min-width: 992px) {
  .register {
    flex: 1 1 30%;
  }
  
  .users-list {
    flex: 1 1 30%;
  }
}

// Mejoras para pantallas muy pequeñas
@media (max-width: 576px) {
  .form-wrap {
    padding: 1rem;
  }
  
  .register-container {
    gap: 1.5rem;
  }
  
  .register {
    padding: 1.5rem;
    
    h2 {
      font-size: 1.5rem;
    }
    
    .inputs {
      gap: 1rem;
    }
    
    .input {
      input, select {
        padding: 0.875rem 0.875rem 0.875rem 2.75rem;
        font-size: 0.95rem;
      }
      
      .icon {
        left: 0.875rem;
      }
    }
    
    button {
      padding: 0.875rem 1.75rem;
      font-size: 0.95rem;
    }
  }
  
  .user-item {
    flex-direction: column;
    align-items: flex-start;
    
    .user-actions {
      flex-direction: row;
      margin-left: 0;
      margin-top: 1rem;
      width: 100%;
      
      .btn-small {
        flex: 1;
      }
    }
  }
  
  .modal {
    width: 90%;
    max-width: 350px;
    padding: 1.5rem;
  }
  
  .edit-modal {
    width: 90%;
    max-width: 400px;
    
    .role-select {
      width: 100%;
      padding: 1rem 1rem 1rem 3rem;
      border: 2px solid $border-color;
      border-radius: 12px;
      font-size: 1rem;
      transition: all 0.3s ease;
      background: $light-color;
      appearance: none;
      background-repeat: no-repeat;
      background-position: right 1rem center;
      background-size: 1em;
      
      &:focus {
        border-color: $primary-color;
        background: white;
        box-shadow: 0 0 0 0.25rem rgba(74, 108, 247, 0.25);
        outline: none;
      }
    }
  }
}
</style>