const axios = require('axios')

const PORT = 8778
const BASE_URL = `http://localhost:${PORT}`

export const searchCharities = (query, rank) => (
	axios.post(`${BASE_URL}/search?rank=${rank || false}`, {query})
)