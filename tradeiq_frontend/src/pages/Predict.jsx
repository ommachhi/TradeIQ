import PredictionForm from '../components/PredictionForm'
import Sidebar from '../components/Sidebar'

/**
 * Predict Page
 * Stock price prediction interface
 */
const Predict = () => {
  return (
    <div className="flex">
      <Sidebar />
      <div className="min-h-[calc(100vh-64px)] bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 px-4 flex-1">
      {/* Animated Background Elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl opacity-20 -translate-x-1/2 -translate-y-1/2"></div>
      <div className="absolute top-1/2 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl opacity-20 translate-x-1/2 -translate-y-1/2"></div>

      <div className="relative z-10 max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 text-white">
            Stock Price <span className="gradient-text">Prediction</span>
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Enter the stock market data to get an AI-powered price prediction and trading recommendation
          </p>
        </div>

        {/* Prediction Form */}
        <PredictionForm />

        {/* Info Box */}
        <div className="mt-12 max-w-2xl mx-auto card bg-blue-500/10 border border-blue-500/30">
          <div className="flex items-start space-x-4">
            <div className="text-blue-400 text-2xl flex-shrink-0">ℹ️</div>
            <div>
              <h3 className="font-bold text-white mb-2">How It Works</h3>
              <p className="text-gray-300 text-sm">
                Our machine learning model analyzes stock market patterns to predict closing prices. 
                Enter the stock's opening price, highest price, lowest price, and trading volume to get 
                an instant prediction along with a buy/sell/hold recommendation.
              </p>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  )
}

export default Predict
