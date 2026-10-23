<template>
  <div class="min-h-screen bg-white text-gray-900 dark:bg-gray-900 dark:text-white">
    <Header />
    <div class="container mx-auto px-4 py-6">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import Header from './Header.vue'
</script>