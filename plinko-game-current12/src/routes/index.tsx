import { DefaultLayout } from 'layouts/DefaultLayout'
import { PlinkoGamePage } from 'pages/Games/Plinko'
import { Welcome } from 'pages/Welcome'
import { BrowserRouter, Routes as Switch, Route } from 'react-router-dom'

import { NotFound } from './components/NotFound'

export function Routes() {
  return (
    <BrowserRouter>
      <Switch>
        <Route element={<DefaultLayout />}>
          <Route path="/" element={<Welcome />} />
          <Route path="/games/plinko" element={<PlinkoGamePage />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Switch>
    </BrowserRouter>
  )
}
