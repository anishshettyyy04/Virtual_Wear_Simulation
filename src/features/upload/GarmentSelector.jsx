import { useState, useEffect } from 'react';
import { Check, Loader2, AlertCircle } from 'lucide-react';
import { simulationService } from '@/services/simulationService';

export const GarmentSelector = ({ selectedGarment, onSelectGarment }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const data = await simulationService.getProducts();
        if (isMounted) {
          setProducts(data);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          const errorMsg = typeof err === 'object' ? (err.message || 'Failed to load garments.') : String(err);
          setError(errorMsg);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchProducts();
    return () => { isMounted = false; };
  }, []);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
          Or Select Preset Garment
        </span>
        <span className="text-[11px] text-slate-500 font-mono">
          {loading ? 'Loading...' : `${products.length} Items Available`}
        </span>
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center p-6 bg-slate-900/40 rounded-xl border border-slate-800">
          <Loader2 size={24} className="text-blue-500 animate-spin mb-2" />
          <span className="text-xs text-slate-400">Loading catalog...</span>
        </div>
      )}

      {error && !loading && (
        <div className="flex flex-col items-center justify-center p-6 bg-rose-950/20 rounded-xl border border-rose-900/30">
          <AlertCircle size={24} className="text-rose-500 mb-2" />
          <span className="text-xs text-rose-400 text-center">{typeof error === 'object' ? (error?.message || JSON.stringify(error)) : String(error)}</span>
        </div>
      )}

      {!loading && !error && products.length === 0 && (
        <div className="flex flex-col items-center justify-center p-6 bg-slate-900/40 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400">No garments available in catalog.</span>
        </div>
      )}

      {!loading && !error && products.length > 0 && (
        <div className="grid grid-cols-2 gap-3 max-h-[300px] overflow-y-auto pr-1 pb-1 custom-scrollbar">
          {products.map((garment) => {
            const isSelected = selectedGarment?.id === garment.id;
            return (
              <button
                key={garment.id}
                type="button"
                onClick={() =>
                  onSelectGarment({
                    id: garment.id,
                    title: garment.name,
                    previewUrl: garment.image,
                    file: null,
                  })
                }
                className={`relative rounded-xl overflow-hidden border text-left p-2 transition-all flex items-center gap-3 ${
                  isSelected
                    ? 'bg-indigo-600/10 border-indigo-500 shadow-md shadow-indigo-600/20'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <img
                  src={garment.image}
                  alt={garment.name}
                  className="w-12 h-12 rounded-lg object-cover bg-slate-950"
                  onError={(e) => {
                    e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="300" height="400" viewBox="0 0 300 400"><rect width="300" height="400" fill="%230f172a"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%2364748b" font-size="14" font-family="sans-serif">Garment Thumbnail</text></svg>';
                  }}
                />
                <div className="flex-1 min-w-0">
                  <h5 className="text-xs font-bold text-white truncate">{garment.name}</h5>
                  <span className="text-[10px] text-slate-400">{garment.category}</span>
                </div>
                {isSelected && (
                  <div className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center shrink-0 mr-1">
                    <Check size={12} />
                  </div>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
