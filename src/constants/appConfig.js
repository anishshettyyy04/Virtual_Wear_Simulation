export const APP_CONFIG = {
  NAME: 'Virtual Wear AI',
  SLOGAN: 'Next-Generation AI Virtual Apparel Try-On',
  VERSION: '1.0.0',
  UPLOAD: {
    MAX_FILE_SIZE_MB: 10,
    MAX_FILE_SIZE_BYTES: 10 * 1024 * 1024,
    ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
    ALLOWED_EXTENSIONS: ['.jpg', '.jpeg', '.png', '.webp'],
  },
  SIMULATION_DEFAULTS: {
    FIT_TYPE: 'regular', // slim, regular, relaxed, oversized
    POSE_MODE: 'auto_align', // auto_align, strict_pose, full_body
    FABRIC_WEIGHT: 'medium', // light, medium, heavy
    RESOLUTION: 'hd', // sd, hd, ultra
  },
  TEAM_MEMBERS: [
    { name: 'Lead AI Engineer', role: 'Computer Vision & Diffusion Models' },
    { name: 'Full Stack Architect', role: 'React Core & API Infrastructure' },
    { name: 'UX/UI Designer', role: 'Product Design & Ergonomics' },
    { name: 'Research Scientist', role: '3D Mesh Deformation' },
  ],
};
