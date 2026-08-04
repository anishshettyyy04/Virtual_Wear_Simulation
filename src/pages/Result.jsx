import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Download, Share2, RefreshCw, Sparkles, CheckCircle2, Clock, Shirt, BarChart3, Image as ImageIcon, Star, Tag, AlertCircle, Loader2 } from 'lucide-react';
import { SEO } from '@/components/common/SEO';
import { SectionTitle } from '@/components/ui/SectionTitle';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { useSimulation } from '@/hooks/useSimulation';

export default function Result() {
  const navigate = useNavigate();
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [imageLoadError, setImageLoadError] = useState(false);
  const { simulationResult, resultImage, simulationStatus, personImage, selectedGarment, error, isProcessing, runSimulation } = useSimulation();

  const isCompleted = simulationStatus === 'completed' && Boolean(simulationResult);
  const recommendations = simulationResult?.recommendations || [];
  const topRec = recommendations[0];

  // Determine pipeline timing from tryon result if available
  const tryonTimings = simulationResult?.tryon?.timings;
  const pipelineDuration = tryonTimings?.total_duration_ms || simulationResult?.executionTimeMs;

  const resultInfo = {
    status: isCompleted ? 'Completed' : isProcessing ? 'Processing...' : 'Pending Simulation',
    processingTime: pipelineDuration ? `${pipelineDuration.toFixed(2)} ms` : 'N/A',
    selectedOutfit: topRec?.name || selectedGarment?.title || 'No garment selected',
    confidence: topRec?.score ? `${topRec.score.toFixed(1)}%` : 'N/A',
  };

  const displayOriginal = personImage?.previewUrl || simulationResult?.originalImageUrl || null;

  // Prioritize AI-generated image; track whether it's a true AI result or fallback
  const aiRenderedUrl = simulationResult?.renderedImageUrl;
  const isAiResult = Boolean(aiRenderedUrl && aiRenderedUrl !== personImage?.previewUrl && aiRenderedUrl !== topRec?.image);
  const displayResult = aiRenderedUrl || resultImage || topRec?.image || null;

  useEffect(() => {
    console.log('[RESULT:MOUNT]', {
      displayOriginal,
      displayResult,
      isAiResult,
      simulationStatus,
      renderedImageUrl: simulationResult?.renderedImageUrl,
      resultImage,
    });
    // Reset image load error when a new result arrives
    setImageLoadError(false);
  }, [personImage, simulationResult, resultImage, displayResult, displayOriginal, isAiResult, simulationStatus]);

  const handleRetry = async () => {
    setImageLoadError(false);
    const result = await runSimulation();
    if (!result) {
      // Stay on result page — error will be shown via error state
    }
  };

  const handleDownloadReport = () => {
    console.log('[STAGE6:PDF_INPUTS]', {
      displayOriginal,
      displayResult,
      isOriginalAccessible: Boolean(displayOriginal),
      isResultAccessible: Boolean(displayResult)
    });
    const reportWindow = window.open('', '_blank');
    if (!reportWindow) {
      alert('Please allow popups to download the AI Virtual Try-On report.');
      return;
    }

    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Virtual Wear Simulation — AI Fitting Report</title>
          <style>
            body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 24px; }
            .header { border-bottom: 2px solid #3b82f6; padding-bottom: 12px; margin-bottom: 20px; }
            .title { font-size: 24px; font-weight: bold; color: #38bdf8; margin: 0; }
            .meta { font-size: 12px; color: #94a3b8; margin-top: 4px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
            .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 16px; }
            .card h4 { margin: 0 0 12px 0; color: #cbd5e1; font-size: 14px; }
            .img-box { aspect-ratio: 3/4; width: 100%; border-radius: 8px; overflow: hidden; background: #090d16; }
            .img-box img { width: 100%; height: 100%; object-fit: cover; }
            .reasons { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
            .badge { background: #1e1b4b; border: 1px solid #4338ca; color: #c7d2fe; padding: 4px 8px; border-radius: 6px; font-size: 11px; }
            .table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
            .table td { padding: 8px; border-bottom: 1px solid #334155; }
            .table td:first-child { color: #94a3b8; font-weight: bold; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1 class="title">AI Virtual Wear Simulation — Audit Report</h1>
            <div class="meta">Generated on: ${new Date().toLocaleString()} | User ID: ${simulationResult?.userId || 'USR001'} | Status: ${resultInfo.status}</div>
          </div>
          <div class="grid">
            <div class="card">
              <h4>Input Avatar Model</h4>
              <div class="img-box"><img src="${displayOriginal || ''}" alt="Input Avatar" /></div>
            </div>
            <div class="card">
              <h4>AI Virtual Try-On Render Output</h4>
              <div class="img-box"><img src="${displayResult || ''}" alt="AI TryOn Output" /></div>
            </div>
          </div>
          <div class="card">
            <h4>Recommended Garment & Fitting Details</h4>
            <table class="table">
              <tr><td>Selected Outfit:</td><td>${resultInfo.selectedOutfit}</td></tr>
              <tr><td>Match Score:</td><td>${resultInfo.confidence}</td></tr>
              <tr><td>Engine Strategy:</td><td>${simulationResult?.strategy || 'RuleBased v1.0.0'}</td></tr>
              <tr><td>Pipeline Latency:</td><td>${resultInfo.processingTime}</td></tr>
            </table>
            <div class="reasons">
              ${(topRec?.reasons || ['High fit compatibility']).map(r => `<span class="badge">✓ ${r}</span>`).join('')}
            </div>
          </div>
          <script>
            window.onload = function() {
              setTimeout(function() { window.print(); }, 500);
            };
          </script>
        </body>
      </html>
    `;

    reportWindow.document.write(htmlContent);
    reportWindow.document.close();
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <SEO
        title="Simulation Result"
        description="Inspect AI Virtual Wear comparison result, fit confidence, and processing metrics."
      />

      <SectionTitle
        badge="Comparison View"
        title="AI Virtual Try-On & Recommendation Result"
        subtitle="Compare original avatar image against live AI Virtual Wear simulation and recommendation output."
      />

      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-rose-950/40 border border-rose-800 rounded-xl flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <AlertCircle size={18} className="text-rose-400 shrink-0" />
            <span className="text-xs text-rose-300">{error}</span>
          </div>
          <Button variant="outline" size="sm" leftIcon={<RefreshCw size={14} />} onClick={handleRetry}>
            Retry
          </Button>
        </div>
      )}

      {/* Processing Indicator */}
      {isProcessing && (
        <Card hover={false} className="border border-blue-800/40 bg-blue-950/20 p-6">
          <div className="flex items-center justify-center gap-3">
            <Loader2 size={20} className="text-blue-400 animate-spin" />
            <span className="text-sm text-blue-300 font-semibold">AI inference in progress — this takes ~40 seconds...</span>
          </div>
        </Card>
      )}

      {/* COMPARISON INTERFACE: Original Image | AI Result */}
      <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Sparkles size={18} className="text-blue-400" />
            <h3 className="text-base font-bold text-white">Side-by-Side Comparison</h3>
          </div>
          <Badge variant={isCompleted ? 'success' : 'neutral'} size="sm" icon={<CheckCircle2 size={12} />}>
            Render Status: {resultInfo.status}
          </Badge>
        </div>

        {/* Side-by-Side Image Display */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          
          {/* Left: Original Image Container */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span>Original Image</span>
              <span className="text-[10px] text-slate-500 font-mono">Input Photo</span>
            </div>

            <div className="relative aspect-[3/4] rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden flex flex-col items-center justify-center p-6 text-center group">
              {displayOriginal ? (
                <img
                  src={displayOriginal}
                  alt="Original Model"
                  className="absolute inset-0 w-full h-full object-cover"
                  onError={(e) => {
                    e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="800" viewBox="0 0 600 800"><rect width="600" height="800" fill="%230f172a"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%2364748b" font-size="18" font-family="sans-serif">Model Avatar Photo</text></svg>';
                  }}
                />
              ) : (
                <>
                  <div className="w-20 h-20 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 mb-3 group-hover:scale-105 transition-transform z-10">
                    <ImageIcon size={36} className="text-slate-400" />
                  </div>
                  <span className="text-xs font-semibold text-slate-300 mb-1 z-10">Original Model Avatar</span>
                  <span className="text-[11px] text-slate-500 max-w-xs z-10">
                    Please upload an avatar image or pick a sample on the Upload page.
                  </span>
                </>
              )}
              <div className="absolute top-3 left-3 z-10">
                <Badge variant="neutral" size="sm">Original</Badge>
              </div>
            </div>
          </div>

          {/* Right: AI Result Container */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span className="text-blue-400 font-bold">AI Result / Top Match</span>
              <span className="text-[10px] text-purple-400 font-mono">Virtual Wear Output</span>
            </div>

            <div className="relative aspect-[3/4] rounded-2xl bg-slate-950 border-2 border-blue-500/40 overflow-hidden flex flex-col items-center justify-center p-6 text-center group shadow-xl shadow-blue-600/10">
              {displayResult ? (
                <img
                  src={displayResult}
                  alt="AI Output"
                  className="absolute inset-0 w-full h-full object-cover"
                  onLoad={() => setImageLoadError(false)}
                  onError={(e) => {
                    console.error('[RESULT:IMAGE_LOAD_FAILED]', displayResult);
                    setImageLoadError(true);
                    e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="800" viewBox="0 0 600 800"><rect width="600" height="800" fill="%230f172a"/><text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" fill="%23ef4444" font-size="16" font-family="sans-serif">Image Load Failed</text><text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle" fill="%2364748b" font-size="12" font-family="sans-serif">Click Retry to regenerate</text></svg>';
                  }}
                />
              ) : (
                <>
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-blue-600/20 to-purple-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-3 group-hover:scale-105 transition-transform z-10">
                    <Sparkles size={36} className="text-blue-400" />
                  </div>
                  <span className="text-xs font-semibold text-white mb-1 z-10">AI Recommendation Result</span>
                  <span className="text-[11px] text-slate-400 max-w-xs z-10">
                    Run simulation on the Upload page to generate live recommendation & fitting result.
                  </span>
                </>
              )}
              <div className="absolute top-3 right-3 z-10">
                <Badge variant={isAiResult ? 'primary' : 'neutral'} size="sm" icon={<Sparkles size={10} />}>
                  {isAiResult ? 'AI Render' : imageLoadError ? 'Load Failed' : displayResult ? 'Recommendation' : 'Pending'}
                </Badge>
              </div>
            </div>
          </div>

        </div>
      </Card>

      {/* RESULT METRICS CARD */}
      <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-6">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <BarChart3 size={18} className="text-purple-400" />
            <h3 className="text-base font-bold text-white">Live Execution Metrics & Pipeline Info</h3>
          </div>
          <span className="text-xs font-mono text-slate-500">
            User ID: {simulationResult?.userId || 'USR001'}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Status */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800/80 space-y-1">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              Execution Status
            </span>
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${isCompleted ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`}></span>
              <span className="text-base font-bold text-white font-mono">{resultInfo.status}</span>
            </div>
          </div>

          {/* Processing Time */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800/80 space-y-1">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Clock size={12} className="text-blue-400" /> Latency
            </span>
            <span className="text-base font-bold text-blue-400 font-mono">{resultInfo.processingTime}</span>
          </div>

          {/* Strategy */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800/80 space-y-1">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Shirt size={12} className="text-purple-400" /> Recommendation Engine
            </span>
            <span className="text-xs font-bold text-slate-200 truncate block">
              {simulationResult?.strategy || 'RuleBased'} (v{simulationResult?.engineVersion || '1.0.0'})
            </span>
          </div>

          {/* Fit Match Confidence */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800/80 space-y-1">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Sparkles size={12} className="text-amber-400" /> Match Score
            </span>
            <span className="text-base font-bold text-emerald-400 font-mono">{resultInfo.confidence}</span>
          </div>

        </div>
      </Card>

      {/* TOP RECOMMENDATION DETAILS & MATCH REASONS */}
      {topRec && (
        <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <span className="text-[10px] font-mono uppercase text-indigo-400 font-bold">{topRec.brand} • {topRec.category}</span>
              <h3 className="text-lg font-bold text-white">{topRec.name}</h3>
            </div>
            <div className="text-right">
              <span className="text-lg font-bold text-emerald-400 font-mono">{topRec.currency || 'INR'} ₹{topRec.price}</span>
              <div className="flex items-center gap-1 text-xs text-amber-400 justify-end">
                <Star size={12} className="fill-amber-400" />
                <span>{topRec.rating || 4.5} Rating</span>
              </div>
            </div>
          </div>

          {/* Match Reasons Badges */}
          {topRec.reasons && topRec.reasons.length > 0 && (
            <div className="space-y-2 pt-1">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1">
                <Tag size={12} className="text-blue-400" /> Recommendation Match Factors ({topRec.reasons.length}):
              </span>
              <div className="flex flex-wrap gap-2 pt-1">
                {topRec.reasons.map((reason, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg bg-indigo-950/60 border border-indigo-800/60 text-indigo-200 text-xs flex items-center gap-1.5"
                  >
                    <CheckCircle2 size={12} className="text-indigo-400 shrink-0" />
                    {reason}
                  </span>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* ALL RECOMMENDATIONS LIST */}
      {recommendations.length > 1 && (
        <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h3 className="text-base font-bold text-white border-b border-slate-800 pb-3">
            Other Recommended Garments ({recommendations.length - 1})
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {recommendations.slice(1).map((item) => (
              <div
                key={item.productId}
                className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-2 flex flex-col justify-between"
              >
                <div className="flex gap-3 items-center">
                  <img
                    src={item.image}
                    alt={item.name}
                    className="w-14 h-14 rounded-lg object-cover bg-slate-900 shrink-0"
                    onError={(e) => {
                      e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="%230f172a"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%2364748b" font-size="12" font-family="sans-serif">Item</text></svg>';
                    }}
                  />
                  <div className="min-w-0 flex-1">
                    <span className="text-[10px] font-mono text-indigo-400 block uppercase">{item.brand}</span>
                    <h5 className="text-xs font-bold text-white truncate">{item.name}</h5>
                    <span className="text-xs font-mono text-emerald-400 font-semibold">₹{item.price}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-900">
                  <span className="text-amber-400 font-mono flex items-center gap-1">★ {item.rating || 4.5}</span>
                  <span className="text-emerald-400 font-bold font-mono">{item.score?.toFixed(0)}% Score</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* ACTION BUTTONS: Download | Try Another | Share */}
      <div className="glass-card p-4 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Button
            variant="primary"
            size="md"
            leftIcon={<Download size={18} />}
            onClick={handleDownloadReport}
          >
            Download Report
          </Button>

          <Button
            variant="secondary"
            size="md"
            leftIcon={<Share2 size={18} />}
            onClick={() => setIsShareModalOpen(true)}
          >
            Share
          </Button>
        </div>

        <Button
          variant="outline"
          size="md"
          leftIcon={<RefreshCw size={16} />}
          onClick={() => navigate('/upload')}
        >
          Try Another Garment
        </Button>
      </div>

      {/* Share Modal */}
      <Modal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        title="Share Simulation Result"
      >
        <div className="space-y-4 py-2">
          <p className="text-xs text-slate-300">
            Copy link below to share this virtual wear simulation result:
          </p>
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs font-mono text-slate-400 truncate">
            http://localhost:5173/share/{isCompleted ? simulationResult?.userId : 'USR001'}
          </div>
          <div className="flex justify-end pt-2">
            <Button variant="secondary" size="sm" onClick={() => setIsShareModalOpen(false)}>
              Close
            </Button>
          </div>
        </div>
      </Modal>

    </div>
  );
}

