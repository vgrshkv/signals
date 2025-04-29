import { Link } from 'react-router-dom'
import { Play } from 'phosphor-react'

export function ScoreBoardPage() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-4">
      <div className="flex w-4/5 flex-col gap-3 rounded bg-primary p-4 text-text">
        <div className="rounded-md bg-background p-1 text-center text-2xl">
          <strong>Scoreboard отключен</strong>
          <br />
          <span className="text-xs">
            Функциональность scoreboard отключена в этой версии.
          </span>
        </div>
      </div>
      <Link
        to="/plinko"
        className="mb-4 flex items-center justify-center gap-4 rounded-lg bg-purpleDark p-4 text-lg font-bold text-text shadow-md transition-colors hover:bg-purple"
      >
        <Play weight="fill" size="20" />
        JOGAR
      </Link>
    </div>
  )
}