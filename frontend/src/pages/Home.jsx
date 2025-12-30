// frontend/src/pages/Home.jsx
import React from 'react'
import { Link } from 'react-router-dom'

function Home() {
  const plans = [
    {
      name: 'Starter',
      price: '$29',
      features: ['Up to 10 AWS accounts', 'Basic recommendations', 'Email reports']
    },
    {
      name: 'Pro',
      price: '$99',
      features: ['Unlimited accounts', 'Advanced AI recommendations', 'Slack integration', 'API access']
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      features: ['Everything in Pro', 'Dedicated support', 'Custom integrations', 'SLA']
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800">
      <div className="max-w-7xl mx-auto py-16 px-4">
        <h1 className="text-4xl font-bold text-white mb-4">CloudOptimizer</h1>
        <p className="text-xl text-blue-100 mb-8">
          Reduce your AWS costs by 30% on average with AI-powered optimization
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          {plans.map((plan) => (
            <div key={plan.name} className="bg-white rounded-lg shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
              <p className="text-3xl font-bold text-blue-600 mt-4">{plan.price}<span className="text-lg text-gray-600">/month</span></p>
              
              <ul className="mt-6 space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center">
                    <span className="text-green-500 mr-3">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
              
              <button className="w-full mt-8 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700">
                Get Started
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Home