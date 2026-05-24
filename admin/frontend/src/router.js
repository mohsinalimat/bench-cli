import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('./pages/Dashboard.vue') },
  { path: '/apps', component: () => import('./pages/Apps.vue') },
  { path: '/sites', component: () => import('./pages/Sites.vue') },
  { path: '/sites/:name', component: () => import('./pages/SiteDetail.vue') },
  { path: '/processes', component: () => import('./pages/Processes.vue') },
  { path: '/logs', component: () => import('./pages/LogList.vue') },
  { path: '/logs/:filename', component: () => import('./pages/LogViewer.vue') },
  { path: '/tasks', component: () => import('./pages/TaskList.vue') },
  { path: '/tasks/:id', component: () => import('./pages/TaskDetail.vue') },
  { path: '/database/binlogs', component: () => import('./pages/Database.vue') },
  { path: '/database/binlogs/:name', component: () => import('./pages/BinlogDetail.vue') },
  { path: '/database/slow-queries', component: () => import('./pages/SlowQueries.vue') },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
