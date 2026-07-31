import { useState } from 'react';
import { useNavigate } from 'react';
import { Upload as UploadIcon, ArrowRight, RefreshCw, Image as ImageIcon } from 'lucide-react';
import { SEO } from '@/components/common/SEO';
import { SectionTitle } from '@/components/ui/SectionTitle';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ImageUploadSection } from '@/features/upload/ImageUploadSection';
import { UploadInfo } from '@/components/upload/UploadInfo';

export default function Upload() {
  const navigate = useNavigate();
  const [, setUploadedImageInfo] = useState(null);


  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <SEO
        title="Upload Image"
        description="Upload model avatar or garment photo for Virtual Wear AI fitting simulation."
      />

      <SectionTitle
        badge="Upload Station"
        title="Upload Image Interface"
        subtitle="Frontend upload UI supporting drag and drop, instant preview, file validation, and format checking."
      />

      {/* Main 2-Panel Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* LEFT PANEL: Interactive Upload Section */}
        <div className="lg:col-span-7 space-y-6">
          <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold">
                  <UploadIcon size={18} />
                </div>
                <h3 className="text-base font-bold text-white">Image Upload Portal</h3>
              </div>
              <Badge variant="primary" size="sm">
                Interactive Memory Upload
              </Badge>
            </div>

            {/* Interactive Image Upload Area */}
            <ImageUploadSection onImageChange={setUploadedImageInfo} />

            {/* CTA to view sample Result page */}
            <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400 border-t border-slate-800/80">
              <span>Ready to inspect the comparison interface?</span>
              <Button
                variant="outline"
                size="sm"
                rightIcon={<ArrowRight size={14} />}
                onClick={() => navigate('/result')}
              >
                Proceed to Result Page
              </Button>
            </div>
          </Card>
        </div>

        {/* RIGHT PANEL: Guidelines, Information & Specs */}
        <div className="lg:col-span-5 space-y-6">
          <UploadInfo />

          {/* Recent Upload Mock Placeholder */}
          <Card hover={false} className="border border-slate-800 bg-slate-900/60 p-6 space-y-4">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center justify-between">
              <span>Preset Sample Avatars</span>
              <RefreshCw size={12} className="text-slate-500" />
            </h4>

            <p className="text-xs text-slate-400">
              Or pick one of our sample model avatars to test fitting speed:
            </p>

            <div className="grid grid-cols-3 gap-2">
              {[1, 2, 3].map((item) => (
                <div
                  key={item}
                  className="aspect-square rounded-xl bg-slate-950 border border-slate-800/80 flex flex-col items-center justify-center p-2 text-slate-500 hover:border-blue-500/50 hover:text-blue-400 transition-colors cursor-pointer group"
                >
                  <ImageIcon size={20} className="mb-1 group-hover:scale-110 transition-transform" />
                  <span className="text-[9px] font-mono text-slate-400">Model #{item}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

      </div>
    </div>
  );
}
