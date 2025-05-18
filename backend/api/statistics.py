import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import requests
import os
import folium
from folium.plugins import MarkerCluster
from pymongo import MongoClient
from datetime import datetime
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

def get_geo_data(ip):
    """Get geographical data for an IP address using ipinfo.io"""
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        if response.status_code == 200:
            data = response.json()
            return data.get('loc', '')
        return ''
    except Exception as e:
        print(f"Error getting geo data for IP {ip}: {str(e)}")
        return ''

def load_data_from_mongodb(app):
    """Load data from MongoDB into pandas DataFrame"""
    try:
        # Get all records from the visits collection
        cursor = app.data_collection.find({})
        data = list(cursor)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Update geo data for records with missing coordinates
        for index, row in df.iterrows():
            if not row.get('geo') or row.get('geoAccuracy') == '—' or row.get('geoAccuracy') == '':
                ip = row.get('ip')
                if ip:
                    geo_data = get_geo_data(ip)
                    if geo_data:
                        df.at[index, 'geo'] = geo_data
        
        return df
    except Exception as e:
        print(f"Error loading data from MongoDB: {str(e)}")
        return pd.DataFrame()

def create_map_visualization(df, output_pattern):
    """Create a map visualization of visitor locations"""
    try:
        # Create a map centered at a default location
        m = folium.Map(location=[0, 0], zoom_start=2)
        
        # Add a marker cluster
        marker_cluster = MarkerCluster().add_to(m)
        
        # Count occurrences of each location
        location_counts = {}
        
        for _, row in df.iterrows():
            geo = row.get('geo')
            if geo and ',' in geo:
                try:
                    lat, lon = map(float, geo.split(','))
                    location_key = f"{lat},{lon}"
                    location_counts[location_key] = location_counts.get(location_key, 0) + 1
                except ValueError:
                    continue
        
        # Add markers for each location
        for loc_key, count in location_counts.items():
            try:
                lat, lon = map(float, loc_key.split(','))
                popup_text = f"Visits: {count}"
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_text,
                    icon=folium.Icon(color='blue')
                ).add_to(marker_cluster)
            except ValueError:
                continue
        
        # Save the map
        map_file = output_pattern.format(3)
        m.save(map_file)
        
        return True
    except Exception as e:
        print(f"Error creating map visualization: {str(e)}")
        return False

def create_language_chart(df, output_pattern):
    """Create a bar chart of visitor languages"""
    try:
        # Get unique visitors by IP
        unique_df = df.drop_duplicates(subset=['ip'])
        
        # Count languages
        language_counts = unique_df['language'].value_counts()
        
        plt.figure(figsize=(12, 6))
        language_counts.plot(kind='bar')
        plt.title('Languages of Unique Visitors')
        plt.xlabel('Language')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig(output_pattern.format(4))
        plt.close()
        
        return True
    except Exception as e:
        print(f"Error creating language chart: {str(e)}")
        return False

def create_screen_resolution_chart(df, output_pattern):
    """Create a bar chart of screen resolutions"""
    try:
        # Get unique visitors by IP
        unique_df = df.drop_duplicates(subset=['ip'])
        
        # Count screen resolutions
        screen_counts = unique_df['screen'].value_counts().head(10)  # Top 10 resolutions
        
        plt.figure(figsize=(12, 6))
        screen_counts.plot(kind='bar')
        plt.title('Screen Resolutions of Unique Visitors (Top 10)')
        plt.xlabel('Resolution')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_pattern.format(5))
        plt.close()
        
        return True
    except Exception as e:
        print(f"Error creating screen resolution chart: {str(e)}")
        return False

def create_os_visualization(df, output_pattern):
    """Create visualization of operating systems"""
    try:
        # Get unique visitors by IP
        unique_df = df.drop_duplicates(subset=['ip'])
        
        # Define OS categories and their patterns
        os_categories = {
            'Windows': ['Win32', 'Win64', 'Win16', 'WinCE', 'Windows'],
            'Mac': ['MacIntel', 'MacPPC', 'Mac68K', 'Mac', 'macOS'],
            'Linux': ['Linux x86_64', 'Linux i686', 'Linux armv7l', 'Linux armv81', 'Linux'],
            'iOS': ['iPhone', 'iPad', 'iPod', 'iOS'],
            'Android': ['Android'],
            'Other': ['SunOS', 'HP-UX']
        }
        
        # Categorize platforms
        def categorize_os(platform):
            for category, patterns in os_categories.items():
                if any(pattern in platform for pattern in patterns):
                    return category
            return 'Other'
        
        unique_df['os_category'] = unique_df['platform'].apply(categorize_os)
        os_counts = unique_df['os_category'].value_counts()
        
        # Create figure with OS icons
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Define positions for each OS category
        categories = list(os_categories.keys())
        positions = np.arange(len(categories))
        
        # Create bars
        bars = ax.bar(positions, [os_counts.get(cat, 0) for cat in categories])
        
        # Add percentages and counts
        total = os_counts.sum()
        for i, bar in enumerate(bars):
            count = os_counts.get(categories[i], 0)
            percentage = (count / total) * 100 if total > 0 else 0
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                   f"{percentage:.1f}%\n({count})",
                   ha='center', va='bottom')
        
        ax.set_xticks(positions)
        ax.set_xticklabels(categories)
        ax.set_title('Operating Systems of Unique Visitors')
        ax.set_ylabel('Count')
        
        plt.tight_layout()
        plt.savefig(output_pattern.format(6))
        plt.close()
        
        return True
    except Exception as e:
        print(f"Error creating OS visualization: {str(e)}")
        return False

