import { CurrencyDollarSimple, X } from 'phosphor-react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { formatPoints } from 'utils/currencyFormat'

interface WalletCardProps {
  showFormatted?: boolean
  balance: number
}

function ZeroBalanceModal({
  isOpen,
  onClose
}: {
  isOpen: boolean
  onClose: () => void
}) {
  const { t } = useTranslation()
  if (!isOpen) return null
  const steps = t('zeroBalanceSteps', { returnObjects: true }) as string[]
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="relative w-full max-w-md rounded-lg bg-primary p-6 text-text">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-text hover:text-purple"
        >
          <X size={24} weight="bold" />
        </button>
        <h2 className="mb-4 text-xl font-bold">{t('zeroBalanceTitle')}</h2>
        <div className="mb-6 space-y-2">
          {steps && Array.isArray(steps)
            ? steps.map((step, idx) => (
                <p className="text-sm" key={idx}>
                  {step}
                </p>
              ))
            : null}
        </div>
        <div className="flex flex-col gap-2">
          <button
            onClick={() => window.open('https://t.me/PremiumBot', '_blank')}
            className="w-full rounded-md bg-yellow-500 px-4 py-2 font-bold text-white transition-colors hover:bg-yellow-600"
          >
            {t('goToPremiumBot')}
          </button>
          <button
            onClick={() =>
              window.Telegram?.WebApp?.openTelegramLink(
                'https://t.me/plinostar_bot?start=topup'
              )
            }
            className="w-full rounded-md bg-purple px-4 py-2 font-bold text-white transition-colors hover:bg-purpleDark"
          >
            {t('goToPlinoBot')}
          </button>
        </div>
        <div className="mt-4 text-center text-xs text-gray-400">
          @PremiumBot / @plinostar_bot
        </div>
      </div>
    </div>
  )
}

export function WalletCard({ balance, showFormatted }: WalletCardProps) {
  const currency = showFormatted ? formatPoints(balance) : balance
  const [isZeroBalanceModalOpen, setIsZeroBalanceModalOpen] = useState(false)
  return (
    <>
      <div
        className="flex cursor-pointer items-stretch"
        onClick={() => {
          if (balance === 0) setIsZeroBalanceModalOpen(true)
        }}
      >
        <div className="flex items-center gap-2 rounded-bl-md rounded-tl-md bg-background px-2 py-1 pr-4 font-bold uppercase text-white md:text-lg">
          <span className="rounded-full bg-purpleDark p-1">
            <CurrencyDollarSimple weight="bold" />
          </span>
          <span title={String(balance)}>{currency}</span>
        </div>
        <span
          title="Plinko Points"
          className="rounded-br-md rounded-tr-md bg-purpleDark p-2 font-bold text-white"
        >
          PP
        </span>
      </div>
      <ZeroBalanceModal
        isOpen={isZeroBalanceModalOpen}
        onClose={() => setIsZeroBalanceModalOpen(false)}
      />
    </>
  )
}
