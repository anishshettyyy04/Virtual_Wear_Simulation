import { Check } from 'lucide-react';

const PRESET_GARMENTS = [
  {
    id: 'g1',
    title: 'Urban Denim Jacket',
    category: 'Outerwear',
    previewUrl: 'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&q=80&w=400',
  },
  {
    id: 'g2',
    title: 'Casual Cotton Hoodie',
    category: 'Sweatshirts',
    previewUrl: 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&q=80&w=400',
  },
  {
    id: 'g3',
    title: 'Floral Summer Dress',
    category: 'Dresses',
    previewUrl: 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&q=80&w=400',
  },
  {
    id: 'g4',
    title: 'Classic White Linen Tee',
    category: 'T-Shirts',
    previewUrl: 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&q=80&w=400',
  },
];

export const GarmentSelector = ({ selectedGarment, onSelectGarment }) => {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
          Or Select Preset Garment
        </span>
        <span className="text-[11px] text-slate-500 font-mono">4 Demo Presets</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {PRESET_GARMENTS.map((garment) => {
          const isSelected = selectedGarment?.id === garment.id;
          return (
            <button
              key={garment.id}
              type="button"
              onClick={() =>
                onSelectGarment({
                  id: garment.id,
                  title: garment.title,
                  previewUrl: garment.previewUrl,
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
                src={garment.previewUrl}
                alt={garment.title}
                className="w-12 h-12 rounded-lg object-cover bg-slate-950"
              />
              <div className="flex-1 min-w-0">
                <h5 className="text-xs font-bold text-white truncate">{garment.title}</h5>
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
    </div>
  );
};
