import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/components/HomeView.vue'
import LoginView from '@/components/LoginView.vue'
import LogoutView from '@/components/LogoutView.vue'
import TournamentCreate from '@/components/TournamentCreate.vue'
import TournamentDetail from '@/components/TournamentDetail.vue'
import FAQView from '@/components/FAQView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/logout',
      name: 'logout',
      component: LogoutView,
      meta: { requiresAuth: true }
    },
    {
      path: '/createtournament',
      name: 'createtournament',
      component: TournamentCreate,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/tournamentdetail/:tournament_id',
      name: 'tournamentdetail',
      component: TournamentDetail,
      props: true
    },
    {
      path: '/faq',
      name: 'faq',
      component: FAQView
    }
  ]
})


// Navigation guard para manejar autenticación
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.token) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router