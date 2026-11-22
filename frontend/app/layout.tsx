import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {title: "ZU Assistant", description: "دستیار هوشمند دانشجویان دانشگاه زنجان"};

export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) {
  return <html lang="fa" dir="rtl"><body>{children}</body></html>;
}
