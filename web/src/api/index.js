const axios = require('axios')

const PORT = 8778
const BASE_URL = `http://localhost:${PORT}`

export const searchCharities = (query) => (
	axios.post(`${BASE_URL}/search`, {query})
)