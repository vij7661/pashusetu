import { useState } from "react";
import { get } from "../api";

export default function Bids(){
  const [listing,setListing]=useState("");
  const [rows,setRows]=useState<any[]>([]);
  async function load(){ setRows(await get(`/bidding/listings/${listing}/bids`)); }

  return <div className="card">
    <h3>Bidding Audit</h3>
    <input className="field" placeholder="Listing ID" value={listing} onChange={e=>setListing(e.target.value)} />
    <button className="btn" onClick={load}>Load Bids</button>
    <table>
      <thead><tr><th>Seq</th><th>Bid ID</th><th>₹/kg paise</th><th>Total paise</th><th>Status</th></tr></thead>
      <tbody>{rows.map(x=><tr key={x.bid_id}>
        <td>#{x.server_sequence}</td><td>{x.bid_id}</td><td>{x.price_per_kg_paise}</td><td>{x.total_offer_paise}</td><td>{x.status}</td>
      </tr>)}</tbody>
    </table>
    <p className="note">Server sequence is authoritative. Client timestamps do not decide priority.</p>
  </div>
}
