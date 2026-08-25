import { NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Users from "./pages/Users";
import Centres from "./pages/Centres";
import Transactions from "./pages/Transactions";
import Bids from "./pages/Bids";
import Disputes from "./pages/Disputes";
import Payments from "./pages/Payments";
import Audit from "./pages/Audit";
import Operators from "./pages/Operators";
import Login from "./pages/Login";

const nav = [
  ["/", "Dashboard"],
  ["/users", "Users / KYC"],
  ["/centres", "Centres / Scales"],
  ["/transactions", "Transactions"],
  ["/bids", "Bidding Audit"],
  ["/disputes", "Disputes"],
  ["/payments", "Payments"],
  ["/audit", "Audit Replay"],
  ["/operators", "Operator Scores"]
];

export default function App() {
  const loggedIn = !!localStorage.getItem("access_token");
  if (!loggedIn) return <Login />;

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">PashuSetu Admin</div>
        <nav className="nav">
          {nav.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === "/"}>{label}</NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <div className="topbar">
          <h2>Operations Console</h2>
          <button className="btn secondary" onClick={() => { localStorage.clear(); location.reload(); }}>
            Logout
          </button>
        </div>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/users" element={<Users />} />
          <Route path="/centres" element={<Centres />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/bids" element={<Bids />} />
          <Route path="/disputes" element={<Disputes />} />
          <Route path="/payments" element={<Payments />} />
          <Route path="/audit" element={<Audit />} />
          <Route path="/operators" element={<Operators />} />
        </Routes>
      </main>
    </div>
  );
}
