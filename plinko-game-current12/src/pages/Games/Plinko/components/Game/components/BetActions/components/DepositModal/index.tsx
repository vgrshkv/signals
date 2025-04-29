import { X } from 'phosphor-react'
import { useTranslation } from 'react-i18next'

interface BuyPPsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function BuyPPsModal({ isOpen, onClose }: BuyPPsModalProps) {
  const { t } = useTranslation()
  if (!isOpen) return null
  const steps = t('buyPPsSteps', { returnObjects: true }) as string[]
  const goToBot = () => {
    window.Telegram?.WebApp?.openTelegramLink('https://t.me/plinostar_bot')
    onClose()
  }
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="relative w-full max-w-md rounded-lg bg-primary p-6 text-text">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-text hover:text-purple"
        >
          <X size={24} weight="bold" />
        </button>
        <h2 className="mb-4 text-xl font-bold">{t('buyPPsTitle')}</h2>
        <div className="mb-6 space-y-2">
          {steps && Array.isArray(steps)
            ? steps.map((step, idx) => (
                <p className="text-sm" key={idx}>
                  {step}
                </p>
              ))
            : null}
        </div>
        <button
          onClick={goToBot}
          className="w-full rounded-md bg-purple px-4 py-2 font-bold text-white transition-colors hover:bg-purpleDark"
        >
          {t('goToBot')}
        </button>
      </div>
    </div>
  )
}

// Восстанавливаю старую DepositModal для пополнения баланса
interface DepositModalProps {
  isOpen: boolean
  onClose: () => void
}

export function DepositModal({ isOpen, onClose }: DepositModalProps) {
  if (!isOpen) return null
  const handleOpenBot = () => {
    window.open('https://t.me/PremiumBot', '_blank')
  }
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="relative w-full max-w-md rounded-lg bg-primary p-6 text-text">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-text hover:text-purple"
        >
          <X size={24} weight="bold" />
        </button>
        <h2 className="mb-4 text-xl font-bold">Пополнение баланса</h2>
        <div className="mb-6 space-y-4">
          <p className="text-sm">1. Перейдите в бота @PremiumBot</p>
          <p className="text-sm">2. Выполните команду /start</p>
          <p className="text-sm">3. Выполните команду /stars</p>
          <p className="text-sm">
            4. Следуйте инструкциям бота для пополнения баланса
          </p>
        </div>
        <button
          onClick={handleOpenBot}
          className="w-full rounded-md bg-purple px-4 py-2 font-bold text-white transition-colors hover:bg-purpleDark"
        >
          Перейти в бота
        </button>
      </div>
    </div>
  )
}
