#!/usr/bin/env python3
"""
Recommendation Engine Benchmarking & Performance Analytics Exporter
Virtual Wear Simulation — Phase 1.3 Optimization
"""

import json
import os
import sys
import time

# Ensure backend directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommendation.analytics import (
    compute_average_recommendation_score,
    compute_category_popularity,
    compute_most_recommended_products,
    compute_recommendation_frequency,
    compute_user_preference_distribution
)
from recommendation.engine import RecommendationEngine


def run_benchmark():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    users_file = os.path.join(base_dir, 'data', 'user_preferences.json')
    products_file = os.path.join(base_dir, 'data', 'products.json')
    metrics_output_file = os.path.join(base_dir, 'data', 'recommendation_metrics.json')

    if not os.path.exists(users_file) or not os.path.exists(products_file):
        print("ERROR: Seed datasets missing. Run setup first.")
        sys.exit(1)

    with open(users_file, 'r', encoding='utf-8') as f:
        users = json.load(f)

    with open(products_file, 'r', encoding='utf-8') as f:
        products = json.load(f)

    engine = RecommendationEngine(products_file=products_file, users_file=users_file)

    user_ids = [u['userId'] for u in users]
    iterations = 2  # Run twice (uncached pass + cached pass)
    total_runs = len(user_ids) * iterations

    all_recommendation_results = []
    start_benchmark_time = time.perf_counter()

    for run_pass in range(iterations):
        for uid in user_ids:
            res = engine.generate_recommendations(uid, limit=10)
            all_recommendation_results.append(res)

    total_duration_sec = time.perf_counter() - start_benchmark_time
    avg_latency_ms = round((total_duration_sec / total_runs) * 1000, 2)
    recs_per_sec = round(total_runs / max(total_duration_sec, 0.001), 1)

    cache_stats = engine.cache.get_stats()

    # Compute Analytics
    top_recommended = compute_most_recommended_products(all_recommendation_results, top_n=5)
    avg_score = compute_average_recommendation_score(all_recommendation_results)
    cat_popularity = compute_category_popularity(all_recommendation_results)
    rec_freq = compute_recommendation_frequency(all_recommendation_results)
    user_dist = compute_user_preference_distribution(users)

    metrics_payload = {
        "benchmarkSummary": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "usersTested": len(user_ids),
            "totalRuns": total_runs,
            "totalDurationSec": round(total_duration_sec, 4),
            "averageLatencyMs": avg_latency_ms,
            "recommendationsPerSecond": recs_per_sec,
            "productsProcessed": len(products),
            "cacheStats": cache_stats
        },
        "analytics": {
            "averageRecommendationScore": avg_score,
            "mostRecommendedProducts": top_recommended,
            "categoryPopularity": cat_popularity,
            "recommendationFrequency": rec_freq,
            "userPreferenceDistribution": user_dist
        }
    }

    # Save metrics export JSON
    os.makedirs(os.path.dirname(metrics_output_file), exist_ok=True)
    with open(metrics_output_file, 'w', encoding='utf-8') as f:
        json.dump(metrics_payload, f, indent=2)

    # Print Console Summary
    print("\nRecommendation Benchmark\n")
    print(f"Users Tested: {len(user_ids)}\n")
    print(f"Average Latency: {avg_latency_ms} ms\n")
    print(f"Products Processed: {len(products)}\n")
    print(f"Recommendations/sec: {recs_per_sec}\n")
    print(f"Cache Hit Rate: {cache_stats['hitRatePercent']}%\n")
    print("SUCCESS\n")


if __name__ == '__main__':
    run_benchmark()
