import React, { Component } from "react"
import { throttle } from "throttle-debounce"
import { searchCharities } from "../api";

export default class Home extends Component {
  state = {
    q: "",
		loading: false,
		results: []
  }

  constructor(props) {
    super(props)
    this.changeQuery = this.changeQuery.bind(this)

    this.autocompleteSearchThrottled = throttle(2000, this.autocompleteSearch)
  }

  changeQuery = event => {
    this.setState({ q: event.target.value, loading: true }, () => {
      this.autocompleteSearchThrottled(this.state.q)
    })
  }

  autocompleteSearch = async q => {
    this._fetch(q)
  }

  _fetch = async q => {
    if (!q || q.length === 1) {
      return
    }

    const _searches = this.state._searches || []
    _searches.push(q)
		this.setState({ _searches})

		try {
			const results = searchCharities(q)
			if (results) {
				console.log(results)
				this.setState({loading: false, results})
			}
		} catch (e) {
			console.error('server err', e)
			alert('There was a problem finding your charities. ' + e)
			this.setState({loading: false})
		}
  }

  render() {
    const _searches = this.state._searches || []
    const { q, loading, results } = this.state

    return (
      <div>
        <div className="container">
          <div className="hero-body">
            <div className="container has-text-centered">
              <h1 className="title">
								Discover amazing charities.
							</h1>
              <h2 className="subtitle">
                Intelligent search backed by <a href="https://arxiv.org/abs/1810.04805" target="_blank">BERT</a> and <a href="https://pytorch.org/" target="_blank">Pytorch</a>
              </h2>
            </div>
          </div>
          <div className="columns is-centered">
            <div className="column is-two-thirds">
              <div className="field">
                <div className={`control is-medium ${loading ? "is-loading" : ""}`}>
                  <textarea
                    className="textarea is-medium"
                    value={q}
                    onChange={this.changeQuery}
                    placeholder="Describe your ideal charity..."
                  />
                </div>
              </div>

              <div className="main-results">
                <div className="search-results" />

                <hr />
                <div className="past-searches">
                  {_searches.length ? (
                    <button
                      type="button"
                      onClick={event => this.setState({ _searches: [] })}
                    >
											Clear history
                    </button>
                  ) : null}
                  <ol>
                    {_searches.map((s, i) => {
                      return <li key={s + i}>{s}</li>
                    })}
                  </ol>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}
