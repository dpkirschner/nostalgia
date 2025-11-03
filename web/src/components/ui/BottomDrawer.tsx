import * as Dialog from "@radix-ui/react-dialog";
import { type BottomDrawerProps } from "../../types/components";
import { cn } from "../../lib/utils";

export function BottomDrawer({
  open,
  onOpenChange,
  title,
  children,
}: BottomDrawerProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay
          className={cn(
            "fixed inset-0 z-20",
            "bg-black/50 backdrop-blur-sm",
            "data-[state=open]:animate-in data-[state=closed]:animate-out",
            "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
            "transition-all duration-250"
          )}
        />
        <Dialog.Content
          className={cn(
            "fixed z-20",
            "bottom-0 left-0 right-0",
            "md:left-1/2 md:-translate-x-1/2 md:max-w-[680px]",
            "bg-white dark:bg-gray-900",
            "rounded-t-2xl shadow-2xl",
            "max-h-[85vh] flex flex-col",
            "data-[state=open]:animate-in data-[state=closed]:animate-out",
            "data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom",
            "transition-all duration-200"
          )}
          aria-describedby={undefined}
        >
          {/* Drag handle area */}
          <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
            <div className="flex justify-center py-2">
              <div className="w-12 h-1 bg-gray-300 dark:bg-gray-700 rounded-full" />
            </div>
            {title && (
              <Dialog.Title className="px-4 pb-3 text-lg font-semibold text-gray-900 dark:text-gray-100">
                {title}
              </Dialog.Title>
            )}
          </div>

          {/* Scrollable body */}
          <div className="flex-1 overflow-y-auto p-4">{children}</div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
