import { useState } from "react";
import { loginAdmin } from "../auth";

export default function Login() {
  const [mobile, setMobile] = useState("+919876500099");
  const [otp, setOtp] = useState("4816");
  const [error, setError] = useState("");

  async function login() {
    try {
      await loginAdmin(mobile, otp);
      location.reload();
    } catch (e: any) {
      setError(e?.message || String(e));
    }
  }

  return (
    <div style={{maxWidth:420,margin:"90px auto"}} className="card">
      <h2>PashuSetu Admin Login</h2>
      <input className="field" value={mobile} onChange={e=>setMobile(e.target.value)} />
      <input className="field" value={otp} onChange={e=>setOtp(e.target.value)} />
      {error && <p style={{color:"red"}}>{error}</p>}
      <button className="btn" onClick={login}>Login</button>
      <p className="note">Development OTP: 4816. Production admin access must use stricter authentication and role checks.</p>
    </div>
  );
}
