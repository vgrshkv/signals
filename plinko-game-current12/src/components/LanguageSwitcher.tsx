import { useTranslation } from 'react-i18next'

const languages = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'ru', name: 'Русский', flag: '🇷🇺' },
  { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' },
  { code: 'pt', name: 'Português', flag: '🇧🇷' },
  { code: 'es', name: 'Español', flag: '🇪🇸' }
]

interface LanguageSwitcherProps {
  variant?: 'compact' | 'full'
}

export function LanguageSwitcher({ variant = 'full' }: LanguageSwitcherProps) {
  const { i18n } = useTranslation()

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng)
  }

  if (variant === 'compact') {
    return (
      <div className="flex w-full flex-col gap-1">
        {languages.map(lang => (
          <button
            key={lang.code}
            onClick={() => changeLanguage(lang.code)}
            className={`flex items-center justify-start gap-2 rounded-lg px-2 py-1.5 text-sm font-medium transition-all ${
              i18n.language === lang.code
                ? 'bg-[#8B5CF6] text-white'
                : 'text-white hover:bg-[#8B5CF6]/10'
            }`}
          >
            <span className="text-base">{lang.flag}</span>
            <span>{lang.name}</span>
          </button>
        ))}
      </div>
    )
  }

  return (
    <div className="grid w-full grid-cols-2 gap-2 sm:grid-cols-3">
      {languages.map(lang => (
        <button
          key={lang.code}
          onClick={() => changeLanguage(lang.code)}
          className={`flex items-center justify-center gap-2 rounded-lg border-2 px-3 py-2 text-sm font-medium transition-all ${
            i18n.language === lang.code
              ? 'border-[#8B5CF6] bg-[#8B5CF6] text-white'
              : 'border-[#8B5CF6] bg-transparent text-white hover:bg-[#8B5CF6]/10'
          }`}
        >
          <span className="text-base">{lang.flag}</span>
          <span>{lang.name}</span>
        </button>
      ))}
    </div>
  )
}
