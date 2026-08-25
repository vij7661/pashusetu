export default function Centres(){
  return <div className="grid2">
    <div className="card">
      <h3>Mandal Centres</h3>
      <table><tbody>
        <tr><td>CHY-02</td><td>Chityal</td><td><span className="badge">Online</span></td></tr>
        <tr><td>NLG-04</td><td>Nalgonda</td><td><span className="badge">Online</span></td></tr>
        <tr><td>YDG-01</td><td>Yadadri</td><td><span className="badge warn">Limited</span></td></tr>
      </tbody></table>
    </div>
    <div className="card">
      <h3>Scale Registry</h3>
      <table><tbody>
        <tr><td>A-114</td><td>CHY-02</td><td><span className="badge">Valid</span></td></tr>
        <tr><td>A-118</td><td>YDG-01</td><td><span className="badge warn">Due</span></td></tr>
      </tbody></table>
    </div>
  </div>
}
