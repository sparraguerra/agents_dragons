<template>
  <div class="h-full w-full bg-fantasy-dark flex flex-col">
    <!-- Loading Screen -->
    <div v-if="loading" class="h-full flex items-center justify-center">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-fantasy-gold mb-6"></div>
        <h2 class="text-2xl capitalize font-bold text-fantasy-gold mb-2">{{ storyTitle }}</h2>
        <p class="text-gray-400">Preparing your adventure...</p>
      </div>
    </div>

    <!-- Main Game Interface -->
    <template v-else>
      <!-- Header -->
      <header class="bg-fantasy-medium border-b border-fantasy-accent p-4 shadow-lg">
        <div class="container mx-auto flex items-center justify-between">
          <div>
            <h1 class="text-3xl capitalize font-bold text-fantasy-gold">🐉 {{ storyTitle }}</h1>
            <p class="text-gray-400 text-sm mt-1">AI-Powered Narrative Roleplaying Game</p>
          </div>
          <button 
            @click="$emit('back')"
            class="bg-fantasy-accent hover:bg-opacity-80 text-white font-bold py-2 px-4 rounded-lg transition-all"
          >
            ← Back to Stories
          </button>
        </div>
      </header>

      <!-- Main Chat Area -->
      <div class="flex-1 overflow-hidden relative">
        <!-- Background Image -->
        <div 
          v-if="backgroundImage" 
          class="absolute inset-0 bg-cover bg-center bg-no-repeat pointer-events-none"
          :style="{ backgroundImage: `url(data:image/png;base64,${backgroundImage})` }"
        ></div>
      <div class="container mx-auto h-full flex flex-col py-4 px-4 relative z-10">
        <!-- Messages Container -->
        <div 
          ref="messagesContainer" 
          class="flex-1 overflow-y-auto space-y-4 mb-4 px-2"
        >
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            class="animate-fade-in"
          >
            <!-- User Message -->
            <div 
              v-if="message.role === 'user'" 
              class="flex justify-end"
            >
              <div class="max-w-3xl bg-fantasy-highlight bg-opacity-75 rounded-lg p-4 shadow-md">
                <div class="flex items-start gap-3">
                  <div class="flex-1">
                    <p class="text-sm font-semibold text-fantasy-gold mb-1">You</p>
                    <p class="text-white">{{ message.content }}</p>
                  </div>
                  <span class="text-2xl">⚔️</span>
                </div>
              </div>
            </div>

            <!-- Assistant Message -->
            <div 
              v-else 
              class="flex justify-start"
            >
              <div class="max-w-3xl bg-fantasy-accent bg-opacity-75 rounded-lg p-4 shadow-md">
                <div class="flex items-start gap-3">
                  <span class="text-2xl">📜</span>
                  <div class="flex-1">
                    <p class="text-sm font-semibold text-fantasy-gold mb-1">Storyteller</p>
                    <div 
                      class="text-gray-200 prose prose-invert prose-base max-w-none"
                      v-html="renderMarkdown(message.content)"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="isTyping" class="flex justify-start animate-fade-in">
            <div class="max-w-3xl bg-fantasy-accent bg-opacity-75 rounded-lg p-4 shadow-md">
              <div class="flex items-start gap-3">
                <span class="text-2xl">📜</span>
                <div class="flex space-x-2">
                  <div class="w-2 h-2 bg-fantasy-gold rounded-full animate-bounce" style="animation-delay: 0s"></div>
                  <div class="w-2 h-2 bg-fantasy-gold rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  <div class="w-2 h-2 bg-fantasy-gold rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="bg-fantasy-medium bg-opacity-75 rounded-lg p-4 shadow-lg">
          <!-- Image Generation Checkbox -->
          <div class="mb-3 flex items-center gap-2">
            <input
              id="image-generation-toggle"
              v-model="imageGenerationEnabled"
              type="checkbox"
              class="w-4 h-4 text-fantasy-gold bg-fantasy-dark border-fantasy-accent rounded focus:ring-fantasy-gold focus:ring-2"
            />
            <label for="image-generation-toggle" class="text-gray-300 text-sm cursor-pointer">
              🎨 Enable AI Image Generation
            </label>
          </div>
          
          <form @submit.prevent="sendMessage" class="flex gap-3">
            <input
              v-model="inputMessage"
              type="text"
              placeholder="Type your action or speak to the world..."
              class="flex-1 bg-fantasy-dark text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-fantasy-gold placeholder-gray-500"
              :disabled="isTyping"
            />
            <button
              type="submit"
              :disabled="!inputMessage.trim() || isTyping"
              class="bg-fantasy-gold hover:bg-opacity-80 text-white font-bold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script>
import { ref, nextTick, onMounted } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

