export default function Footer() {
  return (
    <footer className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white mt-12">
      <div className="max-w-6xl mx-auto px-4 py-6 text-center text-sm">
        <p>© {new Date().getFullYear()} UniBazaar — All rights reserved.</p>
        <p className="text-indigo-200 mt-1">
          Built with ❤️ for students across World
        </p>
      </div>
    </footer>
  );
}
