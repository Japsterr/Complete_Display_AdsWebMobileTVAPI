import { DeviceTabletIcon, BoltIcon } from "@heroicons/react/24/outline";
import { useNavigate } from "react-router-dom";

function isRecentHeartbeat(last_heartbeat: string) {
  if (!last_heartbeat) return false;
  const last = new Date(last_heartbeat).getTime();
  const now = Date.now();
  return now - last < 5 * 60 * 1000;
}

export default function DisplayCard({ display }: { display: any }) {
  const navigate = useNavigate();
  const heartbeatRecent = isRecentHeartbeat(display.last_heartbeat);

  return (
    <div className="rounded-lg shadow-sm bg-white dark:bg-slate-800 p-6 flex flex-col gap-2">
      <div className="flex items-center gap-3 mb-2">
        <DeviceTabletIcon className="h-6 w-6 text-indigo-600" />
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{display.display_name}</h3>
      </div>
      <div className="text-sm text-slate-500 dark:text-slate-400 mb-2">{display.location}</div>
      <div className="flex items-center gap-2 mb-2">
        <span className="flex items-center gap-1">
          <span
            className={`h-3 w-3 rounded-full ${
              heartbeatRecent ? "bg-green-500 animate-pulse" : "bg-red-500"
            }`}
          ></span>
          <span className="text-xs text-slate-600 dark:text-slate-300">Heartbeat</span>
        </span>
        <BoltIcon className="h-4 w-4 text-slate-400" />
      </div>
      <div className="text-sm text-slate-700 dark:text-slate-200 mb-4">
        Default Campaign: <span className="font-medium">{display.default_campaign}</span>
      </div>
      <button
        className="rounded-lg bg-slate-200 text-slate-800 hover:bg-slate-300 px-4 py-2 font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200 ease-in-out"
        onClick={() => navigate(`/displays/${display.id}`)}
      >
        Manage
      </button>
    </div>
  );
}
