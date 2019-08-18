import React, { Component } from "react"
import { throttle } from "throttle-debounce"
import { searchCharities } from "../api"

import loading_spinner from '../assets/loading.gif'

export default class Home extends Component {

  state = {
    q: "",
    loading: false,
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
    return 'N/A' 
  }
  autocompleteSearch = q => {
    this._fetch(q)
  }

  resultClicked = (result) => {
    // TODO: open result in new tab window.
    console.log('clicked', result)
  }

  _fetch = q => {
    const self = this
    if (!q || q.length === 1) {
      return
    }

    const _searches = this.state._searches || []
    _searches.push(q)
    this.setState({ _searches, loading: true, startTime: new Date() })

    searchCharities(q).then(data => {
      const results = data['data']['results']
      console.log(results)
      self.setState({ loading: false, results, endTime: new Date() })
    }).catch(e => {
      console.error("server err", e)
      alert("There was a problem finding your charities. " + e)
      self.setState({ loading: false })
    })
  }

  render() {
    const _searches = this.state._searches || []
    const { q, loading, results } = this.state

    const duration = this.getDuration()

    const hasResults = results && results.length > 0

    return (
      <div>
        <div className="container">
          <div className="hero-body">
            <div className="container has-text-centered">
              <h1 className="title">Discover amazing charities.</h1>
              <h2 className="subtitle">
                Intelligent search backed by{" "}
                <a href="https://arxiv.org/abs/1810.04805" target="_blank">
                  BERT
                </a>{" "}
                and{" "}
                <a href="https://pytorch.org/" target="_blank">
                  Pytorch
                </a>
              </h2>
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
                    placeholder="Describe your ideal charity..."
                  />

                  {!loading && <a class="button is-danger search-button" onClick={() => this.autocompleteSearch(q)}>Search</a>}

                  </div>
                </div>
              <hr/>
              <div className="main-results">
                {loading && <div>
                  <img src={loading_spinner}/>
                  </div>}

                {hasResults && !loading && <p className='has-text-centered'>
                  Showing top <b>{results.length}</b> results. Charity matching took <b>{duration}</b> seconds.
                </p>}
                {hasResults && !loading && results.map((result, i) => {
                  return <div key={i} className='search-result-row' onClick={() => this.resultClicked(result)}>
                    {JSON.stringify(result)}
                  </div>
                })}
               
                {(!loading && _searches.length > 0) && <div className="past-searches">
                  <hr />
                    <a class="button is-danger clear-button is-outlined" onClick={event => this.setState({ _searches: [] })}>
                      Clear history
                    </a>
                    <ol>
                    {_searches.map((s, i) => {
                      return <li key={s + i}>{s}</li>
                    })}
                    </ol>
                </div>}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}
