import { useState } from "react";
import { post } from "../api";

export default function Payments(){
  const [tx,setTx]=useState("");
  const [result,setResult]=useState<any>(null);
  async function settle(){ setResult(await post(`/payments/transactions/${tx}/settle`)); }

  return <div className="card">
    <h3>Settlement Monitor</h3>
    <input className="field" placeholder="Transaction ID" value={tx} onChange={e=>setTx(e.target.value)} />
    <button className="btn" onClick={settle}>Load / Complete Settlement</button>
    {result && <div className="mono">{JSON.stringify(result,null,2)}</div>}
    <p className="note">Current funds provider is simulated. Production payment/hold/release must use the selected compliant provider.</p>
  </div>
}
