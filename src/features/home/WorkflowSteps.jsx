import { UploadCloud, SlidersHorizontal, PlayCircle, CheckCircle2 } from 'lucide-react';
import { SectionTitle } from '@/components/ui/SectionTitle';

export const WorkflowSteps = () => {
  const steps = [
    {
      step: '01',
      icon: UploadCloud,
      title: 'Upload Avatar & Garment',
      desc: 'Drag and drop your model photo and chosen apparel garment into the upload dropzones.',
    },
    {
      step: '02',
      icon: SlidersHorizontal,
      title: 'Configure Fit Settings',
      desc: 'Select desired fit profile (regular, slim, oversized), pose mode, and fabric weight.',
    },
    {
      step: '03',
      icon: PlayCircle,
      title: 'Run AI Simulation',
      desc: 'The neural network extracts pose landmarks and warps the garment mesh seamlessly.',
    },
    {
      step: '04',
      icon: CheckCircle2,
      title: 'Inspect & Export Result',
      desc: 'Compare before/after try-on visuals, inspect fit metrics, and download HD renders.',
    },
  ];

  return (
    <section id="workflow-section" className="py-12 border-t border-slate-900">
      <SectionTitle
        badge="4-Step Process"
        title="Simple Workflow, Professional Output"
        subtitle="How Virtual Wear AI transforms raw apparel photos into photorealistic virtual try-ons."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {steps.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="relative glass-card rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-3xl font-black text-indigo-500/40 font-display">
                    {item.step}
                  </span>
                  <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-indigo-400">
                    <Icon size={20} />
                  </div>
                </div>
                <h3 className="text-base font-bold text-white mb-2">{item.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
