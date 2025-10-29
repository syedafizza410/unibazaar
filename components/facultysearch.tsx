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

  const parseTextList = (text: string) =>
    text
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);

  const parseUniversities = (text: string): University[] => {
    const lines = text.split("\n").filter(Boolean);
    const uniList: University[] = [];
    lines.forEach((line) => {
      const match = line.match(
        /\*\*(.+?)\*\*,\s*🎓 Faculty:\s*(.+?),\s*🏙️ City:\s*(.+?),\s*🌐 Website: \[(?:.+?)\]\((https?:\/\/[^\s]+)\)/
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
        { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: "List all countries" }) }
      );
      const data = await res.json();
      if (data.reply) setCountries(parseTextList(data.reply));
    } catch (err) {
      console.error("Error fetching countries:", err);
    }
  };

  const fetchCities = async (country: string) => {
    if (!country) return setCities([]);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/faculty-agent`,
        { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: `List major cities in ${country}` }) }
      );
      const data = await res.json();
      if (data.reply) setCities(parseTextList(data.reply));
    } catch (err) {
      console.error("Error fetching cities:", err);
    }
  };

  useEffect(() => { fetchCountries(); }, []);

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

      {/* Country & City Select */}
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <select
          value={selectedCountry}
          onChange={(e) => setSelectedCountry(e.target.value)}
          className="w-full p-3 border rounded-xl bg-gray-50 text-gray-700"
        >
          <option value="">Select Country</option>
          {countries.map((c, i) => <option key={i} value={c}>{c}</option>)}
        </select>

        <select
          value={selectedCity}
          onChange={(e) => setSelectedCity(e.target.value)}
          disabled={!selectedCountry}
          className="w-full p-3 border rounded-xl bg-gray-50 text-gray-700"
        >
          <option value="">Select City</option>
          {cities.map((c, i) => <option key={i} value={c}>{c}</option>)}
        </select>
      </div>

      {/* Search Input */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-grow">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search faculty e.g. Computer Science, Business..."
            className="w-full pl-10 pr-4 py-3 border rounded-xl bg-gray-50 text-gray-700"
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-6 py-3 rounded-xl text-white bg-gradient-to-r from-indigo-600 to-purple-600 disabled:bg-blue-300"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {/* Results */}
      {universities.length > 0 ? (
        <div className="grid sm:grid-cols-2 gap-4">
          {universities.map((uni, idx) => (
            <div key={idx} className="p-4 border rounded-xl bg-gray-50">
              <h3 className="font-semibold text-lg text-gray-800">{uni.name}</h3>
              <p className="text-gray-600">{uni.faculty}</p>
              <p className="text-gray-500">{uni.city}</p>
              {uni.website && <a href={uni.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">{uni.website}</a>}
            </div>
          ))}
        </div>
      ) : reply && !loading ? (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-xl text-gray-800">
          <ReactMarkdown>{reply}</ReactMarkdown>
        </div>
      ) : (
        !reply && !loading && <p className="text-center text-gray-400">Start by selecting a country and typing your faculty name 🌐</p>
      )}
    </div>
  );
}
