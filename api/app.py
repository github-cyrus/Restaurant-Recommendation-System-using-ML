from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import os
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables
df = None
similarity_matrix = None

def load_data():
    """Load and preprocess the dataset"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(os.path.dirname(current_dir), 'dataset', 'restaurant.csv')
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Dataset not found at {csv_path}")
        
        # Read CSV and clean column names
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()  # Remove leading/trailing spaces from column names
        logger.info(f"Successfully loaded dataset with {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise

def preprocess_data(df):
    """Preprocess the dataset for better recommendations"""
    try:
        # Convert yes/no columns to binary
        binary_columns = ['homedelivery', 'smoking', 'alcohol', 'wifi', 'valetparking', 'rooftop']
        for col in binary_columns:
            df[f'{col}_binary'] = (df[col].str.strip().str.lower() == 'yes').astype(int)

        # Process cost column
        def extract_cost_value(cost_str):
            if pd.isna(cost_str):
                return 0
            cost_str = str(cost_str).replace('$', '').replace('₹', '').replace(',', '').replace('?', '').strip()
            match = re.search(r'(\d+(?:\.\d+)?)', cost_str)
            return float(match.group(1)) if match else 0

        df['cost_value'] = df['cost'].apply(extract_cost_value)
        
        # Normalize numerical values
        scaler = MinMaxScaler()
        df['normalized_cost'] = scaler.fit_transform(df[['cost_value']])
        df['normalized_rating'] = scaler.fit_transform(df[['rating']])

        # Create feature matrix for similarity calculation
        feature_cols = ['normalized_cost', 'normalized_rating'] + [f'{col}_binary' for col in binary_columns]
        feature_matrix = df[feature_cols].values
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(feature_matrix)
        
        logger.info("Successfully preprocessed data")
        return df, similarity_matrix
    except Exception as e:
        logger.error(f"Error preprocessing data: {str(e)}")
        raise

def get_recommendations(preferences, df, similarity_matrix):
    """Get personalized restaurant recommendations based on user preferences"""
    try:
        # Log incoming preferences
        logger.info(f"Received preferences: {preferences}")
        
        # Extract preferences
        cost_range = preferences.get('cost', '')
        cost_type = preferences.get('Cost_Type', '')
        min_rating = float(preferences.get('rating', 0))
        rating_type = preferences.get('rating_type', '')
        
        # Get amenity preferences
        amenities = {
            'homedelivery': preferences.get('homedelivery') == '1',
            'smoking': preferences.get('smoking') == '1',
            'alcohol': preferences.get('alcohol') == '1',
            'wifi': preferences.get('wifi') == '1',
            'valetparking': preferences.get('valetparking') == '1',
            'rooftop': preferences.get('rooftop') == '1'
        }
        
        # Initial filtering
        filtered_df = df.copy()
        logger.info(f"Initial dataset size: {len(filtered_df)}")
        
        # Apply cost range filter
        if cost_range:
            if '-' in cost_range:
                min_cost, max_cost = map(float, cost_range.split('-'))
                filtered_df = filtered_df[filtered_df['cost_value'].between(min_cost, max_cost)]
            else:
                min_cost = float(cost_range.replace('+', ''))
                filtered_df = filtered_df[filtered_df['cost_value'] >= min_cost]
            logger.info(f"After cost range filter: {len(filtered_df)} restaurants")
        
        # Apply cost type filter
        if cost_type:
            filtered_df = filtered_df[filtered_df['Cost_Type'].str.strip() == cost_type]
            logger.info(f"After cost type filter: {len(filtered_df)} restaurants")
        
        # Apply rating filter
        if min_rating > 0:
            filtered_df = filtered_df[filtered_df['rating'] >= min_rating]
            logger.info(f"After rating filter: {len(filtered_df)} restaurants")
        
        # Apply rating type filter
        if rating_type:
            filtered_df = filtered_df[filtered_df['rating_type'].str.strip() == rating_type]
            logger.info(f"After rating type filter: {len(filtered_df)} restaurants")
        
        # Apply amenity filters
        for amenity, value in amenities.items():
            if value:
                filtered_df = filtered_df[filtered_df[amenity].str.strip().str.lower() == 'yes']
                logger.info(f"After {amenity} filter: {len(filtered_df)} restaurants")
        
        # If no restaurants match the criteria, return the top rated restaurants
        if len(filtered_df) == 0:
            logger.warning("No restaurants match all criteria. Returning top rated restaurants.")
            filtered_df = df.nlargest(10, 'rating')
        
        # Calculate personalization score
        filtered_indices = filtered_df.index.tolist()
        avg_similarities = similarity_matrix[:, filtered_indices].mean(axis=1)
        filtered_df['personalization_score'] = avg_similarities[filtered_df.index]
        
        # Sort by combined score (rating + personalization)
        filtered_df['combined_score'] = (
            0.6 * filtered_df['normalized_rating'] +
            0.4 * filtered_df['personalization_score']
        )
        
        result_df = filtered_df.sort_values('combined_score', ascending=False)
        
        # Select and format output columns
        output_columns = [
            'id', 'name', 'latitude', 'longitude', 'address', 'area', 'city',
            'cost', 'Cost_Type', 'rating', 'rating_type'
        ]
        
        recommendations = result_df[output_columns].head(10).to_dict('records')
        logger.info(f"Returning {len(recommendations)} recommendations")
        return recommendations
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """API endpoint for getting restaurant recommendations"""
    try:
        preferences = request.json
        if not preferences:
            return jsonify({
                'success': False,
                'error': 'No preferences provided'
            }), 400
        
        recommendations = get_recommendations(preferences, df, similarity_matrix)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    try:
        # Initialize the model
        df = load_data()
        df, similarity_matrix = preprocess_data(df)
        logger.info("Server initialization complete")
        
        # Run the Flask app
        app.run(debug=True, port=5000)
    except Exception as e:
        logger.error(f"Server initialization failed: {str(e)}")
        raise 