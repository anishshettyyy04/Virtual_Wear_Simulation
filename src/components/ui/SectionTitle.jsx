import { Badge } from './Badge';

export const SectionTitle = ({
  badge,
  title,
  subtitle,
  center = true,
  className = '',
}) => {
  return (
    <div className={`mb-12 ${center ? 'text-center max-w-2xl mx-auto' : ''} ${className}`}>
      {badge && <Badge variant="primary" className="mb-3">{badge}</Badge>}
      <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight mb-3">
        {title}
      </h2>
      {subtitle && <p className="text-sm md:text-base text-slate-400 leading-relaxed">{subtitle}</p>}
    </div>
  );
};
