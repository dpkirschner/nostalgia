import { ReactNode } from "react";

export interface MapCanvasProps {
  onIdle?: (bounds: unknown) => void;
  onReady?: (mapRef: unknown) => void;
}

export interface PrimaryFABProps {
  onPress: () => void;
}

export interface BottomDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title?: string;
  children: ReactNode;
}
