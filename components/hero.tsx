"use client";
import { motion } from "framer-motion";

interface HeroProps {
  setIsChatOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

export default function Hero({ setIsChatOpen }: HeroProps) {
  return (
    <section className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-20">
      <div className="max-w-6xl mx-auto px-6 text-center">
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-4xl md:text-6xl font-bold mb-4"
        >
          Find the Best <span className="text-yellow-300">University</span> for You 🎓
        </motion.h1>
        <p className="text-lg text-indigo-100 mb-8">
          Explore top universities in World — choose by faculty, fees, and city.
        </p>

        <motion.button
          onClick={() => setIsChatOpen(true)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="bg-gradient-to-r from-white via-gray-100 to-white text-indigo-600 font-semibold px-6 py-3 rounded-full shadow-lg hover:from-yellow-300 hover:to-yellow-200 transition-all duration-300"
        >
          Explore Now
        </motion.button>
      </div>
    </section>
  );
}
