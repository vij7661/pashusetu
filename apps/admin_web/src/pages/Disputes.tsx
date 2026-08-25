import { useState } from "react";
import { post } from "../api";

export default function Disputes(){
  const [id,setId]=useState("");
  const [decision,setDecision]=useState("Apply contract tolerance and verified reweigh evidence.");
  const [adjustment,setAdjustment]=useState("0");
  const [result,setResult]=useState<any>(null);

  async function resolve(){
    setResult(await post(`/disputes/${id}/resolve`,{
      final_decision:decision,
      settlement_adjustment_paise:Number(adjustment),
      resolution_rule:"Contract rule + verified evidence + controlled/independent reweigh"
    }));
  }

  return <div className="grid2">
    <div className="card">
      <h3>Resolve Dispute</h3>
      <input className="field" placeholder="Dispute ID" value={id} onChange={e=>setId(e.target.value)} />
      <textarea className="field" value={decision} onChange={e=>setDecision(e.target.value)} />
      <input className="field" value={adjustment} onChange={e=>setAdjustment(e.target.value)} />
      <button className="btn" onClick={resolve}>Apply Resolution</button>
    </div>
    <div className="card">
      <h3>Evidence rule</h3>
      <p>Origin weight · delivery weight · videos · QR · timestamps · Scale IDs · agreement tolerance · controlled/independent reweigh.</p>
      {result && <div className="mono">{JSON.stringify(result,null,2)}</div>}
      <p className="note">Admin should apply predefined rules, not arbitrarily choose a winner.</p>
    </div>
  </div>
}
