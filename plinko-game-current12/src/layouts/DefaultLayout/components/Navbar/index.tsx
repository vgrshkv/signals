import plinkoLogo from '@images/logo.svg'
import { Link } from 'react-router-dom'
import { useGameStore } from 'store/game'
import { useAuthStore } from 'store/auth'
import { CurrencyDollarSimple } from 'phosphor-react'
import { Settings } from 'components/Settings'

export function Navbar() {
  const inGameBallsCount = useGameStore(state => state.gamesRunning)
  const telegramUser = useAuthStore(state => state.telegramUser)
  const currentBalance = useAuthStore(state => state.wallet.balance)

  return (
    <nav className="sticky top-0 z-50 bg-primary px-4 shadow-lg">
      <div
        // Возвращаем justify-between, чтобы ID отображался справа
        className="mx-auto flex h-16 w-full max-w-[1400px] items-center justify-between"
      >
        <Link to="/">
          <img src={plinkoLogo} alt="" className="w-32 md:w-40" />
        </Link>

        {/* Отображаем ID пользователя Telegram, если он есть */}
        {telegramUser && (
          <div className="flex items-center gap-4">
            <div className="text-xs font-bold text-text md:text-sm">
              TG ID: {telegramUser.id}
            </div>
            <div className="flex items-center gap-1 rounded-md bg-background px-3 py-1">
              <div className="rounded-full bg-purpleDark p-0.5">
                <CurrencyDollarSimple weight="bold" size={16} />
              </div>
              <span className="text-xs font-bold text-text md:text-sm">
                {currentBalance.toFixed(2)}
              </span>
            </div>
            <Settings />
          </div>
        )}
      </div>
    </nav>
  )
}
