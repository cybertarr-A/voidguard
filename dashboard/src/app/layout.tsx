import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VOIDGUARD | Autonomous Security",
  description: "Enterprise cyber defense AI platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
