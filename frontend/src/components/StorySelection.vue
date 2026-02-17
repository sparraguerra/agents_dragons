<template>
  <div class="h-full w-full bg-fantasy-dark flex flex-col">
    <!-- Header -->
    <header class="bg-fantasy-medium border-b border-fantasy-accent p-4 shadow-lg">
      <div class="container mx-auto">
        <h1 class="text-4xl font-bold text-fantasy-gold">🐉 Agents & Dragons</h1>
        <p class="text-gray-400 text-sm mt-1">Choose Your Adventure</p>
      </div>
    </header>

    <!-- Main Content Area -->
    <div class="flex-1 overflow-y-auto">
      <div class="container mx-auto py-8 px-4">
        <!-- Loading State -->
        <div v-if="loading" class="flex justify-center items-center h-64">
          <div class="text-center">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-fantasy-gold"></div>
            <p class="text-gray-400 mt-4">Loading stories...</p>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="text-center py-12">
          <div class="bg-red-900 bg-opacity-20 border border-red-500 rounded-lg p-6 max-w-2xl mx-auto">
            <p class="text-red-400 text-lg">⚠️ Failed to load stories</p>
            <p class="text-gray-400 mt-2">{{ error }}</p>
            <button 
              @click="fetchStories"
              class="mt-4 bg-fantasy-gold hover:bg-opacity-80 text-white font-bold py-2 px-6 rounded-lg transition-all"
            >
              Retry
            </button>
          </div>
        </div>

        <!-- Stories Grid -->
        <div v-else-if="stories.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="story in stories"
            :key="story"
            @click="selectStory(story)"
            class="group relative overflow-hidden rounded-lg shadow-lg cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-2xl"
          >
            <!-- Background Image (Placeholder) -->
            <div class="aspect-video bg-gradient-to-br from-fantasy-accent to-fantasy-highlight relative">
              <div class="absolute inset-0 bg-cover bg-center opacity-40" 
                   style="background-image: url('https://images.unsplash.com/photo-1518562923427-c91e4d58a814?w=500&h=300&fit=crop')">
              </div>
              <div class="absolute inset-0 bg-gradient-to-t from-fantasy-dark via-transparent to-transparent"></div>
            </div>

            <!-- Story Title Overlay -->
            <div class="absolute inset-0 flex items-end p-6">
              <div class="w-full">
                <h3 class="text-2xl font-bold text-white capitalize group-hover:text-fantasy-gold transition-colors">
                  {{ story }}
                </h3>
                <div class="flex items-center mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <span class="text-fantasy-gold text-sm">Begin Adventure →</span>
                </div>
              </div>
            </div>

            <!-- Decorative Corner -->
            <div class="absolute top-0 right-0 w-16 h-16">
              <div class="absolute transform rotate-45 bg-fantasy-gold text-fantasy-dark text-xs font-bold py-1 px-8 right-[-32px] top-[12px]">
                NEW
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-12">
          <div class="text-gray-400 text-lg">
            <p class="text-4xl mb-4">📚</p>
            <p>No stories available yet</p>
            <p class="text-sm mt-2">Add markdown files to the stories folder to get started</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'StorySelection',
  emits: ['select-story'],
  setup(props, { emit }) {
    const stories = ref([])
    const loading = ref(true)
    const error = ref(null)

    const fetchStories = async () => {
      loading.value = true
      error.value = null

      try {
        const response = await fetch('http://localhost:8005/stories')
        
        if (!response.ok) {
          throw new Error(`Failed to fetch stories: ${response.status} ${response.statusText}`)
        }

        const data = await response.json()
        stories.value = data
      } catch (err) {
        console.error('Error fetching stories:', err)
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const selectStory = (story) => {
      emit('select-story', story)
    }

    onMounted(() => {
      fetchStories()
    })

    return {
      stories,
      loading,
      error,
      fetchStories,
      selectStory
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #16213e;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #533483;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #e94560;
}
</style>