export default {
  name: 'GameView',
  props: {
    storyTitle: {
      type: String,
      required: true
    }
  },
  emits: ['back'],
  setup(props) {
    const messages = ref([])
    const loading = ref(true)
    const inputMessage = ref('')
    const isTyping = ref(false)
    const messagesContainer = ref(null)
    const imageGenerationEnabled = ref(false)
    const backgroundImage = ref(null)

    // Configure marked for better rendering
    marked.setOptions({
      breaks: true,
      gfm: true
    })

    const renderMarkdown = (content) => {
      const rawMarkup = marked.parse(content)
      return DOMPurify.sanitize(rawMarkup)
    }

    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }

    const startStory = async () => {
      try {
        const response = await fetch('http://localhost:8005/start', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            story: props.storyTitle
          })
        })

        if (!response.ok) {
          throw new Error('Failed to start story')
        }

        const data = await response.json()
        
        // Set the initial message with the story intro
        messages.value = [{
          role: 'assistant',
          content: data.introduction
        }]
      } catch (error) {
        console.error('Error starting story:', error)
        messages.value = [{
          role: 'assistant',
          content: `**[Error]**

Failed to start the story. Please make sure the backend is running at http://localhost:8005

Error: ${error.message}`
        }]
      } finally {
        loading.value = false
        scrollToBottom()
      }
    }

    const sendMessage = async () => {
      if (!inputMessage.value.trim() || isTyping.value) return

      const userMessage = inputMessage.value.trim()
      messages.value.push({
        role: 'user',
        content: userMessage
      })
      
      inputMessage.value = ''
      scrollToBottom()
      isTyping.value = true

      try {
        // Call the backend API with streaming
        const response = await fetch('http://localhost:8005/game', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: userMessage,
            agent_name: 'Orchestrator'
          })
        })

        if (!response.ok) {
          throw new Error('Failed to get response from server')
        }

        // Create an empty assistant message that will be populated with the stream
        messages.value.push({
          role: 'assistant',
          content: ''
        })
        
        const messageIndex = messages.value.length - 1

        // Read the stream
        const reader = response.body.getReader()
        const decoder = new TextDecoder()

        while (true) {
          const { done, value } = await reader.read()
          
          if (done) {
            break
          }

          // Decode the chunk
          const chunk = decoder.decode(value, { stream: true })
          messages.value[messageIndex].content += chunk
          scrollToBottom()
        }
        isTyping.value = false
        // Generate image if enabled
        console.log(imageGenerationEnabled.value)
        if (imageGenerationEnabled.value) {
          try {
            const imageResponse = await fetch('http://localhost:8005/create_image', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              }
            })

            if (imageResponse.ok) {
              const imageData = await imageResponse.json()
              backgroundImage.value = imageData.image
            }
          } catch (imageError) {
            console.error('Error generating image:', imageError)
            // Don't show error to user, just fail silently for image generation
          }
        }        
      } catch (error) {
        console.error('Error sending message:', error)
        
        // Update the assistant message with error
        messages.value[messageIndex].content = `**[Error]**

Failed to connect to the game server. Please make sure the backend is running at http://localhost:8005

Error: ${error.message}`
      } finally {
        isTyping.value = false
        scrollToBottom()
      }
    }

    onMounted(() => {
      startStory()
    })

    return {
      messages,
      loading,
      inputMessage,
      isTyping,
      messagesContainer,
      imageGenerationEnabled,
      backgroundImage,
      renderMarkdown,
      sendMessage
    }
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

/* Custom scrollbar */
:deep(.overflow-y-auto)::-webkit-scrollbar {
  width: 8px;
}

:deep(.overflow-y-auto)::-webkit-scrollbar-track {
  background: #16213e;
  border-radius: 4px;
}

:deep(.overflow-y-auto)::-webkit-scrollbar-thumb {
  background: #533483;
  border-radius: 4px;
}

:deep(.overflow-y-auto)::-webkit-scrollbar-thumb:hover {
  background: #e94560;
}

/* Markdown prose styling */
:deep(.prose) {
  color: #e5e7eb;
  font-size: 1rem;
  line-height: 1.8;
}

:deep(.prose p) {
  margin-top: 1rem;
  margin-bottom: 1rem;
}

:deep(.prose h1),
:deep(.prose h2),
:deep(.prose h3) {
  color: #e94560;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

:deep(.prose strong) {
  color: #f3f4f6;
  font-weight: 600;
}

:deep(.prose em) {
  color: #d1d5db;
}

:deep(.prose ul),
:deep(.prose ol) {
  margin-top: 1rem;
  margin-bottom: 1rem;
  padding-left: 1.5rem;
  list-style-position: outside;
}

:deep(.prose ul) {
  list-style-type: disc;
}

:deep(.prose ol) {
  list-style-type: decimal;
}

:deep(.prose li) {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding-left: 0.25rem;
}

:deep(.prose li::marker) {
  color: #e94560;
}

:deep(.prose code) {
  background-color: #1a1a2e;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  color: #e94560;
}
</style>
