"""
ML-based Terrain Classification
Classify terrain types using machine learning
"""

import numpy as np
from typing import Dict, List, Tuple
from enum import Enum


class TerrainClass(str, Enum):
    MOUNTAIN = "mountain"
    VALLEY = "valley"
    PLATEAU = "plateau"
    PLAIN = "plain"
    HILL = "hill"
    CANYON = "canyon"
    RIDGE = "ridge"
    DEPRESSION = "depression"


class TerrainFeatures:
    """Extract features from terrain heightmap"""
    
    @staticmethod
    def calculate_features(
        heightmap: np.ndarray,
        window_size: int = 10
    ) -> Dict[str, float]:
        """Calculate terrain features for classification"""
        
        features = {}
        
        # Elevation statistics
        features['mean_elevation'] = float(np.mean(heightmap))
        features['std_elevation'] = float(np.std(heightmap))
        features['min_elevation'] = float(np.min(heightmap))
        features['max_elevation'] = float(np.max(heightmap))
        features['elevation_range'] = features['max_elevation'] - features['min_elevation']
        
        # Slope analysis
        dy, dx = np.gradient(heightmap)
        slope = np.sqrt(dx**2 + dy**2)
        features['mean_slope'] = float(np.mean(slope))
        features['max_slope'] = float(np.max(slope))
        features['slope_variance'] = float(np.var(slope))
        
        # Roughness (local variation)
        roughness = np.zeros_like(heightmap)
        h, w = heightmap.shape
        for i in range(window_size, h - window_size):
            for j in range(window_size, w - window_size):
                window = heightmap[
                    i - window_size:i + window_size,
                    j - window_size:j + window_size
                ]
                roughness[i, j] = np.std(window)
        
        features['mean_roughness'] = float(np.mean(roughness))
        features['max_roughness'] = float(np.max(roughness))
        
        # Curvature (second derivative)
        ddy, ddx = np.gradient(dy), np.gradient(dx)
        curvature = np.sqrt(ddx**2 + ddy**2)
        features['mean_curvature'] = float(np.mean(curvature))
        features['max_curvature'] = float(np.max(curvature))
        
        # Aspect (direction of slope)
        aspect = np.arctan2(dy, dx)
        features['aspect_diversity'] = float(np.std(aspect))
        
        # Relief ratio
        if features['elevation_range'] > 0:
            features['relief_ratio'] = features['mean_elevation'] / features['elevation_range']
        else:
            features['relief_ratio'] = 0.0
        
        return features


class SimpleTerrainClassifier:
    """Rule-based terrain classifier"""
    
    def classify(self, features: Dict[str, float]) -> TerrainClass:
        """Classify terrain based on features"""
        
        elevation_range = features['elevation_range']
        mean_slope = features['mean_slope']
        roughness = features['mean_roughness']
        relief_ratio = features['relief_ratio']
        
        # Mountain: high elevation range, steep slopes
        if elevation_range > 500 and mean_slope > 15:
            return TerrainClass.MOUNTAIN
        
        # Canyon: high elevation range, very high curvature
        if elevation_range > 300 and features['max_curvature'] > 0.5:
            return TerrainClass.CANYON
        
        # Plateau: high elevation, low slope variance
        if features['mean_elevation'] > 500 and features['slope_variance'] < 5:
            return TerrainClass.PLATEAU
        
        # Ridge: moderate elevation, high aspect diversity
        if elevation_range > 200 and features['aspect_diversity'] > 1.5:
            return TerrainClass.RIDGE
        
        # Valley: low relief ratio, moderate roughness
        if relief_ratio < 0.3 and roughness > 10:
            return TerrainClass.VALLEY
        
        # Hill: moderate everything
        if elevation_range > 100 and mean_slope > 5:
            return TerrainClass.HILL
        
        # Depression: negative relief features
        if features['mean_elevation'] < features['min_elevation'] + elevation_range * 0.2:
            return TerrainClass.DEPRESSION
        
        # Default: plain
        return TerrainClass.PLAIN
    
    def classify_regions(
        self,
        heightmap: np.ndarray,
        region_size: int = 50
    ) -> List[Tuple[int, int, TerrainClass]]:
        """Classify terrain in regions"""
        
        h, w = heightmap.shape
        results = []
        
        for i in range(0, h, region_size):
            for j in range(0, w, region_size):
                # Extract region
                region = heightmap[
                    i:min(i + region_size, h),
                    j:min(j + region_size, w)
                ]
                
                if region.size == 0:
                    continue
                
                # Calculate features
                features = TerrainFeatures.calculate_features(region)
                
                # Classify
                terrain_class = self.classify(features)
                
                results.append((i, j, terrain_class))
        
        return results
    
    def get_classification_map(
        self,
        heightmap: np.ndarray,
        region_size: int = 50
    ) -> np.ndarray:
        """Generate classification map"""
        
        h, w = heightmap.shape
        classification_map = np.zeros((h, w), dtype=int)
        
        regions = self.classify_regions(heightmap, region_size)
        
        terrain_to_int = {
            TerrainClass.MOUNTAIN: 1,
            TerrainClass.VALLEY: 2,
            TerrainClass.PLATEAU: 3,
            TerrainClass.PLAIN: 4,
            TerrainClass.HILL: 5,
            TerrainClass.CANYON: 6,
            TerrainClass.RIDGE: 7,
            TerrainClass.DEPRESSION: 8,
        }
        
        for i, j, terrain_class in regions:
            classification_map[
                i:min(i + region_size, h),
                j:min(j + region_size, w)
            ] = terrain_to_int[terrain_class]
        
        return classification_map


# Global classifier instance
terrain_classifier = SimpleTerrainClassifier()


def classify_terrain(heightmap: np.ndarray) -> Dict[str, any]:
    """
    Classify terrain and return results
    
    Args:
        heightmap: 2D array of elevation values
    
    Returns:
        Dictionary with classification results
    """
    # Calculate overall features
    features = TerrainFeatures.calculate_features(heightmap)
    
    # Classify overall terrain
    overall_class = terrain_classifier.classify(features)
    
    # Classify regions
    regions = terrain_classifier.classify_regions(heightmap)
    
    # Count terrain types
    terrain_counts = {}
    for _, _, terrain_class in regions:
        terrain_counts[terrain_class] = terrain_counts.get(terrain_class, 0) + 1
    
    return {
        'overall_classification': overall_class,
        'features': features,
        'regions': regions,
        'terrain_distribution': terrain_counts,
        'classification_map': terrain_classifier.get_classification_map(heightmap)
    }
