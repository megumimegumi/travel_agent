import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Recommendation from '../views/Recommendation.vue'
import Planner from '../views/Planner.vue'
import MyItineraries from '../views/MyItineraries.vue'
import Favorites from '../views/Favorites.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import ForgotPassword from '../views/ForgotPassword.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/planner', component: Planner, meta: { requiresAuth: true } },
  { path: '/recommend', component: Recommendation, meta: { requiresAuth: true } },
  { path: '/my-itineraries', component: MyItineraries, meta: { requiresAuth: true } },
  { path: '/favorites', component: Favorites, meta: { requiresAuth: true } },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/forgot-password', component: ForgotPassword },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('user');
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});

export default router
