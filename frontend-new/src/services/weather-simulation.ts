/**
 * Weather Simulation System
 * Dynamic weather with climate modeling
 */

export type WeatherType = 'clear' | 'cloudy' | 'rain' | 'snow' | 'fog' | 'storm';
export type Season = 'spring' | 'summer' | 'autumn' | 'winter';

export interface WeatherState {
  type: WeatherType;
  temperature: number; // Celsius
  humidity: number; // 0-100%
  windSpeed: number; // km/h
  windDirection: number; // 0-360 degrees
  precipitation: number; // mm/h
  visibility: number; // km
  cloudCover: number; // 0-100%
}

export interface ClimateZone {
  name: string;
  avgTemperature: number;
  tempRange: number;
  avgHumidity: number;
  avgRainfall: number;
}

export class WeatherSimulation {
  private currentWeather: WeatherState;
  private season: Season;
  private time: number = 0; // seconds since start

  constructor(season: Season = 'summer', initialWeather?: Partial<WeatherState>) {
    this.season = season;
    this.currentWeather = {
      type: 'clear',
      temperature: 20,
      humidity: 50,
      windSpeed: 10,
      windDirection: 180,
      precipitation: 0,
      visibility: 10,
      cloudCover: 20,
      ...initialWeather,
    };
  }

  update(deltaTime: number): WeatherState {
    this.time += deltaTime;

    // Natural weather transitions
    this.updateTemperature(deltaTime);
    this.updateWind(deltaTime);
    this.updateClouds(deltaTime);
    this.updatePrecipitation(deltaTime);
    this.determineWeatherType();

    return this.getState();
  }

  private updateTemperature(deltaTime: number): void {
    const seasonTemp = this.getSeasonalTemperature();
    const timeOfDay = (this.time % 86400) / 86400; // 0-1
    const dailyCycle = Math.sin(timeOfDay * Math.PI * 2 - Math.PI / 2) * 8;
    
    const targetTemp = seasonTemp + dailyCycle;
    this.currentWeather.temperature += (targetTemp - this.currentWeather.temperature) * deltaTime * 0.01;
  }

  private updateWind(deltaTime: number): void {
    // Random wind fluctuations
    const windNoise = (Math.random() - 0.5) * 2;
    this.currentWeather.windSpeed += windNoise * deltaTime;
    this.currentWeather.windSpeed = Math.max(0, Math.min(100, this.currentWeather.windSpeed));
    
    this.currentWeather.windDirection += (Math.random() - 0.5) * 10 * deltaTime;
    this.currentWeather.windDirection = (this.currentWeather.windDirection + 360) % 360;
  }

  private updateClouds(deltaTime: number): void {
    const cloudChange = (Math.random() - 0.5) * 5 * deltaTime;
    this.currentWeather.cloudCover += cloudChange;
    this.currentWeather.cloudCover = Math.max(0, Math.min(100, this.currentWeather.cloudCover));
  }

  private updatePrecipitation(deltaTime: number): void {
    if (this.currentWeather.cloudCover > 70) {
      const rainChance = (this.currentWeather.cloudCover - 70) / 30;
      if (Math.random() < rainChance * deltaTime * 0.1) {
        this.currentWeather.precipitation = Math.random() * 10;
      }
    } else {
      this.currentWeather.precipitation *= 0.95; // Gradually stop
    }

    // Snow vs rain based on temperature
    if (this.currentWeather.temperature < 2 && this.currentWeather.precipitation > 0) {
      // It's snowing
    }

    this.currentWeather.visibility = 10 - (this.currentWeather.precipitation * 0.5);
    this.currentWeather.visibility = Math.max(0.5, this.currentWeather.visibility);
  }

  private determineWeatherType(): void {
    if (this.currentWeather.precipitation > 5) {
      if (this.currentWeather.windSpeed > 50) {
        this.currentWeather.type = 'storm';
      } else if (this.currentWeather.temperature < 2) {
        this.currentWeather.type = 'snow';
      } else {
        this.currentWeather.type = 'rain';
      }
    } else if (this.currentWeather.cloudCover > 80) {
      this.currentWeather.type = 'cloudy';
    } else if (this.currentWeather.visibility < 1) {
      this.currentWeather.type = 'fog';
    } else {
      this.currentWeather.type = 'clear';
    }
  }

  private getSeasonalTemperature(): number {
    switch (this.season) {
      case 'winter': return 0;
      case 'spring': return 15;
      case 'summer': return 25;
      case 'autumn': return 10;
    }
  }

  setSeason(season: Season): void {
    this.season = season;
  }

  setWeather(weather: Partial<WeatherState>): void {
    this.currentWeather = { ...this.currentWeather, ...weather };
  }

  getState(): WeatherState {
    return { ...this.currentWeather };
  }
}

export const climateZones: Record<string, ClimateZone> = {
  tropical: {
    name: 'Tropical',
    avgTemperature: 27,
    tempRange: 5,
    avgHumidity: 80,
    avgRainfall: 200,
  },
  desert: {
    name: 'Desert',
    avgTemperature: 30,
    tempRange: 20,
    avgHumidity: 20,
    avgRainfall: 10,
  },
  temperate: {
    name: 'Temperate',
    avgTemperature: 15,
    tempRange: 15,
    avgHumidity: 60,
    avgRainfall: 80,
  },
  arctic: {
    name: 'Arctic',
    avgTemperature: -10,
    tempRange: 20,
    avgHumidity: 70,
    avgRainfall: 30,
  },
};

export const weatherSimulation = new WeatherSimulation();
