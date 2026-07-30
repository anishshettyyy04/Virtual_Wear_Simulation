import { Component } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Uncaught error caught by ErrorBoundary:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-950 p-6">
          <div className="max-w-md w-full glass-panel rounded-2xl p-8 text-center border border-rose-500/20 shadow-2xl">
            <div className="w-16 h-16 bg-rose-500/10 rounded-2xl flex items-center justify-center mx-auto mb-6 text-rose-400">
              <AlertTriangle size={32} />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Something Went Wrong</h2>
            <p className="text-slate-400 text-sm mb-6">
              An unhandled UI error occurred in the simulation engine. Please refresh or try again.
            </p>
            {this.state.error?.message && (
              <div className="bg-slate-900/80 rounded-xl p-3 text-xs text-rose-300 font-mono mb-6 text-left overflow-x-auto max-h-24 border border-slate-800">
                {this.state.error.message}
              </div>
            )}
            <button
              onClick={this.handleReload}
              className="w-full inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-3 rounded-xl transition-all shadow-lg shadow-indigo-600/20"
            >
              <RefreshCw size={18} />
              Reload Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
