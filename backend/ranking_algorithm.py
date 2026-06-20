import pandas as pd

def rank_zones_by_pickups(filepath):
    df = pd.read_csv(filepath)
    zone_counts = {}
    for zone in df['PULocationID']:
        if zone in zone_counts:
            zone_counts[zone] += 1
        else:
            zone_counts[zone] = 1
            zones = list(zone_counts.items())
    
    for i in range(len(zones)):
        for j in range(i + 1, len(zones)):
            if zones[j][1] > zones[i][1]:
                zones[i], zones[j] = zones[j], zones[i]
    
    return zones

if __name__ == "__main__":
    results = rank_zones_by_pickups("cleaned_enriched_data.csv")
    for rank, (zone, count) in enumerate(results, 1):
        print(f"Rank {rank}: Zone {zone} - {count} trips")