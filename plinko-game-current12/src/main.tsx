import './styles/global.css'
import React, { useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import { Toaster } from 'react-hot-toast'
import { Routes } from 'routes'
import { useAuthStore } from 'store/auth'
import './i18n/i18n'
import toast from 'react-hot-toast'

const container = document.getElementById('root')!
const root = createRoot(container)

function MainApp() {
  const setTelegramUser = useAuthStore(state => state.setTelegramUser)

  useEffect(() => {
    console.log('useEffect running. Checking for Telegram API...')
    console.log('window.Telegram:', window.Telegram)
    if (window.Telegram) {
      console.log('window.Telegram.WebApp:', window.Telegram.WebApp)
    }

    if (window.Telegram && window.Telegram.WebApp) {
      console.log('Telegram WebApp API found!')
      const webApp = window.Telegram.WebApp
      console.log('webApp.initDataUnsafe:', webApp.initDataUnsafe)
      console.log('webApp.userInfo:', webApp.userInfo)

      let telegramUserId: { id: number } | null = null

      if (webApp.userInfo && webApp.userInfo.id) {
        telegramUserId = { id: webApp.userInfo.id }
        console.log('Using userInfo.id:', telegramUserId.id)
      } else if (
        webApp.initDataUnsafe &&
        webApp.initDataUnsafe.user &&
        webApp.initDataUnsafe.user.id
      ) {
        telegramUserId = { id: webApp.initDataUnsafe.user.id }
        console.log('Using initDataUnsafe.user.id:', telegramUserId.id)
      }

      if (telegramUserId) {
        setTelegramUser(telegramUserId)
        console.log('Telegram User ID stored:', telegramUserId)
      } else {
        console.log('Telegram User ID not found in userInfo or initDataUnsafe.')
        setTelegramUser(null)
      }

      try {
        if (typeof webApp.ready === 'function') {
          webApp.ready()
        }
        console.log('webApp.ready() called successfully.')
      } catch (e) {
        console.error('Error calling webApp.ready():', e)
      }
    } else {
      console.error('Debug: Telegram WebApp API not found.')
      setTelegramUser(null)
    }
  }, [setTelegramUser])

  // === DEVELOPMENT-ONLY: Expose function to edit balance in console ===
  useEffect(() => {
    if (import.meta.env.DEV) {
      console.log('[DEV] Development mode detected. Adding debug functions.')

      const zustandSetBalance = useAuthStore.getState().setBalance

      window.dev_setBalance = (newBalance: number) => {
        if (typeof newBalance === 'number' && !isNaN(newBalance)) {
          zustandSetBalance(newBalance)
          console.log(`[DEV] Balance manually set to: ${newBalance}`)
          toast.success(`[DEV] Balance set to: ${newBalance}`)
        } else {
          console.error(
            '[DEV] Invalid balance value provided to dev_setBalance. Please provide a number.'
          )
        }
      }

      console.log(
        "[DEV] Function 'dev_setBalance(amount)' is now available in the browser console."
      )

      return () => {
        if (window.dev_setBalance) {
          console.log("[DEV] Removing debug function 'dev_setBalance'.")
          delete window.dev_setBalance
        }
      }
    }
  }, [])
  // ==========================

  return (
    <>
      <Routes />
      <Toaster />
    </>
  )
}

root.render(
  <React.StrictMode>
    <MainApp />
  </React.StrictMode>
)
