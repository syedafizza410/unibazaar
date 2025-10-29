"use client";

import { useState } from "react";
import Hero from "../../components/hero";
import FacultySearch from "../../components/facultysearch";
import ReviewSection from "../../components/reviews";
import ChatAgent from "../../components/chatagent";

export default function Home() {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <div>
      <Hero setIsChatOpen={setIsChatOpen} />

      <FacultySearch />

      <ReviewSection />

      <ChatAgent open={isChatOpen} setOpen={setIsChatOpen} />
    </div>
  );
}
