"use client";
import React, { useState, useEffect } from "react";
import { Search } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface University {
  name: string;
  faculty: string;
  city: string;
  website: string;
}

export default function FacultySearch() {
  const [query, setQuery] = useState<string>("");
  const [reply, setReply] = useState<string>("");
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const [countries, setCountries] = useState<string[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<string>("");
  const [selectedCity, setSelectedCity] = useState<string>("");

  // 🧹 Clean and parse comma/line-separated lists safely
  const parseTextList = (text: string): string[] =>
    text
      .split(/,|\n|;/)
      .map((item) =>
        item
          .replace(/^\s*[\d\-*•]+\s*/, "") // remove bullet symbols and numbering
          .replace(/\(.*?\)/g, "") // remove parentheses text
          .trim()
      )
      .filter(
        (item) =>
          item &&
          !/^(here|list|countries|cities|major|of|the|world)/i.test(item)
      );

  const parseUniversities = (text: string): University[] => {
    const lines = text.split("\n").filter(Boolean);
    const uniList: University[] = [];
    lines.forEach((line) => {
      const match = line.match(
        /\*\*(.+?)\*\*,\s*(.+?),\s*(.+?),\s*(https?:\/\/[^\s]+)/
      );
      if (match) {
        uniList.push({
          name: match[1].trim(),
          faculty: match[2].trim(),
          city: match[3].trim(),
          website: match[4].trim(),
        });
      }
    });
    return uniList;
  };

  const fetchCountries = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/faculty-agent`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: "List all countries of the world." }),
        }
      );
      const data = await res.json();
      if (data.reply && typeof data.reply === "string") {
        const cleanText = data.reply
          .replace(/here('|’)s a list.*:?/i, "")
          .replace(/list of countries.*:?/i, "")
          .replace(/countries:?/i, "")
          .replace(/okay[,.]?/i, "")
          .trim();
        setCountries(parseTextList(cleanText));
      }
    } catch (err) {
      console.error("Error fetching countries:", err);
    }
  };

  const fetchCities = async (country: string) => {
    if (!country) return;
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/faculty-agent`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: `List major cities in ${country}.` }),
        }
      );
      const data = await res.json();
      if (data.reply && typeof data.reply === "string") {
        const cleanText = data.reply
          .replace(/here('|’)s a list.*:?/i, "")
          .replace(/list of major cities.*:?/i, "")
          .replace(/major cities in.*:?/i, "")
          .replace(/cities:?/i, "")
          .replace(/okay[,.]?/i, "")
          .trim();
        setCities(parseTextList(cleanText));
      }
    } catch (err) {
      console.error("Error fetching cities:", err);
    }
  };

  useEffect(() => {
    fetchCountries();
  }, []);

  useEffect(() => {
    setSelectedCity("");
    if (selectedCountry) fetchCities(selectedCountry);
    else setCities([]);
  }, [selectedCountry]);

  const handleSearch = async () => {
    if (!query.trim() && !selectedCountry) return;
    setLoading(true);
    setReply("");
    setUniversities([]);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/faculty-agent`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: query,
            country: selectedCountry,
            city: selectedCity,
          }),
        }
      );
      const data = await res.json();
      setReply(data.reply || "No response received.");
      if (data.reply) setUniversities(parseUniversities(data.reply));
    } catch (err) {
      console.error("Error fetching universities:", err);
      setReply("Failed to connect to AI agent.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto mt-10 p-6 bg-white rounded-2xl shadow-lg border border-gray-200">
      <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">
        🎓 Find Universities by Country, City & Faculty
      </h2>

      {/* ✅ Responsive Country & City Row */}
      <div className="flex flex-col sm:flex-row gap-3 mb-4 w-full">
        <div className="w-full sm:w-1/2">
          <select
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="w-full max-w-full p-3 border border-gray-300 rounded-xl text-gray-700 focus:ring-2 focus:ring-blue-400 focus:outline-none bg-gray-50 overflow-hidden text-ellipsis"
          >
            <option value="">Select Country</option>
            {countries.map((country, idx) => (
              <option key={idx} value={country}>
                {country}
              </option>
            ))}
          </select>
        </div>

        <div className="w-full sm:w-1/2">
          <select
            value={selectedCity}
            onChange={(e) => setSelectedCity(e.target.value)}
            disabled={!selectedCountry}
            className="w-full max-w-full p-3 border border-gray-300 rounded-xl text-gray-700 focus:ring-2 focus:ring-blue-400 focus:outline-none bg-gray-50 overflow-hidden text-ellipsis"
          >
            <option value="">Select City</option>
            {cities.map((city, idx) => (
              <option key={idx} value={city}>
                {city}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Faculty Search Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3 mb-6">
        <div className="relative flex-grow">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search faculty e.g. Computer Science, Engineering, Business..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl text-gray-700 focus:ring-2 focus:ring-blue-400 focus:outline-none bg-gray-50"
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
        </div>

        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-6 py-3 text-white rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 transition disabled:bg-blue-300"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {/* Results */}
      {universities.length > 0 ? (
        <div className="grid sm:grid-cols-2 gap-4">
          {universities.map((uni, idx) => (
            <div
              key={idx}
              className="p-4 border rounded-xl shadow-sm hover:shadow-md transition bg-gray-50"
            >
              <h3 className="font-semibold text-lg text-gray-800">
                {uni.name}
              </h3>
              <p className="text-gray-600">{uni.faculty}</p>
              <p className="text-gray-500">{uni.city}</p>
              {uni.website && (
                <a
                  href={uni.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline mt-1 inline-block"
                >
                  Visit Website
                </a>
              )}
            </div>
          ))}
        </div>
      ) : (
        reply &&
        !loading && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-xl text-gray-800">
            <ReactMarkdown
              components={{
                a: ({ node, ...props }) => (
                  <a
                    {...props}
                    className="text-blue-600 underline hover:text-blue-800 break-words"
                    target="_blank"
                    rel="noopener noreferrer"
                  />
                ),
              }}
            >
              {reply}
            </ReactMarkdown>
          </div>
        )
      )}

      {!reply && !loading && (
        <p className="text-center text-gray-400 mt-4 text-sm">
          Start by selecting a country and typing your faculty name 🌐
        </p>
      )}
    </div>
  );
}
