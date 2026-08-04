import { forwardRef } from 'react';

export const Input = forwardRef(
  (
    { label, helperText, error, leftIcon, rightIcon, className = '', id, type = 'text', ...props },
    ref
  ) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {leftIcon && (
            <div className="absolute left-3.5 text-slate-400 pointer-events-none">{leftIcon}</div>
          )}
          <input
            ref={ref}
            id={inputId}
            type={type}
            className={`w-full bg-slate-900/80 border ${
              error ? 'border-rose-500/80 focus:ring-rose-500' : 'border-slate-800 focus:border-indigo-500 focus:ring-indigo-500'
            } text-slate-100 placeholder-slate-500 text-sm rounded-xl py-2.5 ${
              leftIcon ? 'pl-10' : 'pl-3.5'
            } ${
              rightIcon ? 'pr-10' : 'pr-3.5'
            } transition-all outline-none focus:ring-1 ${className}`}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3.5 text-slate-400 pointer-events-none">{rightIcon}</div>
          )}
        </div>
        {error ? (
          <span className="text-xs text-rose-400 mt-0.5">{typeof error === 'object' ? (error?.message || JSON.stringify(error)) : String(error)}</span>
        ) : helperText ? (
          <span className="text-xs text-slate-400 mt-0.5">{helperText}</span>
        ) : null}
      </div>
    );
  }
);

Input.displayName = 'Input';
