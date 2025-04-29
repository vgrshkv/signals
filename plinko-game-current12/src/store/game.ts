import create from 'zustand'

interface Game {
  gamesRunning: number
  soundEnabled: boolean
  setGamesRunning: (gamesRunning: number) => void
  incrementGamesRunning: () => void
  decrementGamesRunning: () => void
  setSoundEnabled: (enabled: boolean) => void
  toggleSound: () => void
}

export const useGameStore = create<Game>((set, get) => ({
  gamesRunning: 0,
  soundEnabled: true,
  setGamesRunning: (gamesRunning: number) => {
    set({ gamesRunning })
  },
  incrementGamesRunning: () => {
    const gamesRunning = get().gamesRunning
    const calc = gamesRunning + 1

    set({ gamesRunning: calc < 0 ? 1 : calc })
  },
  decrementGamesRunning: () => {
    const gamesRunning = get().gamesRunning
    const calc = gamesRunning - 1

    set({ gamesRunning: calc < 0 ? 0 : calc })
  },
  setSoundEnabled: (enabled: boolean) => {
    set({ soundEnabled: enabled })
  },
  toggleSound: () => {
    const soundEnabled = get().soundEnabled
    set({ soundEnabled: !soundEnabled })
  }
}))
