"""
Traffic route generation and optimization
"""

from .traffic_generator import TrafficGenerator
from .beamng_traffic import BeamNGTrafficIntegrator

__all__ = ['TrafficGenerator', 'BeamNGTrafficIntegrator']
