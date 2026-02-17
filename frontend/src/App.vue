<template>
  <div class="h-screen w-screen">
    <!-- Story Selection View -->
    <StorySelection 
      v-if="currentView === 'selection'"
      @select-story="handleStorySelection"
    />
    
    <!-- Game View -->
    <GameView 
      v-else-if="currentView === 'game'"
      :story-title="selectedStory"
      @back="handleBack"
    />
  </div>
</template>

<script>
import { ref } from 'vue'
import StorySelection from './components/StorySelection.vue'
import GameView from './components/GameView.vue'

export default {
  name: 'App',
  components: {
    StorySelection,
    GameView
  },
  setup() {
    const currentView = ref('selection')
    const selectedStory = ref('')

    const handleStorySelection = (storyTitle) => {
      selectedStory.value = storyTitle
      currentView.value = 'game'
    }

    const handleBack = () => {
      currentView.value = 'selection'
      selectedStory.value = ''
    }

    return {
      currentView,
      selectedStory,
      handleStorySelection,
      handleBack
    }
  }
}
</script>
