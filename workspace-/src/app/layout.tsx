import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Dragon Arena — Sparking! ZERO-style Combat Demo",
  description: "A playable Dragon Ball arena fighter demo: Sparking! ZERO-style combat, canon power levels with the log-scaled combat-ratio damage formula, and Noea-style transformation progression. Built from the Dragon Ball Game Design Blueprint.",
  keywords: ["Dragon Ball", "Sparking Zero", "arena fighter", "power levels", "fighting game", "canon power scaling", "Dragon Block Noea", "combat demo"],
  authors: [{ name: "Z.ai" }],
  icons: {
    icon: "https://z-cdn.chatglm.cn/z-ai/static/logo.svg",
  },
  openGraph: {
    title: "Dragon Arena — Sparking! ZERO-style Combat Demo",
    description: "Canon power levels + Noea-style progression + Sparking! ZERO-style combat, in a playable browser demo.",
    siteName: "Dragon Arena",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Dragon Arena",
    description: "Sparking! ZERO-style Dragon Ball combat demo with canon power levels.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
