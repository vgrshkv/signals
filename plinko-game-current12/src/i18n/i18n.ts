import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en.json';
import ru from './locales/ru.json';
import hi from './locales/hi.json';
import pt from './locales/pt.json';
import es from './locales/es.json';

const resources = {
  en: {
    translation: en,
  },
  ru: {
    translation: ru,
  },
  hi: {
    translation: hi,
  },
  pt: {
    translation: pt,
  },
  es: {
    translation: es,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n; 