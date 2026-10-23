<template>
  <header class="bg-white border-b border-gray-200 py-4 px-6 dark:bg-gray-900 dark:border-gray-700">
    <div class="container mx-auto flex justify-between items-center">
      <div class="flex items-center space-x-2">
        <div class="bg-emerald-500 w-8 h-8 rounded-lg"></div>
        <h1 class="text-xl font-bold text-gray-900 dark:text-white">Salad Monitor</h1>
      </div>
      
      <nav class="hidden md:block">
        <ul class="flex space-x-6">
          <li>
            <router-link 
              to="/" 
              class="hover:text-emerald-600 transition-colors text-gray-700 dark:text-gray-300 dark:hover:text-emerald-400"
              active-class="text-emerald-600 font-medium dark:text-emerald-400"
            >
              Dashboard
            </router-link>
          </li>
          <li>
            <router-link 
              to="/system" 
              class="hover:text-emerald-600 transition-colors text-gray-700 dark:text-gray-300 dark:hover:text-emerald-400"
              active-class="text-emerald-600 font-medium dark:text-emerald-400"
            >
              System
            </router-link>
          </li>
          <li>
            <router-link 
              to="/gpu" 
              class="hover:text-emerald-600 transition-colors text-gray-700 dark:text-gray-300 dark:hover:text-emerald-400"
              active-class="text-emerald-600 font-medium dark:text-emerald-400"
            >
              GPU
            </router-link>
          </li>
          <li>
            <router-link 
              to="/workloads" 
              class="hover:text-emerald-600 transition-colors text-gray-700 dark:text-gray-300 dark:hover:text-emerald-400"
              active-class="text-emerald-600 font-medium dark:text-emerald-400"
            >
              Workloads
            </router-link>
          </li>
        </ul>
      </nav>
      
      <div class="flex items-center space-x-4">
        <UseDark v-slot="{ isDark, toggleDark }">
          <button @click="toggleDark()">
            <svg 
              v-if="isDark" 
              xmlns="http://www.w3.org/2000/svg" 
              class="h-5 w-5 text-gray-900 dark:text-white" 
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
            </svg>
            <svg 
              v-else 
              xmlns="http://www.w3.org/2000/svg" 
              class="h-5 w-5 text-gray-900 dark:text-white" 
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          </button>
        </UseDark>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { UseDark } from '@vueuse/components';

</script>