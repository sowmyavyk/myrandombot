import { useState, useRef, useEffect } from 'react'

interface Message {
  id: string
  role: 'user' | 'bot'
  content: string
  type?: 'tool' | 'llm'
  timestamp: Date
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showSidebar, setShowSidebar] = useState(false)
  const [userId] = useState(() => `user_${Math.random().toString(36).substr(2, 9)}`)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, user_id: userId }),
      })

      const data = await response.json()

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: data.reply,
        type: data.type || 'llm',
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: 'Sorry, I could not connect to the bot. Make sure the server is running.',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setMessages([])
  }

  return (
    <div className="flex h-screen bg-black text-white overflow-hidden font-sans">
      {/* Sidebar */}
      <div className={`${showSidebar ? 'w-64' : 'w-0'} transition-all duration-300 bg-neutral-900 border-r border-neutral-800 flex flex-col overflow-hidden`}>
        <div className="p-6 border-b border-neutral-800">
          <h1 className="text-xl font-light tracking-[0.2em] uppercase">Femicase</h1>
          <p className="text-xs text-neutral-500 mt-1">AI Assistant</p>
        </div>

        <div className="p-6 flex-1">
          <button
            onClick={clearChat}
            className="w-full py-3 px-4 border border-neutral-700 text-neutral-400 hover:bg-neutral-800 hover:text-white transition-all text-sm"
          >
            Clear Chat
          </button>
        </div>

        <div className="p-6 border-t border-neutral-800">
          <p className="text-xs text-neutral-600">v1.0</p>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-16 px-6 border-b border-neutral-800 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-2 hover:bg-neutral-900 transition-colors"
            >
              <svg className="w-5 h-5 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h2 className="font-light tracking-wide">Chat</h2>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span className="text-sm text-neutral-500">Online</span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-full border border-neutral-700 flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-lg font-light text-neutral-300 mb-2">Start a Conversation</h3>
              <p className="text-neutral-500 text-sm max-w-md">
                Ask me anything. I can help with files, code, or just chat.
              </p>
            </div>
          )}
          
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center border ${
                message.role === 'user'
                  ? 'border-neutral-600'
                  : message.type === 'tool'
                  ? 'border-neutral-500 bg-neutral-800'
                  : 'border-neutral-600'
              }`}>
                {message.role === 'user' ? (
                  <span className="text-xs text-neutral-400">Y</span>
                ) : (
                  <span className="text-xs text-neutral-400">AI</span>
                )}
              </div>
              <div className={`max-w-[70%] ${message.role === 'user' ? 'text-right' : ''}`}>
                <div className={`px-4 py-3 text-sm leading-relaxed ${
                  message.role === 'user'
                    ? 'bg-white text-black'
                    : message.type === 'tool'
                    ? 'bg-neutral-900 border border-neutral-800 font-mono text-xs'
                    : 'text-neutral-200'
                }`}>
                  <pre className={`whitespace-pre-wrap ${message.type === 'tool' ? 'max-h-60 overflow-y-auto' : ''} ${message.role === 'user' ? 'font-sans' : ''}`}>
                    {message.content}
                  </pre>
                </div>
                <p className="text-xs text-neutral-600 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full border border-neutral-700 flex items-center justify-center">
                <span className="text-xs text-neutral-400">AI</span>
              </div>
              <div className="bg-neutral-900 border border-neutral-800 px-4 py-3">
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 bg-neutral-500 rounded-full animate-pulse"></div>
                  <div className="w-1.5 h-1.5 bg-neutral-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-1.5 h-1.5 bg-neutral-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-neutral-800">
          <div className="max-w-3xl mx-auto">
            <div className="relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Type a message..."
                className="w-full bg-neutral-900 border border-neutral-800 px-6 py-4 text-white placeholder-neutral-500 focus:outline-none focus:border-emerald-500 transition-colors"
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-neutral-400 hover:text-emerald-500 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
