"""
Qwen3-VL Vision Analysis через Ollama
Модель: qwen3-vl:235b-cloud
"""

import asyncio
import httpx
import base64
from typing import Dict, Any, Optional
from pathlib import Path
import json


class QwenVisionOllama:
    """Анализ спутниковых изображений через Qwen3-VL в Ollama"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "qwen3-vl:235b-cloud"
        
    async def check_model_available(self) -> bool:
        """Проверить доступность модели Qwen3-VL"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    return any(m['name'] == self.model_name for m in models)
        except Exception as e:
            print(f"Error checking Qwen3-VL availability: {e}")
        return False
    
    async def fetch_satellite_image(self, bbox: Dict[str, float]) -> Optional[bytes]:
        """
        Получить спутниковый снимок для области
        Использует Esri World Imagery
        """
        # Центр bbox
        lat = (bbox['north'] + bbox['south']) / 2
        lon = (bbox['east'] + bbox['west']) / 2
        zoom = 14  # Можно динамически рассчитать
        
        # Esri ArcGIS API для статических изображений
        url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export"
        params = {
            'bbox': f"{bbox['west']},{bbox['south']},{bbox['east']},{bbox['north']}",
            'size': '1024,1024',
            'format': 'png',
            'f': 'image'
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    return response.content
        except Exception as e:
            print(f"Error fetching satellite image: {e}")
        
        return None
    
    async def analyze_terrain_image(
        self, 
        bbox: Dict[str, float],
        image_bytes: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Анализировать спутниковое изображение через Qwen3-VL
        
        Args:
            bbox: Координаты области
            image_bytes: Байты изображения (если None, загрузит автоматически)
        
        Returns:
            Dict с результатами анализа
        """
        # Загрузить изображение если не передано
        if image_bytes is None:
            image_bytes = await self.fetch_satellite_image(bbox)
            if image_bytes is None:
                return self._fallback_analysis(bbox)
        
        # Конвертировать в base64 для Ollama
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Промпт для анализа
        prompt = """Проанализируй этот спутниковый снимок местности детально.

Определи и опиши:

1. ТИП МЕСТНОСТИ:
   - Горы (высота, крутизна)
   - Равнина (плоская/холмистая)
   - Лес (тип, плотность)
   - Город (плотность застройки)
   - Вода (реки, озера, море)
   - Смешанный тип

2. РАСТИТЕЛЬНОСТЬ:
   - Тип (лес/луга/кустарники/сельхоз)
   - Плотность (0-100%)
   - Распределение (равномерно/кластеры)

3. СТРОЕНИЯ:
   - Наличие зданий (да/нет)
   - Тип (город/деревня/отдельные)
   - Плотность (низкая/средняя/высокая)

4. ИНФРАСТРУКТУРА:
   - Дороги (тип, плотность)
   - Железные дороги
   - Мосты

5. ВОДОЕМЫ:
   - Реки (ширина, извилистость)
   - Озера (размер)
   - Береговая линия

6. РЕЛЬЕФ (по теням и текстуре):
   - Плоский/холмистый/горный
   - Перепад высот (примерно)
   - Наличие склонов/обрывов

7. РЕКОМЕНДАЦИИ ДЛЯ ГЕНЕРАЦИИ:
   - Оптимальное разрешение heightmap (1024/2048/4096/8192)
   - Какие фичи включить (дороги/здания/растительность)
   - Рекомендуемые настройки эрозии
   - Предсказание качества результата (0-100%)

Ответ в формате JSON."""

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "images": [image_base64],
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 2048
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    analysis_text = result.get('response', '')
                    
                    # Парсинг JSON из ответа
                    parsed = self._parse_analysis_response(analysis_text)
                    return {
                        'success': True,
                        'analysis': parsed,
                        'raw_text': analysis_text,
                        'bbox': bbox
                    }
                else:
                    print(f"Ollama API error: {response.status_code}")
                    return self._fallback_analysis(bbox)
                    
        except Exception as e:
            print(f"Error in Qwen3-VL analysis: {e}")
            return self._fallback_analysis(bbox)
    
    def _parse_analysis_response(self, text: str) -> Dict[str, Any]:
        """Парсинг JSON ответа от модели"""
        try:
            # Попытка найти JSON блок
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: простой парсинг текста
        return {
            'terrain_type': self._extract_terrain_type(text),
            'vegetation': {'density': 50, 'type': 'mixed'},
            'buildings': {'present': False},
            'recommended_resolution': 2048,
            'quality_prediction': 75,
            'raw_analysis': text
        }
    
    def _extract_terrain_type(self, text: str) -> str:
        """Извлечь тип местности из текста"""
        text_lower = text.lower()
        if 'гор' in text_lower or 'mountain' in text_lower:
            return 'mountains'
        elif 'лес' in text_lower or 'forest' in text_lower:
            return 'forest'
        elif 'город' in text_lower or 'city' in text_lower:
            return 'urban'
        elif 'вод' in text_lower or 'water' in text_lower:
            return 'water'
        else:
            return 'plains'
    
    def _fallback_analysis(self, bbox: Dict[str, float]) -> Dict[str, Any]:
        """Fallback анализ без Vision модели"""
        area_km2 = abs(bbox['north'] - bbox['south']) * abs(bbox['east'] - bbox['west']) * 111 * 111
        
        return {
            'success': False,
            'fallback': True,
            'analysis': {
                'terrain_type': 'unknown',
                'vegetation': {'density': 50, 'type': 'mixed'},
                'buildings': {'present': False},
                'recommended_resolution': 2048 if area_km2 < 100 else 4096,
                'quality_prediction': 60,
                'message': 'Qwen3-VL недоступен, использованы базовые параметры'
            },
            'bbox': bbox
        }


# Пример использования
async def test_qwen_vision():
    vision = QwenVisionOllama()
    
    # Проверка доступности
    available = await vision.check_model_available()
    print(f"Qwen3-VL доступен: {available}")
    
    if available:
        # Тестовая область (Москва)
        bbox = {
            'north': 55.8,
            'south': 55.7,
            'east': 37.7,
            'west': 37.5
        }
        
        result = await vision.analyze_terrain_image(bbox)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(test_qwen_vision())
