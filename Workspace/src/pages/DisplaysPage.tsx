import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api.ts";
import DisplayCard from "../components/DisplayCard.tsx";

export default function DisplaysPage() {
  const [displays, setDisplays] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/displays/").then(res => {
      setDisplays(res.data);
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-8">Your Displays</h1>
      <button
        className="rounded-lg bg-indigo-600 text-white font-semibold px-6 py-2 mb-8 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200 ease-in-out"
        onClick={() => navigate("/displays/new")}
      >
        Register New Display
      </button>
      {loading ? (
        <div className="text-slate-500">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {displays.map(display => (
            <DisplayCard key={display.id} display={display} />
          ))}
        </div>
      )}
    </div>
  );
}
