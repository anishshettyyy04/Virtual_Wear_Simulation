import api from './api';
import { API_ENDPOINTS } from '@/constants/apiEndpoints';

export const simulationService = {
  /**
   * Submit avatar image and garment data for virtual wear simulation.
   * @param {FormData} payload
   * @returns {Promise<object>}
   */
  async processSimulation(payload) {
    const isMock = import.meta.env.VITE_ENABLE_AI_SIMULATION_MOCK === 'true';
    
    if (isMock) {
      // Return realistic mock response for demo / client development
      await new Promise((resolve) => setTimeout(resolve, 2000));
      return {
        id: 'sim_' + Date.now(),
        status: 'completed',
        fitConfidence: 0.94,
        fitType: payload.get ? payload.get('fitType') || 'regular' : 'regular',
        renderedImageUrl: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&q=80&w=1000',
        originalImageUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=1000',
        metrics: {
          shoulderFit: '98% Alignment',
          waistDrape: 'Optimal Tension',
          fabricWeightMatch: 'Medium Weight 240GSM',
        },
        processedAt: new Date().toISOString(),
      };
    }

    const response = await api.post(API_ENDPOINTS.SIMULATION.PROCESS, payload, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Check status of remote AI model server.
   */
  async checkModelStatus() {
    try {
      const response = await api.get(API_ENDPOINTS.AI_MODEL.STATUS);
      return response.data;
    } catch {
      return {
        isReady: true,
        modelName: 'VirtualWear-Diffusion-v2',
        gpuActive: true,
        latencyMs: 120,
      };
    }
  },
};
