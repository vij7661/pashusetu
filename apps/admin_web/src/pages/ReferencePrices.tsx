import { FormEvent, useEffect, useState } from "react";
import { get, post, put } from "../api";

type ReferencePrice = {
  recommendation_id: string;
  market_code: string;
  breed: string | null;
  price_per_kg_paise: number;
  source_label: string;
  valid_from: string;
  valid_to: string | null;
  active: boolean;
};

function toLocalInput(date = new Date()) {
  const offset = date.getTimezoneOffset();
  return new Date(date.getTime() - offset * 60_000).toISOString().slice(0, 16);
}

export default function ReferencePrices() {
  const [rows, setRows] = useState<ReferencePrice[]>([]);
  const [editing, setEditing] = useState<ReferencePrice | null>(null);
  const [marketCode, setMarketCode] = useState("HYDERABAD");
  const [breed, setBreed] = useState("");
  const [priceRupees, setPriceRupees] = useState("");
  const [sourceLabel, setSourceLabel] = useState("");
  const [effectiveFrom, setEffectiveFrom] = useState(toLocalInput());
  const [validTo, setValidTo] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function load() {
    const data = await get<ReferencePrice[]>("/marketplace/admin/references");
    setRows(data);
  }

  useEffect(() => {
    load().catch((error) => setMessage(error?.response?.data?.message || String(error)));
  }, []);

  function reset() {
    setEditing(null);
    setMarketCode("HYDERABAD");
    setBreed("");
    setPriceRupees("");
    setSourceLabel("");
    setEffectiveFrom(toLocalInput());
    setValidTo("");
  }

  function beginEdit(row: ReferencePrice) {
    setEditing(row);
    setMarketCode(row.market_code);
    setBreed(row.breed || "");
    setPriceRupees((row.price_per_kg_paise / 100).toFixed(2));
    setSourceLabel(row.source_label);
    setEffectiveFrom(toLocalInput());
    setValidTo("");
    setMessage("Editing creates a new reference version; historical listings keep the old version.");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const pricePerKgPaise = Math.round(Number(priceRupees) * 100);
      if (!Number.isFinite(pricePerKgPaise) || pricePerKgPaise <= 0) {
        throw new Error("Enter a valid positive reference price.");
      }
      const common = {
        market_code: marketCode.trim().toUpperCase(),
        breed: breed.trim() || null,
        price_per_kg_paise: pricePerKgPaise,
        source_label: sourceLabel.trim(),
        valid_to: validTo ? new Date(validTo).toISOString() : null,
      };
      if (editing) {
        await put(`/marketplace/admin/references/${editing.recommendation_id}`, {
          ...common,
          effective_from: new Date(effectiveFrom).toISOString(),
        });
        setMessage("Reference price updated as a new version.");
      } else {
        await post("/marketplace/admin/references", {
          ...common,
          valid_from: new Date(effectiveFrom).toISOString(),
        });
        setMessage("Reference price created.");
      }
      reset();
      await load();
    } catch (error: any) {
      setMessage(error?.response?.data?.message || error?.message || String(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <h1>Reference Prices</h1>
      <p>Admin-curated pilot references only. These are evidence-backed references, not calculated market averages.</p>

      <form onSubmit={submit} className="card">
        <h3>{editing ? "Create edited version" : "Create reference price"}</h3>
        <label>Market / area</label>
        <input value={marketCode} onChange={(e) => setMarketCode(e.target.value)} required />
        <label>Breed / category (optional)</label>
        <input value={breed} onChange={(e) => setBreed(e.target.value)} />
        <label>Reference price ₹ / kg</label>
        <input type="number" min="0.01" step="0.01" value={priceRupees} onChange={(e) => setPriceRupees(e.target.value)} required />
        <label>Evidence / source note</label>
        <input value={sourceLabel} onChange={(e) => setSourceLabel(e.target.value)} required minLength={3} />
        <label>{editing ? "New version effective from" : "Effective from"}</label>
        <input type="datetime-local" value={effectiveFrom} onChange={(e) => setEffectiveFrom(e.target.value)} required />
        <label>Expiry (optional)</label>
        <input type="datetime-local" value={validTo} onChange={(e) => setValidTo(e.target.value)} />
        <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
          <button className="btn" disabled={busy}>{busy ? "Saving…" : editing ? "Save new version" : "Create reference"}</button>
          {editing && <button type="button" className="btn secondary" onClick={reset}>Cancel</button>}
        </div>
      </form>

      {message && <p>{message}</p>}

      <div className="card">
        <h3>Reference history</h3>
        <table>
          <thead>
            <tr><th>Market</th><th>Breed</th><th>₹/kg</th><th>Source</th><th>Effective</th><th>Status</th><th /></tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.recommendation_id}>
                <td>{row.market_code}</td>
                <td>{row.breed || "All"}</td>
                <td>₹{(row.price_per_kg_paise / 100).toFixed(2)}</td>
                <td>{row.source_label}</td>
                <td>{new Date(row.valid_from).toLocaleString()}</td>
                <td>{row.active ? "Active" : "Historical"}</td>
                <td><button className="btn secondary" onClick={() => beginEdit(row)}>Edit</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
