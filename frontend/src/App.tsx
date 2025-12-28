import { useState, useEffect, useCallback } from 'react'
import { Header } from './components/Header'
import { NowPlaying } from './components/NowPlaying'
import { DeviceList } from './components/DeviceList'
import { StopButton } from './components/StopButton'
import { Device } from './types'
import { api } from './api'

function App() {
  const [devices, setDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDevices = useCallback(async () => {
    try {
      const data = await api.getDevices()
      // Merge with local optimistic state if needed, or just replace
      // Ideally we want to preserve local UI state like "spinning" toggles if we had them
      setDevices(data)
      setError(null)
    } catch (err) {
      console.error(err)
      setError('Failed to load devices')
    } finally {
      setLoading(false)
    }
  }, [])

  // Poll for devices every 5 seconds
  useEffect(() => {
    fetchDevices()
    const interval = setInterval(fetchDevices, 5000)
    return () => clearInterval(interval)
  }, [fetchDevices])

  const handleToggle = async (id: string, active: boolean) => {
    // Optimistic update
    setDevices(prev => prev.map(d => d.id === id ? { ...d, is_active: active } : d))
    
    try {
      if (active) {
        await api.startCast(id)
      } else {
        await api.stopCast(id)
      }
      // Refetch to confirm state
      fetchDevices()
    } catch (err) {
      console.error('Toggle failed', err)
      // Revert on error
      setDevices(prev => prev.map(d => d.id === id ? { ...d, is_active: !active } : d))
    }
  }

  const handleVolumeChange = async (id: string, volume: number) => {
    // Optimistic update
    setDevices(prev => prev.map(d => d.id === id ? { ...d, volume } : d))
    
    // Debouncing could be added here, but for now we'll just fire requests
    // Using a timeout ref or lodash debounce would be better for slider dragging
    try {
      await api.setVolume(id, volume)
    } catch (err) {
      console.error('Volume set failed', err)
    }
  }

  const handleStopAll = async () => {
    const activeDevices = devices.filter(d => d.is_active)
    setDevices(prev => prev.map(d => ({ ...d, is_active: false }))) // Optimistic

    await Promise.allSettled(activeDevices.map(d => api.stopCast(d.id)))
    fetchDevices()
  }

  return (
    <div className="relative flex h-full min-h-screen w-full flex-col overflow-x-hidden max-w-md mx-auto shadow-2xl bg-background-light dark:bg-background-dark">
      <Header />
      <main className="flex-1 flex flex-col p-4 gap-6">
        <NowPlaying />
        {loading && devices.length === 0 ? (
          <div className="flex justify-center p-8 text-slate-400">Loading devices...</div>
        ) : error ? (
           <div className="flex justify-center p-8 text-red-400">{error}</div>
        ) : (
          <DeviceList 
            devices={devices} 
            onToggle={handleToggle} 
            onVolumeChange={handleVolumeChange}
          />
        )}
      </main>
      <StopButton onStopAll={handleStopAll} />
    </div>
  )
}

export default App