import { Cpu, Shirt, Sliders, LineChart, Sparkles, Layers } from 'lucide-react';
import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { SectionTitle } from '@/components/ui/SectionTitle';

export const FeatureGrid = () => {
  const features = [
    {
      icon: Cpu,
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-500/10',
      title: 'Neural Pose Fitting',
      description: 'Advanced computer vision aligns garments to complex body postures, shoulder slopes, and torso contours.',
    },
    {
      icon: Shirt,
      color: 'text-pink-400',
      bgColor: 'bg-pink-500/10',
      title: 'High-Fidelity Garment Drape',
      description: 'Simulates real fabric tension, wrinkles, shadows, and textures across cotton, silk, denim, and wool.',
    },
    {
      icon: Sliders,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      title: 'Custom Fit Controls',
      description: 'Adjust fit parameters from slim, regular, to relaxed and oversized with instant visual feedback.',
    },
    {
      icon: LineChart,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      title: 'Fit Confidence Analytics',
      description: 'Receive algorithmic confidence scores on chest width, waist drape, and sleeve alignment.',
    },
    {
      icon: Sparkles,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      title: 'Before & After Comparison',
      description: 'Interactive split-screen slider to inspect original avatar alongside the simulated virtual try-on render.',
    },
    {
      icon: Layers,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      title: 'Modular API Architecture',
      description: 'Built ready to interface with Python AI microservices, PyTorch diffusion models, or OpenCV pipelines.',
    },
  ];

  return (
    <section className="py-12 border-t border-slate-900">
      <SectionTitle
        badge="Platform Capabilities"
        title="Engineered for High-Accuracy Virtual Apparel"
        subtitle="Explore the core technologies powering photorealistic virtual try-on simulation."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((item, idx) => {
          const Icon = item.icon;
          return (
            <Card key={idx} className="group">
              <CardHeader className="border-none pb-0">
                <div className={`w-12 h-12 rounded-2xl ${item.bgColor} ${item.color} flex items-center justify-center mb-4 transition-transform group-hover:scale-110`}>
                  <Icon size={24} />
                </div>
                <h3 className="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors">
                  {item.title}
                </h3>
              </CardHeader>
              <CardBody>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {item.description}
                </p>
              </CardBody>
            </Card>
          );
        })}
      </div>
    </section>
  );
};
