import { Navbar } from 'layouts/DefaultLayout/components/Navbar'
import { Outlet } from 'react-router-dom'

import { Footer } from './components/Footer'

export function DefaultLayout() {
  return (
    <div className="relative flex min-h-screen w-full flex-col justify-between bg-background">
      <Navbar />
      <div className="flex h-full w-full max-w-[1400px] flex-1 overflow-auto overflow-x-hidden pt-4 lg:mx-auto">
        <div className="flex-1">
          {' '}
          <Outlet />{' '}
        </div>
      </div>
      <Footer />
    </div>
  )
}
