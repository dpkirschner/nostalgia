import * as VisuallyHidden from '@radix-ui/react-visually-hidden'
import { cn } from '../../lib/utils'

export function Logo() {
  return (
    <div
      className={cn(
        'absolute top-0 left-0 z-10',
        'p-3 sm:p-4',
        'backdrop-blur-sm bg-white/80 dark:bg-gray-900/80',
        'rounded-br-2xl',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2',
        'cursor-pointer'
      )}
      tabIndex={0}
      role="banner"
    >
      <VisuallyHidden.Root>What Used To Be Here, home</VisuallyHidden.Root>
      <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">
        Nostalgia
      </h1>
    </div>
  )
}
