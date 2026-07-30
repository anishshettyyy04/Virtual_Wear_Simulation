import { Upload, Shirt, Cpu, Eye, Download, ArrowDown, ArrowRight } from 'lucide-react';
import { SectionTitle } from '@/components/ui/SectionTitle';

export const WorkflowSteps = () => {
  const steps = [
    {
      id: 1,
      title: 'Upload',
      desc: 'Provide your target photo/avatar image.',
      icon: Upload,
      color: 'text-blue-400',
    },
    {
      id: 2,
      title: 'Select Outfit',
      desc: 'Choose garment apparel design.',
      icon: Shirt,
      color: 'text-purple-400',
    },
    {
      id: 3,
      title: 'AI Processing',
      desc: 'Neural pose alignment & mesh drape.',
      icon: Cpu,
      color: 'text-indigo-400',
    },
    {
      id: 4,
      title: 'Preview',
      desc: 'Inspect interactive split comparison render.',
      icon: Eye,
      color: 'text-pink-400',
    },
    {
      id: 5,
      title: 'Download',
      desc: 'Export high-resolution output file.',
      icon: Download,
      color: 'text-emerald-400',
    },
  ];

  return (
    <section id="workflow-section" className="py-10 border-t border-slate-900">
      <SectionTitle
        badge="Workflow"
        title="5-Step Simulation Pipeline"
        subtitle="Follow the step-by-step workflow to generate virtual wear simulations."
      />

      {/* Horizontal Flow for Desktop, Vertical Flow with Arrows for Mobile */}
      <div className="flex flex-col lg:flex-row items-center justify-between gap-4 max-w-5xl mx-auto">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const isLast = idx === steps.length - 1;

          return (
            <div key={step.id} className="flex flex-col lg:flex-row items-center w-full lg:w-auto">
              {/* Step Box */}
              <div className="glass-card p-5 rounded-2xl border border-slate-800 flex flex-col items-center text-center w-full lg:w-44 group hover:border-blue-500/40 transition-all">
                <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <Icon size={20} className={step.color} />
                </div>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-0.5">
                  Step 0{step.id}
                </span>
                <h4 className="text-sm font-bold text-white mb-1">{step.title}</h4>
                <p className="text-[11px] text-slate-400 leading-tight">{step.desc}</p>
              </div>

              {/* Arrow Connector (Down arrow on mobile, Right arrow on desktop) */}
              {!isLast && (
                <div className="py-3 lg:py-0 lg:px-2 text-blue-500/60 flex items-center justify-center shrink-0">
                  <ArrowDown size={20} className="lg:hidden animate-bounce" />
                  <ArrowRight size={20} className="hidden lg:block" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
};
