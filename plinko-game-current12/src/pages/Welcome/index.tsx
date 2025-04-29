import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { LanguageSwitcher } from 'components/LanguageSwitcher'

export function Welcome() {
  const { t } = useTranslation()
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-between bg-[#1E2329] px-4 py-8">
      {/* Верхний логотип */}
      <div className="w-full">
        <img src="/plinko-logo.svg" alt="Plinko" className="h-8 w-auto" />
      </div>

      {/* Центральный контент */}
      <div className="flex w-full flex-col items-center gap-6">
        <h1 className="text-4xl font-bold text-white">PLINKO</h1>
        <div className="flex w-full max-w-md flex-col items-center gap-4">
          <h2 className="text-xl font-medium text-white">
            {t('selectLanguage')}
          </h2>
          <LanguageSwitcher />
        </div>
        <button
          onClick={() => navigate('/games/plinko')}
          className="mt-4 w-full max-w-[200px] rounded-lg bg-[#8B5CF6] px-8 py-3 text-xl font-bold text-white transition-colors hover:bg-[#7C3AED] active:bg-[#6D28D9]"
        >
          {t('play')}
        </button>
      </div>

      {/* Нижний логотип */}
      <div className="w-full">
        <img
          src="/plinko-logo.svg"
          alt="Plinko"
          className="h-8 w-auto opacity-50"
        />
      </div>
    </div>
  )
}
