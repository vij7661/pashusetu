export default function Dashboard(){
  return <>
    <div className="grid4">
      <div className="card kpi"><strong>126</strong><span>ACTIVE LISTINGS</span></div>
      <div className="card kpi"><strong>34</strong><span>LIVE TRANSACTIONS</span></div>
      <div className="card kpi"><strong>3</strong><span>OPEN DISPUTES</span></div>
      <div className="card kpi"><strong>8</strong><span>MANDAL CENTRES</span></div>
    </div>
    <div className="grid2">
      <div className="card">
        <h3>Needs attention</h3>
        <table><tbody>
          <tr><td>TX-55182</td><td>Weight dispute</td><td><span className="badge bad">Open</span></td></tr>
          <tr><td>Scale A-118</td><td>Calibration</td><td><span className="badge warn">Due</span></td></tr>
          <tr><td>Buyer B-00491</td><td>KYC</td><td><span className="badge warn">Review</span></td></tr>
        </tbody></table>
      </div>
      <div className="card">
        <h3>Today</h3>
        <p>42 verified weighments</p>
        <p>19 pickups</p>
        <p>17 deliveries</p>
        <p>₹4.8L settlement volume</p>
      </div>
    </div>
    <div className="note">
      Normal transactions should progress through backend rules automatically. Admin is for monitoring, exceptions and authorised decisions.
    </div>
  </>
}
