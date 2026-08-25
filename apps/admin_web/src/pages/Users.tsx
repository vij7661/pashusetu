import { useState } from "react";

const demo = [
  ["PS-F-002184","Ramesh","Farmer","Verified","Active"],
  ["PS-B-00418","Hyderabad Meat Traders","Buyer","Verified","Active"],
  ["PS-B-00491","ABC Retail","Buyer","Pending","Review"]
];

export default function Users(){
  const [mask,setMask]=useState(true);
  return <div className="card">
    <div style={{display:"flex",justifyContent:"space-between"}}>
      <h3>Farmers & Buyers</h3>
      <button className="btn secondary" onClick={()=>setMask(!mask)}>
        {mask ? "Show permitted details" : "Mask details"}
      </button>
    </div>
    <table>
      <thead><tr><th>ID</th><th>Name</th><th>Type</th><th>KYC</th><th>Status</th></tr></thead>
      <tbody>
        {demo.map(r=><tr key={r[0]}>
          <td>{r[0]}</td><td>{mask ? r[1][0]+"••••" : r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td>
        </tr>)}
      </tbody>
    </table>
    <p className="note">Sensitive identity data must stay masked by default. Raw Aadhaar is not part of the core backend.</p>
  </div>
}
