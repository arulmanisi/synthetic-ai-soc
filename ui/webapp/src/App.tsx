import { useState, useEffect } from 'react'
import axios from 'axios'
import './index.css'

interface Alert {
    id: number;
    timestamp: string;
    source: string;
    severity: string;
    description: string;
    score: float;
    is_resolved: boolean;
}

function App() {
    const [alerts, setAlerts] = useState<Alert[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const response = await axios.get('http://localhost:8002/alerts/')
                setAlerts(response.data)
            } catch (error) {
                console.error('Error fetching alerts:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchAlerts()
        const interval = setInterval(fetchAlerts, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="container">
            <header>
                <h1>Synthetic AI SOC Dashboard</h1>
            </header>
            <main>
                {loading ? (
                    <p>Loading alerts...</p>
                ) : (
                    <div className="alert-list">
                        {alerts.map(alert => (
                            <div key={alert.id} className={`alert-card ${alert.severity}`}>
                                <div className="alert-header">
                                    <span className="severity-badge">{alert.severity}</span>
                                    <span className="timestamp">{new Date(alert.timestamp).toLocaleString()}</span>
                                </div>
                                <h3>{alert.description}</h3>
                                <div className="alert-details">
                                    <p>Source: {alert.source}</p>
                                    <p>Score: {alert.score.toFixed(2)}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    )
}

export default App
