export const Card = ({ children, className = '', hover = true, ...props }) => {
  return (
    <div
      className={`glass-card rounded-2xl p-6 border border-slate-800/80 ${
        hover ? 'glass-card-hover' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className = '' }) => (
  <div className={`mb-4 pb-3 border-b border-slate-800/60 ${className}`}>{children}</div>
);

export const CardBody = ({ children, className = '' }) => (
  <div className={`${className}`}>{children}</div>
);

export const CardFooter = ({ children, className = '' }) => (
  <div className={`mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between ${className}`}>
    {children}
  </div>
);
