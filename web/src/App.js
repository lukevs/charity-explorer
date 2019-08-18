import React from "react"
import Home from "./components/Home"

import "./App.css"
import "bulma/css/bulma.css"
import logo from "./assets/logo.png"

function App() {
  return (
    <div className="App">
      <nav
        className="navbar dark"
        role="navigation"
        aria-label="main navigation"
      >
        <div className="navbar-brand">
          <a className="navbar-item" href="/">
            <img src={logo} alt="YouCharity" width="112" height="28" />
          </a>

          <a
            role="button"
            className="navbar-burger"
            aria-label="menu"
            aria-expanded="false"
          >
            <span aria-hidden="true" />
            <span aria-hidden="true" />
            <span aria-hidden="true" />
          </a>
        </div>
      </nav>
      <div id="wrapper">
        <Home />
      </div>
      <footer className="footer">
        <div className="content has-text-centered">
          <p>
            <b>YouCharity &copy;2019.</b>
            <br /> The source code is licensed under the&nbsp;
            <a href="http://opensource.org/licenses/mit-license.php">
              MIT
            </a>{" "}
            license.
            {/* The website content is licensed <a href="http://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY NC SA 4.0</a>. */}
          </p>
          <p>
            Source code available&nbsp;
            <a href="" target="_blank">
              here
            </a>
            .
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
