import matplotlib.pyplot as plt
import os

def generate_statistics_images(stats_data, output_pattern):
    """Generate visualization images from statistics data"""
    try:
        # Example visualization 1: Period statistics bar chart
        periods = list(stats_data['periodStats'].keys())
        totals = [v['total'] for v in stats_data['periodStats'].values()]
        uniques = [v['unique'] for v in stats_data['periodStats'].values()]

        plt.figure(figsize=(10, 6))
        plt.bar(periods, totals, label='Total Visits')
        plt.bar(periods, uniques, label='Unique Visitors')
        plt.title('Visitors Statistics')
        plt.legend()
        plt.savefig(output_pattern.format(1))
        plt.close()

        # Example visualization 2: Pie chart for period distribution
        plt.figure(figsize=(8, 8))
        plt.pie(totals, labels=periods, autopct='%1.1f%%')
        plt.title('Visits Distribution')
        plt.savefig(output_pattern.format(2))
        plt.close()

    except Exception as e:
        print(f"Error generating images: {str(e)}")