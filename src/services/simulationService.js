import api from './api';
import { API_ENDPOINTS } from '@/constants/apiEndpoints';

export const simulationService = {
  /**
   * Fetch all garments (products) from the backend.
   * @returns {Promise<Array>}
   */
  async getProducts() {
    const response = await api.get(API_ENDPOINTS.GARMENTS.LIST);
    const data = response.data?.data || response.data;
    return data || [];
  },

  /**
   * Execute AI Virtual Try-On Pipeline via POST /api/v1/tryon.
   * @param {Object} params - { personFile, garmentFile, garmentCategory, engine, sync }
   * @returns {Promise<Object>}
   */
  async executeTryOn({ personFile, garmentFile, garmentCategory = 'upper_body', engine = 'idm_vton', sync = true }) {
    const formData = new FormData();

    const pAttached = personFile instanceof File ? personFile : personFile?.file;
    if (pAttached) {
      formData.append('person_image', pAttached, pAttached.name || 'person.jpg');
    }

    const gAttached = garmentFile instanceof File ? garmentFile : garmentFile?.file;
    if (gAttached) {
      formData.append('garment_image', gAttached, gAttached.name || 'garment.jpg');
    }

    formData.append('garment_category', garmentCategory);
    formData.append('engine', engine);
    formData.append('sync', String(sync));

    const requestPayloadInfo = {
      person_image_filename: pAttached?.name || 'person.jpg',
      person_image_size: pAttached?.size || 0,
      garment_image_filename: gAttached?.name || 'garment.jpg',
      garment_image_size: gAttached?.size || 0,
      garment_category: garmentCategory,
      engine: engine,
      sync: sync,
    };

    console.log('[TRYON:REQUEST]', requestPayloadInfo);

    try {
      const response = await api.post(API_ENDPOINTS.SIMULATION.TRYON, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 180000, // 3 minutes — AI inference takes ~38s + upload/preprocessing
      });

      const result = response.data?.data || response.data;
      console.log('[TRYON:RESPONSE]', {
        status: response.status,
        hasData: Boolean(result),
        image_ref: result?.image_ref || 'MISSING',
        result_id: result?.result_id || 'MISSING',
        engine: result?.engine || 'MISSING',
        timings: result?.timings || null,
      });
      return result;
    } catch (err) {
      console.error('[TRYON:ERROR]', {
        message: err?.message || String(err),
        status: err?.response?.status,
        timeout: err?.code === 'ECONNABORTED',
      });
      throw err;
    }
  },

  /**
   * Request product recommendations for a user with context parameters.
   * @param {Object} params - { userId: string, limit?: number, forceRefresh?: boolean, selectedCategory?: string, selectedProductId?: string, selectedStyle?: string, selectedColor?: string }
   * @returns {Promise<object>}
   */
  async processSimulation({
    userId,
    limit = 10,
    forceRefresh = false,
    selectedCategory,
    selectedProductId,
    selectedStyle,
    selectedColor
  }) {
    if (!userId) {
      throw new Error('User ID is required for recommendations');
    }

    const jsonPayload = {
      userId,
      limit,
      forceRefresh,
      ...(selectedCategory && { selectedCategory }),
      ...(selectedProductId && { selectedProductId }),
      ...(selectedStyle && { selectedStyle }),
      ...(selectedColor && { selectedColor }),
    };

    const response = await api.post(API_ENDPOINTS.SIMULATION.PROCESS, jsonPayload);
    
    // Return the actual backend RecommendationResponse data
    return response.data?.data || response.data;
  },

  /**
   * Check status of backend API health.
   */
  async checkModelStatus() {
    try {
      const response = await api.get(API_ENDPOINTS.AI_MODEL.STATUS);
      const data = response.data?.data || response.data;
      return {
        isReady: data?.status === 'healthy' || data?.status === 'degraded',
        modelName: 'Backend System',
        details: data
      };
    } catch (error) {
      return {
        isReady: false,
        modelName: 'Backend System',
        error: typeof error === 'object' ? (error.message || 'Failed to connect to backend.') : String(error)
      };
    }
  },
};
