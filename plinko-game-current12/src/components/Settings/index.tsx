import { useState } from 'react'
import { Gear } from 'phosphor-react'
import { Dialog } from '@headlessui/react'
import { useGameStore } from 'store/game'

export function Settings() {
  const [isOpen, setIsOpen] = useState(false)
  const { soundEnabled, setSoundEnabled } = useGameStore(state => ({
    soundEnabled: state.soundEnabled,
    setSoundEnabled: state.setSoundEnabled
  }))

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="rounded-full bg-background p-2 transition-colors hover:bg-background/80"
      >
        <Gear size={20} weight="bold" className="text-text" />
      </button>

      <Dialog
        open={isOpen}
        onClose={() => setIsOpen(false)}
        className="relative z-50"
      >
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />

        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="mx-auto w-full max-w-sm rounded-lg bg-primary p-6">
            <Dialog.Title className="text-lg font-medium text-text">
              Settings
            </Dialog.Title>

            <div className="mt-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={soundEnabled}
                  onChange={e => setSoundEnabled(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-purpleDark focus:ring-purpleDark"
                />
                <span className="text-sm text-text">Enable sound effects</span>
              </label>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setIsOpen(false)}
                className="rounded-md bg-purpleDark px-4 py-2 text-sm font-medium text-white hover:bg-purpleDark/80"
              >
                Close
              </button>
            </div>
          </Dialog.Panel>
        </div>
      </Dialog>
    </>
  )
}
