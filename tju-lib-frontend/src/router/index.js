import { createRouter, createWebHistory } from 'vue-router'
import About from '../views/About.vue'
import Show from '../views/Show.vue'
import Log from '../views/Log.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: '/',
      component: Show,
    },
    {
      path: '/show',
      name: 'show',
      component: Show,
    },
    {
      path: '/about',
      name: 'about',
      component: About,
    },
    {
      path: '/log',
      name: 'log',
      component: Log,
    },
  ],
})

export default router
