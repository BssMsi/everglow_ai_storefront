// frontend/src/app/layout.tsx
import type { Metadata } from "next";
// Keep Inter font for default, but ThemeProvider will override body style
import { Inter, Roboto, Lato } from "next/font/google";
import "./globals.css";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { ThemeProvider } from "@/context/ThemeContext"; // Import ThemeProvider

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const roboto = Roboto({ subsets: ["latin"], weight: ['400', '700'], variable: "--font-roboto" });
const lato = Lato({ subsets: ["latin"], weight: ['400', '700'], variable: "--font-lato" });

export const metadata: Metadata = {
  title: "EverGlow",
  description: "Adaptive UI for a personalized skincare experience",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      {/* Apply font variables to html tag for Tailwind access if needed */}
      <body className={`${inter.variable} ${roboto.variable} ${lato.variable} relative min-h-screen pt-20 pb-16 overflow-x-hidden`}>
        <ThemeProvider> {/* Wrap with ThemeProvider */}
          <Header />
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
          {/* <Footer /> */}
        </ThemeProvider>
      </body>
    </html>
  );
}
