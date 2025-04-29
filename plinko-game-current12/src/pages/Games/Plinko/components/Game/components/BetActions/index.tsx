import { CurrencyDollarSimple, Star } from 'phosphor-react'
import { ChangeEvent, useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from 'store/auth'
import toast from 'react-hot-toast'
import { DepositModal } from './components/DepositModal'
import { BuyPPsModal } from './components/DepositModal'

import { LinesType } from '../../@types'

interface PlinkoBetActions {
  onRunBet: (betValue: number) => void
  onChangeLines: (lines: LinesType) => void
  inGameBallsCount: number
}

export function BetActions({
  onRunBet,
  onChangeLines,
  inGameBallsCount
}: PlinkoBetActions) {
  const { t } = useTranslation()
  const currentBalance = useAuthStore(state => state.wallet.balance)
  const decrementCurrentBalance = useAuthStore(state => state.decrementBalance)
  const incrementCurrentBalance = useAuthStore(state => state.incrementBalance)
  const [betValue, setBetValue] = useState(0)
  const maxLinesQnt = 16
  const linesOptions: number[] = []
  for (let i = 8; i <= maxLinesQnt; i++) {
    linesOptions.push(i)
  }
  const [isDepositModalOpen, setIsDepositModalOpen] = useState(false)
  const [isBuyPPsModalOpen, setIsBuyPPsModalOpen] = useState(false)

  function handleChangeBetValue(e: ChangeEvent<HTMLInputElement>) {
    e.preventDefault()
    const value = +e.target.value
    const newBetValue = value >= currentBalance ? currentBalance : value
    setBetValue(newBetValue)
  }

  function handleChangeLines(e: ChangeEvent<HTMLSelectElement>) {
    onChangeLines(Number(e.target.value) as LinesType)
  }

  function handleHalfBet() {
    if (currentBalance <= 0) return
    const value = betValue / 2
    const newBetvalue = value <= 0 ? 0 : Math.floor(value)
    setBetValue(newBetvalue)
  }

  function handleDoubleBet() {
    if (currentBalance <= 0) return
    const value = betValue * 2

    if (value >= currentBalance) {
      setBetValue(currentBalance)
      return
    }

    const newBetvalue = value <= 0 ? 0 : Math.floor(value)
    setBetValue(newBetvalue)
  }

  function handleMaxBet() {
    if (currentBalance <= 0) return
    setBetValue(currentBalance)
  }

  async function handleRunBet() {
    if (currentBalance <= 0) {
      setIsDepositModalOpen(true)
      return
    }
    if (inGameBallsCount >= 15) return
    if (betValue > currentBalance) {
      setBetValue(currentBalance)
      return
    }
    if (betValue <= 0) return
    onRunBet(betValue)
    await decrementCurrentBalance(betValue)
  }

  // === Функции для работы с Telegram Stars - ТЕПЕРЬ ВНУТРИ КОМПОНЕНТА ===
  const handleBuyPPs = useCallback(
    async (amountPP: number, starsCost: number) => {
      //  useCallback
      if (window.Telegram && window.Telegram.WebApp) {
        const webApp = window.Telegram.WebApp
        const telegramUserId = useAuthStore.getState().telegramUser?.id //  убрали хук из тела

        if (!telegramUserId) {
          toast.error('Не удалось получить ID пользователя Telegram.')
          return
        }

        try {
          // === Вызываем API для создания счета (ЗАМЕНИ НА СВОЙ АДРЕС!) ===
          const response = await fetch('/api/create_invoice', {
            //  Замени на свой адрес (например, ngrok) + ИСПРАВЛЕН ПОРТ
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              user_id: telegramUserId,
              amount: starsCost, // Стоимость в звездах
              pp_amount: amountPP
            })
          })

          const data = await response.json()

          if (data && data.invoiceLink) {
            console.log('Invoice link received:', data.invoiceLink)
            webApp.openTelegramLink(data.invoiceLink) // Важно: openTelegramLink, не openInvoice
          } else {
            toast.error('Не удалось создать счет.')
            console.error('Failed to create invoice:', data)
          }
        } catch (error) {
          toast.error('Ошибка при создании счета.')
          console.error('Error creating invoice:', error)
        }
      } else {
        toast.error('Функция покупки доступна только в Telegram.')
        console.error('Telegram WebApp API not found for purchase.')
      }
    },
    []
  )

  return (
    <div className="relative h-1/2 w-full flex-1 px-4 py-8">
      <span className="absolute left-4 top-0 mx-auto text-xs font-bold text-text md:text-base">
        {t('ballsInGame')} {inGameBallsCount}/15
      </span>

      <div className="flex h-full flex-col gap-4 rounded-md bg-primary p-4 text-text md:justify-between">
        <div className="flex flex-col gap-2">
          <div className="flex flex-row items-stretch gap-1 md:flex-col">
            <div className="w-full text-sm font-bold md:text-base">
              <div className="flex flex-1 items-stretch justify-between">
                <span>{t('bet')}</span>
                <div className="flex items-center gap-1">
                  <div className="rounded-full bg-purpleDark p-0.5">
                    <CurrencyDollarSimple weight="bold" />
                  </div>
                  <span>{betValue.toFixed(2)}</span>
                </div>
              </div>
              <div className="flex items-stretch justify-center shadow-md">
                <input
                  type="number"
                  min={0}
                  max={currentBalance}
                  onChange={handleChangeBetValue}
                  value={betValue}
                  className="w-full rounded-bl-md rounded-tl-md border-2 border-secondary bg-background p-2.5 px-4 font-bold transition-colors placeholder:font-bold placeholder:text-text focus:border-purple focus:outline-none md:p-2"
                />
                <button
                  onClick={handleHalfBet}
                  className="relative border-2 border-transparent bg-secondary p-2.5 px-3 transition-colors after:absolute after:right-0 after:top-[calc(50%_-_8px)] after:h-4 after:w-0.5 after:rounded-lg after:bg-background after:content-[''] hover:bg-secondary/80 focus:border-purple focus:outline-none md:p-2"
                >
                  ½
                </button>
                <button
                  onClick={handleDoubleBet}
                  className="relative border-2 border-transparent bg-secondary p-2.5 px-3 transition-colors after:absolute after:right-0 after:top-[calc(50%_-_8px)] after:h-4 after:w-0.5 after:rounded-lg after:bg-background after:content-[''] hover:bg-secondary/80 focus:border-purple focus:outline-none md:p-2"
                >
                  2x
                </button>
                <button
                  onClick={handleMaxBet}
                  className="rounded-br-md rounded-tr-md border-2 border-transparent bg-secondary p-2 px-3 text-xs transition-colors hover:bg-secondary/80 focus:border-purple focus:outline-none"
                >
                  max
                </button>
              </div>
            </div>

            <button
              onClick={handleRunBet}
              className="block rounded-md bg-purple px-2 py-4 text-sm font-bold leading-none text-background transition-colors hover:bg-purpleDark focus:outline-none focus:ring-1 focus:ring-purple focus:ring-offset-1 focus:ring-offset-primary disabled:bg-gray-500 md:hidden"
            >
              {t('bet')}
            </button>
          </div>
          <select
            disabled={inGameBallsCount > 0}
            onChange={handleChangeLines}
            defaultValue={16}
            className="w-full rounded-md border-2 border-secondary bg-background px-4 py-2 font-bold transition-all placeholder:font-bold placeholder:text-text focus:border-purple focus:outline-none disabled:line-through disabled:opacity-80"
            id="lines"
          >
            {linesOptions.map(line => (
              <option key={line} value={line}>
                {line} {t('lines')}
              </option>
            ))}
          </select>
        </div>

        {/* === КНОПКИ ПОКУПКИ PPs === */}
        <div className="mt-4 flex flex-col gap-2">
          <button
            onClick={() => setIsDepositModalOpen(true)}
            className="flex w-full items-center justify-center gap-2 rounded-md bg-yellow-500 px-4 py-2 font-bold text-white transition-colors hover:bg-yellow-600"
          >
            <Star weight="fill" /> {t('deposit')}
          </button>
          <button
            onClick={() => setIsBuyPPsModalOpen(true)}
            className="flex w-full items-center justify-center gap-2 rounded-md bg-blue-500 px-4 py-2 font-bold text-white transition-colors hover:bg-blue-600"
          >
            <Star weight="fill" /> {t('buyPPs', { amount: 100, stars: 100 })}
          </button>
          <button
            onClick={() => setIsBuyPPsModalOpen(true)}
            className="flex w-full items-center justify-center gap-2 rounded-md bg-green-500 px-4 py-2 font-bold text-white transition-colors hover:bg-green-600"
          >
            <Star weight="fill" /> {t('buyPPs', { amount: 500, stars: 500 })}
          </button>
          <button
            onClick={() => setIsBuyPPsModalOpen(true)}
            className="bg-purple-500 hover:bg-purple-600 flex w-full items-center justify-center gap-2 rounded-md px-4 py-2 font-bold text-white transition-colors"
          >
            <Star weight="fill" /> {t('buyPPs', { amount: 1000, stars: 1000 })}
          </button>
        </div>
        {/* ========================== */}

        <button
          onClick={handleRunBet}
          className="hidden rounded-md bg-purple px-6 py-5 font-bold leading-none text-background transition-colors hover:bg-purpleDark focus:outline-none focus:ring-1 focus:ring-purple focus:ring-offset-1 focus:ring-offset-primary disabled:bg-gray-500 md:visible md:block"
        >
          {t('bet')}
        </button>
      </div>

      <DepositModal
        isOpen={isDepositModalOpen}
        onClose={() => setIsDepositModalOpen(false)}
      />
      <BuyPPsModal
        isOpen={isBuyPPsModalOpen}
        onClose={() => setIsBuyPPsModalOpen(false)}
      />
    </div>
  )
}
