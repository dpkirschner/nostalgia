import { useState, type ReactNode } from "react";
import { MapCanvas } from "../map/MapCanvas";
import { Logo } from "../ui/Logo";
import { PrimaryFAB } from "../ui/PrimaryFAB";
import { BottomDrawer } from "../ui/BottomDrawer";

interface AppLayoutProps {
  drawerContent?: ReactNode;
}

export function AppLayout({ drawerContent }: AppLayoutProps) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="relative h-screen w-screen overflow-hidden">
      <MapCanvas />

      <Logo />

      <PrimaryFAB onPress={() => setDrawerOpen(true)} />

      <BottomDrawer
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        title="What used to be here?"
      >
        {drawerContent || (
          <div className="space-y-4">
            <p className="text-gray-700 dark:text-gray-300">
              Results will appear here...
            </p>
            <div className="space-y-2">
              {Array.from({ length: 20 }).map((_, i) => (
                <p key={i} className="text-gray-600 dark:text-gray-400">
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed
                  do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                </p>
              ))}
            </div>
          </div>
        )}
      </BottomDrawer>
    </div>
  );
}
