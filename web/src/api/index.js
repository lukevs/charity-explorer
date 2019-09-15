const axios = require('axios')

const PORT = 5000
// const BASE_URL = `http://localhost:${PORT}`
const BASE_URL = `http://youcharity.pcupcbgjhz.us-east-1.elasticbeanstalk.com`
axios.defaults.baseURL = BASE_URL

export const searchCharities = (query, rank) => (
	axios.post(`/search?rank=${rank || false}`, {query})
)