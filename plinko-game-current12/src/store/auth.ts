import { produce } from 'immer'
// Removed toast, as it's not directly used in this store anymore
import create from 'zustand'

// Now store only the object with ID or null
interface TelegramUserId {
  id: number
}

interface Wallet {
  balance: number
}

interface State {
  telegramUser: TelegramUserId | null // State for Telegram user ID
  wallet: Wallet
  setBalance: (balance: number) => void
  incrementBalance: (amount: number) => void
  decrementBalance: (amount: number) => void
  setTelegramUser: (user: TelegramUserId | null) => void // Function to set the ID
  user: any
  isAuth: boolean
  setUser: (user: any) => void
  redeemGift: () => Promise<void>
  fetchBalance: (telegramId: number) => Promise<void>
  updateBalance: (telegramId: number, delta: number) => Promise<void>
}

const walletInitialState: Wallet = {
  balance: 0
}

const telegramUserInitialState: TelegramUserId | null = null

export const useAuthStore = create<State>((setState, getState) => ({
  telegramUser: telegramUserInitialState,
  wallet: walletInitialState,
  setBalance: (balance: number) => {
    setState(
      produce<State>(state => {
        state.wallet.balance = balance
      })
    )
  },
  incrementBalance: (amount: number) => {
    setState(
      produce<State>(state => {
        state.wallet.balance += amount
      })
    )
  },
  decrementBalance: (amount: number) => {
    setState(
      produce<State>(state => {
        state.wallet.balance -= amount
      })
    )
  },
  setTelegramUser: (user: TelegramUserId | null) => {
    // Accepts object with ID or null
    setState(
      produce<State>(state => {
        state.telegramUser = user
      })
    )
  },
  user: null,
  isAuth: false,
  setUser: (user: any) => {
    setState(
      produce<State>(state => {
        ;(state as any).user = user
      })
    )
  },
  redeemGift: async () => {
    // Заглушка для функции подарка
    return Promise.resolve()
  },
  fetchBalance: async (telegramId: number) => {
    const res = await fetch(`/api/get_balance?telegram_id=${telegramId}`)
    const data = await res.json()
    if (data.ok) {
      setState(
        produce<State>(state => {
          state.wallet.balance = data.pp_balance
        })
      )
    }
  },
  updateBalance: async (telegramId: number, delta: number) => {
    const res = await fetch('/api/update_balance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ telegram_id: telegramId, delta })
    })
    const data = await res.json()
    if (data.ok) {
      setState(
        produce<State>(state => {
          state.wallet.balance = data.pp_balance
        })
      )
    }
  }
}))
