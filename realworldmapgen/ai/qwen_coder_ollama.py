"""
Qwen3-Coder Code Generation через Ollama
Модель: qwen3-coder:480b-cloud
"""

import asyncio
import httpx
import json
from typing import Dict, Any, Optional, List
import ast


class QwenCoderOllama:
    """Генерация кода конфигурации через Qwen3-Coder в Ollama"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "qwen3-coder:480b-cloud"
        
    async def check_model_available(self) -> bool:
        """Проверить доступность модели Qwen3-Coder"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    return any(m['name'] == self.model_name for m in models)
        except Exception as e:
            print(f"Error checking Qwen3-Coder availability: {e}")
        return False
    
    async def generate_terrain_config(
        self,
        vision_analysis: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Генерировать оптимальную конфигурацию генерации на основе Vision анализа
        
        Args:
            vision_analysis: Результат анализа от Qwen3-VL
            user_preferences: Пользовательские предпочтения
        
        Returns:
            Dict с оптимальной конфигурацией
        """
        prompt = f"""Ты - эксперт по процедурной генерации 3D местности.

На основе анализа спутникового снимка создай оптимальную конфигурацию для генерации terrain.

АНАЛИЗ МЕСТНОСТИ:
{json.dumps(vision_analysis.get('analysis', {}), indent=2, ensure_ascii=False)}

СОЗДАЙ PYTHON DICT со следующими параметрами:

```python
config = {{
    # Основные параметры
    "resolution": 2048,  # heightmap разрешение (1024/2048/4096/8192)
    "max_area_km2": 100,
    
    # Высоты и эрозия
    "elevation": {{
        "source_priority": ["srtm", "aster"],  # приоритет источников
        "smoothing": 0.5,  # сглаживание (0-1)
        "erosion_iterations": 3,  # итерации эрозии
        "erosion_strength": 0.7,  # сила эрозии (0-1)
    }},
    
    # Растительность
    "vegetation": {{
        "enabled": True,
        "density": 0.7,  # плотность (0-1)
        "types": ["forest", "grass"],  # типы
        "distribution": "clustered",  # uniform/clustered/noise
        "min_height": 0,  # минимальная высота для spawna
        "max_height": 2000,
        "slope_limit": 45,  # макс угол склона
    }},
    
    # Дороги
    "roads": {{
        "enabled": True,
        "width_meters": 6,
        "curviness": 0.5,  # извилистость (0-1)
        "follow_terrain": True,
    }},
    
    # Здания
    "buildings": {{
        "enabled": False,
        "style": "modern",  # modern/traditional/industrial
        "density": 0.3,
        "max_floors": 5,
    }},
    
    # Водоемы
    "water": {{
        "enabled": True,
        "lake_threshold": 0.2,  # порог для создания озер
        "river_width": 10,
    }},
    
    # Weightmaps для текстур
    "weightmaps": {{
        "enabled": True,
        "layers": [
            {{"name": "rock", "altitude_min": 1500, "slope_min": 45}},
            {{"name": "grass", "altitude_min": 0, "altitude_max": 1500}},
            {{"name": "sand", "near_water": True}},
        ]
    }},
    
    # Экспорт
    "export": {{
        "formats": ["gltf", "png16"],
        "include_normals": True,
        "include_tangents": True,
    }}
}}
```

ВАЖНО:
1. Подбери параметры на основе типа местности из анализа
2. Для гор: больше эрозии, rock weightmaps, меньше зданий
3. Для городов: больше зданий, дорог, меньше растительности
4. Для лесов: высокая плотность vegetation, больше деревьев
5. Для равнин: умеренные параметры, больше травы

Выведи ТОЛЬКО Python код с dict, без объяснений."""

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.2,
                            "num_predict": 2048
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    code = result.get('response', '')
                    
                    # Парсинг Python кода
                    config = self._parse_python_config(code)
                    
                    # Объединить с пользовательскими настройками
                    if user_preferences:
                        config = self._merge_configs(config, user_preferences)
                    
                    return {
                        'success': True,
                        'config': config,
                        'generated_code': code
                    }
                else:
                    return self._fallback_config(vision_analysis, user_preferences)
                    
        except Exception as e:
            print(f"Error in Qwen3-Coder generation: {e}")
            return self._fallback_config(vision_analysis, user_preferences)
    
    async def generate_unreal_blueprint(
        self,
        terrain_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> str:
        """
        Генерировать Blueprint Python скрипт для Unreal Engine 5
        """
        prompt = f"""Создай Python скрипт для Unreal Engine 5 Editor Utility Widget, который импортирует terrain.

ДАННЫЕ МЕСТНОСТИ:
- Heightmap: {terrain_data.get('heightmap_path', 'heightmap.png')}
- Разрешение: {config.get('resolution', 2048)}
- Weightmaps: {config.get('weightmaps', {}).get('enabled', False)}

СКРИПТ ДОЛЖЕН:
1. Импортировать heightmap как Landscape
2. Настроить размер landscape
3. Создать материал с weightmaps (если enabled)
4. Расставить foliage (деревья, траву)
5. Создать splines для дорог
6. Настроить lighting

Выведи чистый Python код для unreal.py без markdown блоков."""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.1}
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get('response', '# Script generation failed')
                    
        except Exception as e:
            print(f"Error generating Unreal script: {e}")
        
        return "# Script generation failed"
    
    def _parse_python_config(self, code: str) -> Dict[str, Any]:
        """Безопасный парсинг Python кода конфигурации"""
        try:
            # Извлечь dict из кода
            start = code.find('{')
            end = code.rfind('}') + 1
            
            if start != -1 and end > start:
                dict_str = code[start:end]
                # Безопасное выполнение через ast.literal_eval
                config = ast.literal_eval(dict_str)
                return config
        except Exception as e:
            print(f"Error parsing config: {e}")
        
        return self._default_config()
    
    def _merge_configs(
        self,
        ai_config: Dict[str, Any],
        user_prefs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Объединить AI конфиг с пользовательскими настройками"""
        merged = ai_config.copy()
        
        # Пользовательские настройки имеют приоритет
        if 'resolution' in user_prefs:
            merged['resolution'] = user_prefs['resolution']
        
        if 'roads' in user_prefs:
            merged['roads']['enabled'] = user_prefs['roads'].get('enabled', True)
        
        if 'buildings' in user_prefs:
            merged['buildings']['enabled'] = user_prefs['buildings'].get('enabled', False)
        
        return merged
    
    def _default_config(self) -> Dict[str, Any]:
        """Дефолтная конфигурация"""
        return {
            "resolution": 2048,
            "elevation": {"smoothing": 0.5, "erosion_iterations": 3},
            "vegetation": {"enabled": True, "density": 0.5},
            "roads": {"enabled": True},
            "buildings": {"enabled": False},
            "water": {"enabled": True},
            "weightmaps": {"enabled": True}
        }
    
    def _fallback_config(
        self,
        vision_analysis: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback конфигурация без Coder модели"""
        config = self._default_config()
        
        # Применить рекомендации из vision анализа
        analysis = vision_analysis.get('analysis', {})
        if 'recommended_resolution' in analysis:
            config['resolution'] = analysis['recommended_resolution']
        
        # Применить user preferences
        if user_preferences:
            config = self._merge_configs(config, user_preferences)
        
        return {
            'success': False,
            'fallback': True,
            'config': config,
            'message': 'Qwen3-Coder недоступен, использована дефолтная конфигурация'
        }


# Пример использования
async def test_qwen_coder():
    coder = QwenCoderOllama()
    
    available = await coder.check_model_available()
    print(f"Qwen3-Coder доступен: {available}")
    
    if available:
        # Тестовый анализ
        vision_analysis = {
            'analysis': {
                'terrain_type': 'mountains',
                'vegetation': {'density': 70, 'type': 'forest'},
                'buildings': {'present': False},
                'recommended_resolution': 4096
            }
        }
        
        result = await coder.generate_terrain_config(vision_analysis)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(test_qwen_coder())
