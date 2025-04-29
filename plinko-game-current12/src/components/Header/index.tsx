import { useAuthStore } from 'store/auth'
import { Settings } from 'components/Settings'

export function Header() {
  const telegramUser = useAuthStore(state => state.telegramUser)

  return (
    <div className="flex w-full items-center justify-between bg-[#1E2329] px-4 py-2">
      <div className="flex items-center gap-2">
        <img src="/plinko-logo.svg" alt="Plinko" className="h-8 w-auto" />
      </div>
      <div className="flex items-center gap-4">
        <Settings />
        <div className="flex items-center gap-2 text-white">
          <span className="text-sm">TG ID: {telegramUser?.id || '-'}</span>
        </div>
      </div>
    </div>
  )
}
