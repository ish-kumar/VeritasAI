import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Space_Grotesk } from "next/font/google";
import "./globals.css";
import Navigation from "@/components/Navigation";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/sonner";

// Primary font for body text - modern, geometric, professional
const plusJakarta = Plus_Jakarta_Sans({ 
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-plus-jakarta",
});

// Display font for headings - distinctive, modern
const spaceGrotesk = Space_Grotesk({ 
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-space-grotesk",
});

export const metadata: Metadata = {
  title: "Veritas AI - Multi-Agent Legal Research",
  description: "Adversarial multi-agent RAG with citation verification, confidence scoring, and risk assessment for legal professionals",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${plusJakarta.variable} ${spaceGrotesk.variable}`} suppressHydrationWarning>
      <body className={plusJakarta.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          <Navigation />
          
          {/* Main content with padding for fixed nav */}
          <main className="pt-16">{children}</main>

          {/* Global Toast Notifications */}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
