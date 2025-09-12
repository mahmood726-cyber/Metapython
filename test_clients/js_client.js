// MetaPython JavaScript Client (Generated)
class MetaPythonClient {
    constructor(baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
    }
    
    async runMetaAnalysis(config) {
        const response = await fetch(`${this.baseUrl}/api/v1/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        return await response.json();
    }
}
