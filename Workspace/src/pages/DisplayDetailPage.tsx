import { useEffect, useState } from "react";
import api from "../services/api.ts";
import { useParams } from "react-router-dom";

export default function DisplayDetailPage() {
  const { id } = useParams();
  const [display, setDisplay] = useState<any>(null);
  const [schedules, setSchedules] = useState<any[]>([]);
  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState("");
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [form, setForm] = useState({ campaign: "", start_datetime: "", end_datetime: "" });

  useEffect(() => {
    api.get(`/displays/${id}/`).then(res => setDisplay(res.data));
    api.get(`/schedules/?display=${id}`).then(res => setSchedules(res.data));
  }, [id]);

  function handleChangeCampaign() {
    api.get("/campaigns/").then(res => setCampaigns(res.data));
    setShowCampaignModal(true);
  }

  function handleSetDefaultCampaign() {
    api.post(`/displays/${id}/set_default_campaign/`, { campaign: selectedCampaign }).then(() => {
      setDisplay((d: any) => ({ ...d, default_campaign: selectedCampaign }));
      setShowCampaignModal(false);
    });
  }

  function handleDeleteSchedule(scheduleId: string) {
    api.delete(`/schedules/${scheduleId}/`).then(() => {
      setSchedules(s => s.filter(sch => sch.id !== scheduleId));
    });
  }

  function handleCreateSchedule(e: React.FormEvent) {
    e.preventDefault();
    api.post("/schedules/", { ...form, display: id }).then(res => {
      setSchedules(s => [...s, res.data]);
      setShowScheduleForm(false);
      setForm({ campaign: "", start_datetime: "", end_datetime: "" });
    });
  }

  return (
    <div>
      {display && (
        <>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">{display.display_name}</h1>
          <div className="text-slate-500 dark:text-slate-400 mb-6">{display.location}</div>
          {/* Default Campaign Section */}
          <div className="mb-8">
            <div className="flex items-center gap-4">
              <span className="text-lg text-slate-700 dark:text-slate-200">
                Default Campaign: <span className="font-semibold">{display.default_campaign}</span>
              </span>
              <button
                className="rounded-lg bg-slate-200 text-slate-800 hover:bg-slate-300 px-4 py-2 font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200 ease-in-out"
                onClick={handleChangeCampaign}
              >
                Change
              </button>
            </div>
            {showCampaignModal && (
              <div className="fixed inset-0 z-50 flex items-center justify-center">
                <div className="absolute inset-0 bg-black bg-opacity-40" onClick={() => setShowCampaignModal(false)}></div>
                <div className="relative bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 w-full max-w-md">
                  <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Select Default Campaign</h2>
                  <select
                    className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-700 text-slate-900 dark:text-white px-4 py-2 mb-4"
                    value={selectedCampaign}
                    onChange={e => setSelectedCampaign(e.target.value)}
                  >
                    <option value="">Select a campaign</option>
                    {campaigns.map(c => (
                      <option key={c.id} value={c.name}>{c.name}</option>
                    ))}
                  </select>
                  <button
                    className="w-full rounded-lg bg-indigo-600 text-white font-semibold py-2 mt-2 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200 ease-in-out"
                    onClick={handleSetDefaultCampaign}
                  >
                    Set Default
                  </button>
                </div>
              </div>
            )}
          </div>
          {/* Schedules Section */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Scheduled Overrides</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {schedules.map(sch => (
                <div key={sch.id} className="rounded-lg shadow-sm bg-white dark:bg-slate-800 p-6 flex flex-col gap-2">
                  <div className="text-slate-700 dark:text-slate-200">
                    Playing <span className="font-semibold">{sch.campaign_name}</span> from <span className="font-semibold">{sch.start_datetime}</span> to <span className="font-semibold">{sch.end_datetime}</span>
                  </div>
                  <button
                    className="rounded-lg bg-slate-200 text-slate-800 hover:bg-slate-300 px-4 py-2 font-semibold mt-2 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200 ease-in-out"
                    onClick={() => handleDeleteSchedule(sch.id)}
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          </div>
          {/* Add Schedule UI */}
          <div>
            <button
              className="rounded-lg bg-indigo-600 text-white font-semibold px-6 py-2 mb-4 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200 ease-in-out"
              onClick={() => setShowScheduleForm(true)}
            >
              Create Schedule
            </button>
            {showScheduleForm && (
              <form className="bg-white dark:bg-slate-800 rounded-xl shadow-md p-6 max-w-md" onSubmit={handleCreateSchedule}>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
                  Campaign
                </label>
                <select
                  className="block w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-700 text-slate-900 dark:text-white px-4 py-2 mb-4"
                  value={form.campaign}
                  onChange={e => setForm(f => ({ ...f, campaign: e.target.value }))}
                  required
                >
                  <option value="">Select a campaign</option>
                  {campaigns.map(c => (
                    <option key={c.id} value={c.name}>{c.name}</option>
                  ))}
                </select>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
                  Start Date/Time
                </label>
                <input
                  type="datetime-local"
                  className="block w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-700 text-slate-900 dark:text-white px-4 py-2 mb-4"
                  value={form.start_datetime}
                  onChange={e => setForm(f => ({ ...f, start_datetime: e.target.value }))}
                  required
                />
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
                  End Date/Time
                </label>
                <input
                  type="datetime-local"
                  className="block w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-700 text-slate-900 dark:text-white px-4 py-2 mb-4"
                  value={form.end_datetime}
                  onChange={e => setForm(f => ({ ...f, end_datetime: e.target.value }))}
                  required
                />
                <button
                  type="submit"
                  className="w-full rounded-lg bg-indigo-600 text-white font-semibold py-2 mt-2 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200 ease-in-out"
                >
                  Save Schedule
                </button>
              </form>
            )}
          </div>
        </>
      )}
    </div>
  );
}
