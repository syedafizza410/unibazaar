"use client";

import { useState, useEffect } from "react";

interface Review {
  name: string;
  email: string;
  comment: string;
  date: string;
}

export default function ReviewSection() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(true);

  const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL + "/reviews"; // ⬅️ Full backend URL

  // ---------- Fetch Reviews from Backend ----------
  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const res = await fetch(BACKEND_URL);
        if (!res.ok) throw new Error("Failed to fetch reviews");
        const data = await res.json();
        setReviews(data);
      } catch (err) {
        console.error("Error fetching reviews:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchReviews();
  }, []);

  // ---------- Submit Review ----------
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !comment) return;

    const newReview: Review = {
      name,
      email,
      comment,
      date: new Date().toISOString().split("T")[0],
    };

    try {
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newReview),
      });
      if (!res.ok) throw new Error("Failed to submit review");
      const savedReview = await res.json();
      setReviews([savedReview, ...reviews]);
      setName("");
      setEmail("");
      setComment("");
    } catch (err) {
      console.error("Error submitting review:", err);
    }
  };

  return (
    <div className="mt-8 p-6 rounded-xl shadow-md max-w-2xl mx-auto bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
      <h2 className="text-2xl font-bold mb-4">Student Reviews</h2>

      {/* Review Form */}
      <form onSubmit={handleSubmit} className="mb-6 flex flex-col gap-3">
        <input
          type="text"
          placeholder="Your Name"
          className="p-2 rounded border border-white bg-transparent placeholder-white text-white"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Your Email"
          className="p-2 rounded border border-white bg-transparent placeholder-white text-white"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <textarea
          placeholder="Your Review"
          className="p-2 rounded border border-white bg-transparent placeholder-white text-white"
          rows={3}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          required
        ></textarea>
        <button
          type="submit"
          className="bg-white text-indigo-600 font-semibold py-2 rounded hover:bg-gray-100 transition"
        >
          Submit Review
        </button>
      </form>

      {/* Reviews List */}
      <div className="flex flex-col gap-4">
        {loading ? (
          <p>Loading reviews...</p>
        ) : reviews.length === 0 ? (
          <p>No reviews yet. Be the first to review!</p>
        ) : (
          reviews.map((r, idx) => (
            <div key={idx} className="p-3 rounded shadow-sm border border-white bg-white text-gray-800">
              <p className="text-md text-gray-900">
                <span className="font-bold text-lg bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Name: </span>{r.name} <br />
                <span className="font-bold text-lg bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Review:</span> {r.comment} <br />
                <span className="font-bold text-lg bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Date: </span>{r.date}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
