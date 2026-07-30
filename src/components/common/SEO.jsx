import { useEffect } from 'react';

export const SEO = ({ title, description }) => {
  useEffect(() => {
    if (title) {
      document.title = `${title} | Virtual Wear AI`;
    }
    if (description) {
      const meta = document.querySelector('meta[name="description"]');
      if (meta) meta.setAttribute('content', description);
    }
  }, [title, description]);

  return null;
};
