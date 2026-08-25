import { useState } from "react";
import { get } from "../api";

export default function Transactions(){
  const [id,setId]=useState("");
  const [data,setData]=useState<any>(null);
  const [error,setError]=useState("");

  async function load(){
    try{ setData(await get(`/transaction/${id}`)); setError(""); }
    catch(e:any){ setError(e?.message||String(e)); }
  }

  return <>
    <div className="card">
      <h3>Transaction Monitor</h3>
      <input className="field" placeholder="TX-..." value={id} onChange={e=>setId(e.target.value)} />
      <button className="btn" onClick={load}>Load authoritative state</button>
      {error && <p style={{color:"red"}}>{error}</p>}
      {data && <div className="mono">{JSON.stringify(data,null,2)}</div>}
    </div>
    <div className="note">Farmer, Buyer and Admin should all see the same backend transaction state.</div>
  </>
}
