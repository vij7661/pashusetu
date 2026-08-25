import { useState } from "react";
import { get } from "../api";

export default function Audit(){
  const [type,setType]=useState("TRANSACTION");
  const [id,setId]=useState("");
  const [events,setEvents]=useState<any[]>([]);
  async function load(){ setEvents(await get(`/audit/${type}/${id}`)); }

  return <div className="card">
    <h3>Audit Replay</h3>
    <select className="field" value={type} onChange={e=>setType(e.target.value)}>
      <option>TRANSACTION</option><option>LISTING</option><option>WEIGHMENT</option>
    </select>
    <input className="field" placeholder="Aggregate UUID" value={id} onChange={e=>setId(e.target.value)} />
    <button className="btn" onClick={load}>Load Events</button>
    <div className="mono">{events.map(e=>`${e.sequence} ${e.event_type}\n`).join("") || "No events loaded."}</div>
    <p className="note">Replay should reproduce the same outcome from the same ordered event history.</p>
  </div>
}
