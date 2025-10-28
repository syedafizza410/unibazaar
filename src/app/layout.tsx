import "./globals.css";
import Navbar from "../../components/navbar";
import Footer from "../../components/footer";

export const metadata = {
  title: "UniBazaar | Find the Best University in Pakistan",
  description: "Discover top Pakistani universities by faculty, fees, and location.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-800">
        <Navbar />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
