import logging
import urllib.request
import re
from typing import List, Optional
from courses.ingestion.base import BaseCourseConnector, RawCourse

logger = logging.getLogger(__name__)

class HuggingFaceLearnConnector(BaseCourseConnector):
    """
    Conector para Hugging Face Learn (https://huggingface.co/learn).
    Cursos oficiales de frontera en Inteligencia Artificial, LLMs, Modelos de Difusión,
    Agentes Autónomos y Aprendizaje por Refuerzo Profundo con laboratorios y certificación.
    """
    platform_id = "huggingface"
    platform_name = "Hugging Face Learn"
    tier = 1
    group = "ai"

    CATALOG = [
        {
            "id": "deep-rl-course",
            "title": "Deep Reinforcement Learning Course",
            "url": "https://huggingface.co/learn/deep-rl-course/unit0/introduction",
            "description": "Domina el aprendizaje por refuerzo profundo: Q-Learning, Deep Q-Networks (DQN), Policy Gradients, Actor-Critic y agentes jugando en entornos Unity y Gymnasium.",
            "level": "intermediate",
            "duration_hours": 30.0,
            "tags": ["Reinforcement Learning", "PyTorch", "Gymnasium", "Robotics", "IA"],
            "career_hints": ["ia", "software"],
        },
        {
            "id": "agents-course",
            "title": "AI Agents Course",
            "url": "https://huggingface.co/learn/agents-course/unit0/introduction",
            "description": "Aprende a diseñar y desplegar agentes autónomos basados en LLMs: planificación, llamadas a herramientas (Tool Calling), memoria y frameworks modernos como smolagents y LangChain.",
            "level": "intermediate",
            "duration_hours": 20.0,
            "tags": ["AI Agents", "LLMs", "smolagents", "Tool Calling", "Python"],
            "career_hints": ["ia", "software", "sistemas"],
        },
        {
            "id": "computer-vision-course",
            "title": "Computer Vision Course",
            "url": "https://huggingface.co/learn/computer-vision-course/unit0/introduction",
            "description": "Visión por computadora con Hugging Face Transformers: clasificación de imágenes, segmentación semántica, detección de objetos y Vision Transformers (ViT).",
            "level": "intermediate",
            "duration_hours": 25.0,
            "tags": ["Computer Vision", "Transformers", "ViT", "PyTorch", "Deep Learning"],
            "career_hints": ["ia"],
        },
        {
            "id": "audio-course",
            "title": "Audio & Speech Transformers Course",
            "url": "https://huggingface.co/learn/audio-course/chapter0/introduction",
            "description": "Procesamiento de audio y voz con redes neuronales: reconocimiento automático de voz (Whisper/ASR), síntesis de voz (TTS) y clasificación de audio.",
            "level": "intermediate",
            "duration_hours": 20.0,
            "tags": ["Audio Processing", "Whisper", "Speech-to-Text", "PyTorch"],
            "career_hints": ["ia"],
        },
        {
            "id": "diffusion-course",
            "title": "Diffusion Models Course",
            "url": "https://huggingface.co/learn/diffusion-course/unit0/introduction",
            "description": "Entrenamiento e inferencia de modelos generativos de difusión para síntesis de imágenes fotorrealistas con la biblioteca Diffusers.",
            "level": "advanced",
            "duration_hours": 25.0,
            "tags": ["Diffusion Models", "Diffusers", "Generative AI", "PyTorch"],
            "career_hints": ["ia"],
        },
        {
            "id": "robotics-course",
            "title": "LeRobot: Open Source Robotics Course",
            "url": "https://huggingface.co/learn/robotics-course/unit0/introduction",
            "description": "Inteligencia artificial aplicada a la robótica: imitación de comportamiento, control cinemático e integración con brazos robóticos físicos y simuladores.",
            "level": "advanced",
            "duration_hours": 30.0,
            "tags": ["Robotics", "LeRobot", "Hardware", "Embodied AI", "Control"],
            "career_hints": ["ia", "industrial", "sistemas"],
        },
        {
            "id": "llm-course",
            "title": "Open-Source LLMs & NLP Course",
            "url": "https://huggingface.co/learn/llm-course/unit0/introduction",
            "description": "Fundamentos y ajuste fino (Fine-Tuning con LoRA/QLoRA) de Modelos de Lenguaje Masivos de código abierto como LLaMA, Mistral y Gemma.",
            "level": "intermediate",
            "duration_hours": 35.0,
            "tags": ["LLMs", "Fine-Tuning", "LoRA", "Transformers", "NLP"],
            "career_hints": ["ia", "software"],
        }
    ]

    def fetch_courses(self, limit: Optional[int] = None) -> List[RawCourse]:
        courses: List[RawCourse] = []
        logger.info("Cargando cursos oficiales de Hugging Face Learn...")

        items = self.CATALOG
        if limit:
            items = items[:limit]

        for item in items:
            courses.append(
                RawCourse(
                    platform=self.platform_id,
                    external_id=f"hf-{item['id']}",
                    title=item["title"],
                    description=item["description"],
                    short_description=item["description"][:250],
                    url=item["url"],
                    image_url="https://huggingface.co/front/assets/huggingface_logo-noborder.svg",
                    language="en",
                    level=item["level"],
                    resource_type="interactive",
                    has_certification=True,
                    duration_hours=item["duration_hours"],
                    instructor_name="Hugging Face Community & Staff",
                    category_hint="Inteligencia Artificial & Machine Learning",
                    tags=item["tags"],
                    provider_name="Hugging Face",
                    credential_type="completion",
                    is_free_credential=True,
                    has_practical_labs=True,
                    career_hints=item.get("career_hints", ["ia"])
                )
            )

        logger.info("Hugging Face Learn: %d cursos procesados con éxito", len(courses))
        return courses
