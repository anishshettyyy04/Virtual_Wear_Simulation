import { Upload, Shirt, Sparkles, Download } from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { SectionTitle } from '@/components/ui/SectionTitle';

export const FeatureGrid = () => {
  const featureCards = [
    {
      id: 1,
      title: 'Upload Your Photo',
      description: 'Upload a clear full-body or half-body portrait photo to serve as your virtual avatar base model.',
      icon: Upload,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      badge: 'Step 1',
    },
    {
      id: 2,
      title: 'Choose Clothing',
      description: 'Select your preferred garment from custom uploads or choose from preset apparel designs.',
      icon: Shirt,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      badge: 'Step 2',
    },
    {
      id: 3,
      title: 'AI Virtual Try-On',
      description: 'Our neural simulation Engine aligns posture, drapes fabric physics, and renders instant fitting.',
      icon: Sparkles,
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-500/10',
      badge: 'Step 3',
    },
    {
      id: 4,
      title: 'Download Result',
      description: 'Inspect the side-by-side virtual try-on comparison render and export high-resolution output files.',
      icon: Download,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      badge: 'Step 4',
    },
  ];

  return (
    <section className="py-10 border-t border-slate-900">
      <SectionTitle
        badge="Core Features"
        title="Everything You Need for Virtual Fitting"
        subtitle="Explore the 4 key feature capabilities powering our AI Virtual Wear Simulation."
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {featureCards.map((card) => {
          const Icon = card.icon;
          return (
            <Card key={card.id} className="group relative flex flex-col justify-between h-full border border-slate-800">
              <CardHeader className="border-none pb-2">
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-2xl ${card.bgColor} ${card.color} flex items-center justify-center transition-transform group-hover:scale-110`}>
                    <Icon size={24} />
                  </div>
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700/60 font-mono">
                    {card.badge}
                  </span>
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition-colors">
                  {card.title}
                </h3>
              </CardHeader>
              <CardBody className="pt-0">
                <p className="text-xs text-slate-400 leading-relaxed">
                  {card.description}
                </p>
              </CardBody>
            </Card>
          );
        })}
      </div>
    </section>
  );
};
