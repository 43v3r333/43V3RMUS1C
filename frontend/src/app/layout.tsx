"""
Root layout component
*/
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { Providers } from "./providers"
import "./globals.css"

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" })

export const metadata: Metadata = {
  title: "43V3R CORE - Autonomous Media Operating System",
  description: "Enterprise-grade AI-native media and music operating system",
  icons: {
    icon: [
      {
        url: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%230ea5e9' width='100' height='100' rx='20'/><text y='.9em' font-size='60' fill='white' x='50%' text-anchor='middle'>43</text></svg>",
        type: "image/svg+xml",
      },
    ],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.variable}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}