import { useState } from 'react'
import { Header } from './components/Header'
import { NowPlaying } from './components/NowPlaying'
import { DeviceList } from './components/DeviceList'
import { StopButton } from './components/StopButton'
import { Device } from './types'

// Mock Data
const MOCK_DEVICES: Device[] = [
  { id: '1', name: 'Living Room', model: 'Google Home', type: 'cast', volume: 0.65, is_active: true },
  { id: '2', name: 'Kitchen', model: 'Nest Hub', type: 'cast', volume: 0.4, is_active: false },
  { id: '3', name: 'Office', model: 'Nest Mini', type: 'audio', volume: 0.3, is_active: false },
  { id: '4', name: 'Whole House', model: 'Group • 3 Devices', type: 'group', volume: 0.5, is_active: false },
]

function App() {
  const [devices, setDevices] = useState<Device[]>(MOCK_DEVICES)

  const handleToggle = (id: string, active: boolean) => {
    setDevices(prev => prev.map(d => d.id === id ? { ...d, is_active: active } : d))
  }

  const handleVolumeChange = (id: string, volume: number) => {
    setDevices(prev => prev.map(d => d.id === id ? { ...d, volume } : d))
  }

  const handleStopAll = () => {
    setDevices(prev => prev.map(d => ({ ...d, is_active: false })))
  }

  return (
    <div className="relative flex h-full min-h-screen w-full flex-col overflow-x-hidden max-w-md mx-auto shadow-2xl bg-background-light dark:bg-background-dark">
      <Header />
      <main className="flex-1 flex flex-col p-4 gap-6">
        <NowPlaying />
        <DeviceList 
          devices={devices} 
          onToggle={handleToggle} 
          onVolumeChange={handleVolumeChange}
        />
      </main>
      <StopButton onStopAll={handleStopAll} />
    </div>
  )
}

export default App
