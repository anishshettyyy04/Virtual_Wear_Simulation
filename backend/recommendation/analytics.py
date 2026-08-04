"""
Recommendation Analytics & Metrics Module
Virtual Wear Simulation — Phase 1.3
"""


def compute_most_recommended_products(recommendations_list, top_n=5):
    """
    Computes top N most frequently recommended products across multiple recommendation runs.
    """
    freq = {}
    for run in recommendations_list:
        recs = run.get('recommendations', []) if isinstance(run, dict) else run
        for item in recs:
            pid = item.get('productId') if isinstance(item, dict) else item
            if pid:
                freq[pid] = freq.get(pid, 0) + 1

    sorted_pids = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return sorted_pids[:top_n]


def compute_average_recommendation_score(recommendations):
    """
    Calculates average normalized score for a list of recommendations.
    """
    recs = recommendations.get('recommendations', []) if isinstance(recommendations, dict) else recommendations
    if not recs:
        return 0.0
    scores = [item.get('score', 0.0) for item in recs]
    return round(sum(scores) / len(scores), 2)


def compute_category_popularity(recommendations):
    """
    Computes category breakdown distribution across recommended items.
    """
    recs = recommendations.get('recommendations', []) if isinstance(recommendations, dict) else recommendations
    counts = {}
    for item in recs:
        cat = item.get('category', 'unknown')
        counts[cat] = counts.get(cat, 0) + 1
    return counts


def compute_recommendation_frequency(recommendations_list):
    """
    Computes item appearance frequency across multiple user recommendation runs.
    """
    total_runs = len(recommendations_list)
    if total_runs == 0:
        return {}

    freq = {}
    for run in recommendations_list:
        recs = run.get('recommendations', []) if isinstance(run, dict) else run
        for item in recs:
            pid = item.get('productId') if isinstance(item, dict) else item
            if pid:
                freq[pid] = freq.get(pid, 0) + 1

    return {pid: round(count / total_runs, 4) for pid, count in freq.items()}


def compute_user_preference_distribution(user_profiles):
    """
    Computes demographic and category distribution statistics from user preference profiles.
    """
    total_users = len(user_profiles)
    if total_users == 0:
        return {}

    genders = {}
    styles = {}
    categories = {}

    for user in user_profiles:
        g = user.get('gender', 'unknown')
        genders[g] = genders.get(g, 0) + 1

        for s in user.get('preferredStyles', []):
            styles[s] = styles.get(s, 0) + 1

        for c in user.get('preferredCategories', []):
            categories[c] = categories.get(c, 0) + 1

    return {
        "totalUsers": total_users,
        "genderDistribution": genders,
        "styleDistribution": styles,
        "categoryDistribution": categories
    }