def create_browser_visualization(df, output_pattern):
    """Create visualization of browsers"""
    try:
        # Get unique visitors by IP
        unique_df = df.drop_duplicates(subset=['ip'])
        
        # Count browsers
        browser_counts = unique_df['browserName'].value_counts()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Create bars
        positions = np.arange(len(browser_counts))
        bars = ax.bar(positions, browser_counts.values)
        
        # Add percentages and counts
        total = browser_counts.sum()
        for i, bar in enumerate(bars):
            count = browser_counts.values[i]
            percentage = (count / total) * 100
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                   f"{percentage:.1f}%\n({count})",
                   ha='center', va='bottom')
        
        ax.set_xticks(positions)
        ax.set_xticklabels(browser_counts.index)
        ax.set_title('Browsers of Unique Visitors')
        ax.set_ylabel('Count')
        
        plt.tight_layout()
        plt.savefig(output_pattern.format(7))
        plt.close()
        
        return True
    except Exception as e:
        print(f"Error creating browser visualization: {str(e)}")
        return False

def create_media_devices_table(df, output_pattern):
    """Create table of media devices access"""
    try:
        # Get unique visitors by IP
        unique_df = df.drop_duplicates(subset=['ip'])
        
        # Extract media device information
        media_data = {
            'Device': ['Speakers', 'Microphones', 'Webcams'],
            'Count': [0, 0, 0],
            'Percentage': [0, 0, 0]
        }
        
        total_visitors = len(unique_df)
        
        if 'multimediaDevices' in unique_df.columns:
            # Count devices
            speakers_count = unique_df['multimediaDevices'].apply(
                lambda x: x.get('speakers', 0) > 0 if isinstance(x, dict) else False
            ).sum()
            
            micros_count = unique_df['multimediaDevices'].apply(
                lambda x: x.get('micros', 0) > 0 if isinstance(x, dict) else False
            ).sum()
            
            webcams_count = unique_df['multimediaDevices'].apply(
                lambda x: x.get('webcams', 0) > 0 if isinstance(x, dict) else False
            ).sum()
            
            # Update data
            media_data['Count'] = [speakers_count, micros_count, webcams_count]
            media_data['Percentage'] = [
                (speakers_count / total_visitors) * 100 if total_visitors > 0 else 0,
                (micros_count / total_visitors) * 100 if total_visitors > 0 else 0,
                (webcams_count / total_visitors) * 100 if total_visitors > 0 else 0
            ]
        
        # Create table
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('tight')
        ax.axis('off')
        
        # Format percentage values
        formatted_percentages = [f"{p:.1f}%" for p in media_data['Percentage']]
        
        table_data = [
            media_data['Device'],
            media_data['Count'],
            formatted_percentages
        ]
        
        table = ax.table(
            cellText=list(zip(*table_data)),
            colLabels=['Device', 'Count', 'Percentage'],
            loc='center',
            cellLoc='center'
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.5)
        
        plt.title('Media Devices Access')
        plt.savefig(output_pattern.format(8))
        plt.close()
        
        return True
    except Exception as e:
        print(f"Error creating media devices table: {str(e)}")
        return False

def generate_statistics_images(stats_data, output_pattern):
    """Generate visualization images from statistics data"""
    try:
        # Basic period statistics visualizations
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

        # Pie chart for period distribution
        plt.figure(figsize=(8, 8))
        plt.pie(totals, labels=periods, autopct='%1.1f%%')
        plt.title('Visits Distribution')
        plt.savefig(output_pattern.format(2))
        plt.close()
        
        # Get app from current context if available
        from flask import current_app
        app = current_app._get_current_object()
        
        # Load data from MongoDB
        df = load_data_from_mongodb(app)
        
        if not df.empty:
            # Create additional visualizations
            create_map_visualization(df, output_pattern)
            create_language_chart(df, output_pattern)
            create_screen_resolution_chart(df, output_pattern)
            create_os_visualization(df, output_pattern)
            create_browser_visualization(df, output_pattern)
            create_media_devices_table(df, output_pattern)

    except Exception as e:
        print(f"Error generating images: {str(e)}")