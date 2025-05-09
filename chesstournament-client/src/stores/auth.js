import { defineStore } from "pinia";

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null, // Cargar token desde localStorage
    isAdmin: false, // Puedes usar esta propiedad si necesitas roles
    welcomeMessage: '', // Mensaje de bienvenida
  }),
  actions: {
    login(token) {
      this.token = token;
      this.isAdmin = true; // Configurar como administrador al iniciar sesión
      localStorage.setItem('token', token); // Guardar token en localStorage
    },
    setWelcomeMessage(message) {
      this.welcomeMessage = message;
    },
    logout() {
      this.token = null;
      this.isAdmin = false; // Restablecer estado de administrador
      localStorage.removeItem('token'); // Eliminar token de localStorage
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.token, // Verificar si el usuario está autenticado
  },
});
