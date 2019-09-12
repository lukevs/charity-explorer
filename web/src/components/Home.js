import React, { Component } from "react"
import { throttle } from "throttle-debounce"
import { searchCharities } from "../api"
import { truncate } from "lodash"
import tinygradient from "tinygradient"
import heartLogo from "../assets/heart_logo.png"

import loading_spinner from "../assets/loading.gif"

export default class Home extends Component {
  state = {
    q: "",
    loading: false,
    ranking: false,
    results: [],
    startTime: null,
    endTime: null
  }

  constructor(props) {
    super(props)
    this.changeQuery = this.changeQuery.bind(this)
    // this.autocompleteSearchThrottled = throttle(1000, this.autocompleteSearch)
  }

  changeQuery = event => {
    this.setState({ q: event.target.value })
  }

  getDuration() {
    const { startTime, endTime } = this.state
    if (startTime && endTime) {
      return Math.abs((endTime.getTime() - startTime.getTime()) / 1000)
    }
    return "N/A"
  }
  autocompleteSearch = q => {
    this._fetch(q)
  }

  resultClicked = result => {
    // TODO: open result in new tab window.
    console.log("clicked", result)
    const { name, url } = result
    if (url) {
      window.open(url, "_blank")
    } else {
      alert(`'No additional information found for ${name}.`)
    }
  }

  _fetch = q => {
    const self = this
    if (!q) {
      alert(
        "Enter whatever charity description or idea is on your mind to search!"
      )
      return
    }

    const _searches = this.state._searches || []
    const ranking = this.state.ranking
    _searches.push(q)
    this.setState({ _searches, loading: true, startTime: new Date() })

    searchCharities(q, ranking)
      .then(data => {
        const results = data["data"]["results"]
        console.log(results)
        self.setState({ loading: false, results, endTime: new Date() })
      })
      .catch(e => {
        console.error("server err", e)
        alert("There was a problem finding your charities. " + e)
        self.setState({ loading: false })
      })
  }

  toggleRank() {
    const ranking = !this.state.ranking
    console.log('toggle', ranking)
    this.setState({ranking})
  }

  render() {
    const _searches = this.state._searches || []
    const { q, loading, results, ranking } = this.state

    const duration = this.getDuration()

    const hasResults = results && results.length > 0

    const gradient = tinygradient("red", "yellow", "green")
    const colors = gradient.rgb(101)

    return (
      <div>
        <div className="container">
          <div className="hero-body">
            <div className="container has-text-centered">
              <img src={heartLogo} className="header-logo" />
              <h1 className="title">Discover amazing charities.</h1>
              <h2 className="subtitle">
                Searching nearly 400 charities, backed by{" "}
                <a href="https://arxiv.org/abs/1810.04805" target="_blank">
                  BERT
                </a>{" "}
                and{" "}
                <a href="https://pytorch.org/" target="_blank">
                  Pytorch
                </a>
              </h2>
              <label class="checkbox" className='rank-input'>
                <input type="checkbox" value={ranking} onChange={() => this.toggleRank()}/>&nbsp;
                <span>Use sentence prediction: More accurate, less fast.</span>
              </label>
            </div>
          </div>
          <div className="columns is-centered">
            <div className="column is-two-thirds">
              <div className="field">
                <div
                  className={`control is-medium ${loading ? "is-loading" : ""}`}
                >
                  <textarea
                    className="textarea is-medium"
                    value={q}
                    onChange={this.changeQuery}
                    placeholder="Describe your ideal charity with phrases... <3"
                  />

                  {!loading && (
                    <a
                      className="button is-danger search-button"
                      onClick={() => this.autocompleteSearch(q)}
                    >
                      Search
                    </a>
                  )}
                </div>
              </div>
              <hr />
              <div className="main-results">
                {loading && (
                  <div>
                    <img src={loading_spinner} />
                  </div>
                )}

                {hasResults && !loading && (
                  <p className="has-text-centered result-info-text">
                    Showing top <b>{results.length}</b> results. Charity
                    matching took <b>{duration}</b> seconds.
                  </p>
                )}

                {hasResults && (
                  <div className="columns">
                    <div className="column charity-col jis-three-quarters">
                      <b>Charity</b>
                    </div>
                    <div className="column rel-col is-one-quarter">
                      <b>Relevance Score</b>
                    </div>
                  </div>
                )}
                {hasResults &&
                  !loading &&
                  results.map((result, i) => {
                    const { name, description, url, score } = result
                    const truncatedDescription = truncate(description, {
                      length: 250,
                      separator: " "
                    })
                    const color = colors[0]
                    return (
                      <div
                        key={i}
                        className="search-result-row"
                        onClick={() => this.resultClicked(result)}
                      >
                        <div className="columns">
                          <div className="column is-three-quarters">
                            <h2 className="search-result-heading">{i+1}. {name}</h2>
                            <p>{truncatedDescription}</p>
                            <a
                              href={url}
                              target="_blank"
                              className="search-result-url"
                            >
                              {url}
                            </a>
                          </div>
                          <div className="column is-one-quarter">
                            <span
                              className="search-result-score"
                              style={{ color }}
                            >
                              {score || 50}
                            </span>
                          </div>
                        </div>
                      </div>
                    )
                  })}

                {!loading && _searches.length > 0 && (
                  <div className="past-searches">
                    <hr />
                    <a
                      className="button is-danger clear-button is-outlined"
                      onClick={event => this.setState({ _searches: [] })}
                    >
                      Clear history
                    </a>
                    <p>Recent Searches:</p>
                    {_searches.map((s, i) => {
                      return (
                        <div key={s + i}>
                          <b>{s}</b>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}
