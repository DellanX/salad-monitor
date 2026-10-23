import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'
import Dashboard from '../pages/Dashboard.vue'
import System from '../pages/System.vue'
import Gpu from '../pages/Gpu.vue'
import Workloads from '../pages/Workloads.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'system',
        name: 'System',
        component: System
      },
      {
        path: 'gpu',
        name: 'GPU',
        component: Gpu
      },
      {
        path: 'workloads',
        name: 'Workloads',
        component: Workloads
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router