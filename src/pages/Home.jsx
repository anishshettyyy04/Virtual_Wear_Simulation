import { SEO } from '@/components/common/SEO';
import { HeroSection } from '@/features/home/HeroSection';
import { FeatureGrid } from '@/features/home/FeatureGrid';
import { WorkflowSteps } from '@/features/home/WorkflowSteps';
import { TechSpecs } from '@/features/home/TechSpecs';
import { CTASection } from '@/features/home/CTASection';

export default function Home() {
  return (
    <div className="space-y-12">
      <SEO
        title="Home"
        description="Experience realistic 3D virtual apparel try-on with AI pose alignment and fabric simulation."
      />
      <HeroSection />
      <FeatureGrid />
      <WorkflowSteps />
      <TechSpecs />
      <CTASection />
    </div>
  );
}
