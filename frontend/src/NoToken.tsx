import { Icon } from "./icons";
import Logo from "./Logo";

export default function NoToken() {
  return (
    <main className="wrap">
      <div className="card pad-xl center narrow-card view">
        <div className="ring key"><Icon name="lock" size={46} strokeWidth={2.5} /></div>
        <h1 className="hero sm">Open Sortify from its private link</h1>
        <p className="lead tight">
          Sortify is protected by a secret token, so other websites can't touch your files. The link with the token is
          printed in the terminal where you started it.
        </p>
        <p className="note info left"><Logo size={22} /> Run <code>python -m sortify</code> and it will open the right link for you.</p>
      </div>
    </main>
  );
}
