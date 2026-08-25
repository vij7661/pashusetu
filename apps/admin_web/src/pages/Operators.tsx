export default function Operators(){
  return <div className="card">
    <h3>Operator Scorecards</h3>
    <table>
      <thead><tr><th>Operator</th><th>Centre</th><th>Weighments</th><th>Reweigh %</th><th>Disputes</th><th>Score</th></tr></thead>
      <tbody>
        <tr><td>Suresh</td><td>CHY-02</td><td>214</td><td>3.1%</td><td>2</td><td>92</td></tr>
        <tr><td>Arun</td><td>NLG-04</td><td>176</td><td>5.6%</td><td>4</td><td>86</td></tr>
      </tbody>
    </table>
    <p className="note">High reweigh/dispute rates are signals for review, not automatic misconduct findings.</p>
  </div>
}
