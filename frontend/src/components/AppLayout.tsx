import type { PropsWithChildren } from "react";

import { HeaderBar, type HeaderBarProps } from "./HeaderBar";

interface AppLayoutProps extends PropsWithChildren {
  headerProps: HeaderBarProps;
}

export function AppLayout({ headerProps, children }: AppLayoutProps): JSX.Element {
  return (
    <div className="page-layout">
      <HeaderBar {...headerProps} />
      <main className="page-content">{children}</main>
    </div>
  );
}
