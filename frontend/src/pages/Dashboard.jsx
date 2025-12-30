// frontend/src/pages/Dashboard.jsx
import React, { useState } from 'react'
import axios from 'axios'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

function Dashboard() {
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [credentials, setCredentials] = useState({
    aws_access_key: '',
    aws_secret_key: '',
    aws_region: 'us-east-1'
  })

  const handleAnalyze = async () => {
    if (!credentials.aws_access_key || !credentials.aws_secret_key) {
      alert('Please enter AWS credentials')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post('http://localhost:8000/api/analyze', credentials)
      setAnalysis(response.data)
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">CloudOptimizer</h1>
          <p className="text-gray-600 mt-1">Analyze and reduce your AWS costs</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-8 px-4">
        {!analysis ? (
          // Input Form
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Connect Your AWS Account</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  AWS Access Key ID
                </label>
                <input
                  type="password"
                  value={credentials.aws_access_key}
                  onChange={(e) => setCredentials({
                    ...credentials,
                    aws_access_key: e.target.value
                  })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500"
                  placeholder="AKIA..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  AWS Secret Access Key
                </label>
                <input
                  type="password"
                  value={credentials.aws_secret_key}
                  onChange={(e) => setCredentials({
                    ...credentials,
                    aws_secret_key: e.target.value
                  })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500"
                  placeholder="wJalrXUtnFEM..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  AWS Region
                </label>
                <select
                  value={credentials.aws_region}
                  onChange={(e) => setCredentials({
                    ...credentials,
                    aws_region: e.target.value
                  })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500"
                >
                  <option value="us-east-1">US East (N. Virginia)</option>
                  <option value="us-west-2">US West (Oregon)</option>
                  <option value="eu-west-1">EU (Ireland)</option>
                </select>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Analyzing...' : 'Analyze My Account'}
              </button>
            </div>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> Your credentials are never stored. Analysis happens in real-time and credentials are discarded after use.
              </p>
            </div>
          </div>
        ) : (
          // Results
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-gray-600 text-sm font-medium">Total Potential Savings</h3>
                <p className="text-3xl font-bold text-green-600 mt-2">
                  ${(analysis.total_potential_savings / 1000).toFixed(1)}K
                </p>
                <p className="text-gray-500 text-sm mt-1">/year</p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-gray-600 text-sm font-medium">Monthly Spend</h3>
                <p className="text-3xl font-bold text-blue-600 mt-2">
                  ${(analysis.cost_summary.total_30day_cost).toFixed(0)}
                </p>
                <p className="text-gray-500 text-sm mt-1">Last 30 days</p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-gray-600 text-sm font-medium">Recommendations</h3>
                <p className="text-3xl font-bold text-orange-600 mt-2">
                  {analysis.ec2_recommendations.length + analysis.storage_recommendations.length}
                </p>
                <p className="text-gray-500 text-sm mt-1">Actions to take</p>
              </div>
            </div>

            {/* EC2 Recommendations */}
            {analysis.ec2_recommendations.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">EC2 Recommendations</h2>
                <div className="space-y-4">
                  {analysis.ec2_recommendations.map((item, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-medium text-gray-900">{item.instance_id}</h3>
                          <p className="text-sm text-gray-600 mt-1">
                            Type: {item.instance_type} | CPU: {item.avg_cpu_7d}%
                          </p>
                          <p className="text-sm font-medium mt-2">{item.recommendation}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            Cost: ${item.monthly_cost}/month (${item.annual_cost}/year)
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-green-600">
                            Save ${(item.potential_savings / 1000).toFixed(1)}K/yr
                          </p>
                          <button className="mt-2 text-sm text-blue-600 hover:text-blue-800">
                            Implement
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Storage Recommendations */}
            {analysis.storage_recommendations.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Storage Recommendations</h2>
                <div className="space-y-4">
                  {analysis.storage_recommendations.map((item, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                      <h3 className="font-medium text-gray-900">{item.bucket}</h3>
                      <p className="text-sm text-gray-600 mt-1">{item.issue}</p>
                      <p className="text-sm font-medium mt-2">{item.recommendation}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        Cost: ${item.monthly_cost}/month
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Cost Breakdown Chart */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Spend by Service</h2>
              <BarChart width={600} height={300} data={
                Object.entries(analysis.cost_summary.costs_by_service).map(([service, cost]) => ({
                  service,
                  cost: parseFloat(cost)
                }))
              }>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="service" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="cost" fill="#3b82f6" />
              </BarChart>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={() => setAnalysis(null)}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700"
              >
                Analyze Another Account
              </button>
              <button
                onClick={() => {
                  const csv = generateCSV(analysis)
                  downloadCSV(csv)
                }}
                className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700"
              >
                Export as CSV
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard