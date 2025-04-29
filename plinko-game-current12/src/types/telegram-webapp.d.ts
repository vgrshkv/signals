declare global {
  interface Window {
    Telegram: {
      WebApp: {
        initDataUnsafe?: any
        userInfo?: any
        ready?: () => void
        openTelegramLink: (url: string) => void
        openInvoice?: (url: string) => void
        // Добавьте другие методы, которые вы используете из Telegram WebApp
      }
    }
    dev_setBalance?: (amount: number) => void
  }
}

export {}
