import { useState } from 'react';
import { Sliders } from 'lucide-react';

export const BeforeAfterSlider = ({
  originalImage,
  simulatedImage,
}) => {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [mode, setMode] = useState('slider'); // 'slider' | 'sideBySide'

  const handleSliderMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPosition(percentage);
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Mode Controls */}
      <div className="flex items-center justify-between bg-slate-900/60 p-2 rounded-xl border border-slate-800">
        <span className="text-xs font-semibold text-slate-300 px-2">
          Visual Comparison Mode
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setMode('slider')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
              mode === 'slider'
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Split Slider
          </button>
          <button
            onClick={() => setMode('sideBySide')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
              mode === 'sideBySide'
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Side by Side
          </button>
        </div>
      </div>

      {/* Main Display Area */}
      {mode === 'slider' ? (
        <div
          className="relative w-full h-[450px] sm:h-[550px] rounded-3xl overflow-hidden glass-panel border border-slate-800 select-none cursor-ew-resize"
          onMouseMove={handleSliderMove}
          onTouchMove={(e) => {
            if (e.touches[0]) {
              const rect = e.currentTarget.getBoundingClientRect();
              const x = e.touches[0].clientX - rect.left;
              setSliderPosition(Math.max(0, Math.min(100, (x / rect.width) * 100)));
            }
          }}
        >
          {/* Simulated Image (Base layer - Right) */}
          <img
            src={simulatedImage}
            alt="AI Virtual Try-On Render"
            className="absolute inset-0 w-full h-full object-contain bg-slate-950 p-2"
          />
          <div className="absolute top-4 right-4 bg-indigo-600/90 text-white text-[11px] font-bold px-3 py-1 rounded-full backdrop-blur-md z-10 shadow-lg">
            AI Simulated Try-On
          </div>

          {/* Original Image (Overlay layer - Left clipped) */}
          <div
            className="absolute inset-y-0 left-0 overflow-hidden"
            style={{ width: `${sliderPosition}%` }}
          >
            <img
              src={originalImage}
              alt="Original Avatar"
              className="absolute inset-0 w-full h-full object-contain bg-slate-950 p-2"
              style={{ width: '100%', maxWidth: 'none' }}
            />
            <div className="absolute top-4 left-4 bg-slate-800/90 text-slate-200 text-[11px] font-bold px-3 py-1 rounded-full backdrop-blur-md z-10 shadow-lg">
              Original Avatar
            </div>
          </div>

          {/* Divider Bar */}
          <div
            className="absolute inset-y-0 w-0.5 bg-white shadow-2xl z-20"
            style={{ left: `${sliderPosition}%` }}
          >
            <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-white text-slate-950 flex items-center justify-center shadow-2xl">
              <Sliders size={16} />
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative h-96 rounded-2xl overflow-hidden glass-card border border-slate-800 p-2">
            <span className="absolute top-3 left-3 bg-slate-800/90 text-slate-200 text-[11px] font-bold px-3 py-1 rounded-full z-10">
              Original Avatar
            </span>
            <img
              src={originalImage}
              alt="Original Avatar"
              className="w-full h-full object-contain"
            />
          </div>
          <div className="relative h-96 rounded-2xl overflow-hidden glass-card border border-slate-800 p-2">
            <span className="absolute top-3 left-3 bg-indigo-600/90 text-white text-[11px] font-bold px-3 py-1 rounded-full z-10">
              AI Virtual Try-On Render
            </span>
            <img
              src={simulatedImage}
              alt="AI Simulated Try-On"
              className="w-full h-full object-contain"
            />
          </div>
        </div>
      )}
    </div>
  );
};
