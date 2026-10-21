import logging
from typing import List, Optional
from courses.ingestion.base import BaseCourseConnector, RawCourse

logger = logging.getLogger(__name__)

class KaggleLearnConnector(BaseCourseConnector):
    """
    Conector para Kaggle Learn (Microcursos oficiales).
    Cursos prácticos con notebooks ejecutables gratuitos y certificados de finalización.
    Especialmente enfocado en Inteligencia Artificial, Ciencia de Datos y Python.
    """
    platform_id = "kaggle"
    platform_name = "Kaggle Learn"
    tier = 1
    group = "ai"

    # Catálogo canónico de cursos oficiales de Kaggle Learn
    COURSES_CATALOG = [
        {
            "id": "intro-to-programming",
            "title": "Intro to Programming",
            "url": "https://www.kaggle.com/learn/intro-to-programming",
            "description": "Aprende los conceptos fundamentales de la programación con Python, variables, funciones y lógica booleana mediante ejercicios prácticos.",
            "level": "beginner",
            "duration_hours": 5.0,
            "tags": ["Python", "Programación", "Fundamentos", "Lógica"],
            "career_hints": ["software", "ia", "sistemas"],
        },
        {
            "id": "python",
            "title": "Python for Data Science",
            "url": "https://www.kaggle.com/learn/python",
            "description": "Domina el lenguaje Python para la manipulación de datos, listas, bucles, diccionarios y bibliotecas esenciales de ciencia de datos.",
            "level": "beginner",
            "duration_hours": 5.0,
            "tags": ["Python", "Data Science", "Estructuras de Datos"],
            "career_hints": ["ia", "software", "sistemas"],
        },
        {
            "id": "intro-to-machine-learning",
            "title": "Intro to Machine Learning",
            "url": "https://www.kaggle.com/learn/intro-to-machine-learning",
            "description": "Construye tus primeros modelos de aprendizaje automático con scikit-learn, validación cruzada y árboles de decisión.",
            "level": "beginner",
            "duration_hours": 3.0,
            "tags": ["Machine Learning", "Scikit-Learn", "Modelos Predictivos", "Python"],
            "career_hints": ["ia", "software"],
        },
        {
            "id": "intermediate-machine-learning",
            "title": "Intermediate Machine Learning",
            "url": "https://www.kaggle.com/learn/intermediate-machine-learning",
            "description": "Manejo de valores nulos, variables categóricas, pipelines de preprocesamiento, XGBoost y prevención de fugas de datos.",
            "level": "intermediate",
            "duration_hours": 4.0,
            "tags": ["Machine Learning", "XGBoost", "Pipelines", "Feature Engineering"],
            "career_hints": ["ia"],
        },
        {
            "id": "pandas",
            "title": "Pandas Data Analysis",
            "url": "https://www.kaggle.com/learn/pandas",
            "description": "Manipula y limpia grandes volúmenes de datos con la biblioteca Pandas: indexación, agrupaciones, tipos de datos y transformaciones.",
            "level": "beginner",
            "duration_hours": 4.0,
            "tags": ["Pandas", "Data Analysis", "Python", "ETL"],
            "career_hints": ["ia", "industrial", "sistemas"],
        },
        {
            "id": "data-visualization",
            "title": "Data Visualization",
            "url": "https://www.kaggle.com/learn/data-visualization",
            "description": "Crea gráficos profesionales interactivos con Seaborn y Matplotlib: gráficos de dispersión, mapas de calor, histogramas y distribución.",
            "level": "beginner",
            "duration_hours": 4.0,
            "tags": ["Data Visualization", "Seaborn", "Matplotlib", "Dashboards"],
            "career_hints": ["ia", "industrial"],
        },
        {
            "id": "feature-engineering",
            "title": "Feature Engineering",
            "url": "https://www.kaggle.com/learn/feature-engineering",
            "description": "Mejora el rendimiento de tus modelos de IA creando características informativas mediante análisis de componentes principales y clustering.",
            "level": "intermediate",
            "duration_hours": 5.0,
            "tags": ["Feature Engineering", "PCA", "K-Means", "Machine Learning"],
            "career_hints": ["ia"],
        },
        {
            "id": "intro-to-deep-learning",
            "title": "Intro to Deep Learning",
            "url": "https://www.kaggle.com/learn/intro-to-deep-learning",
            "description": "Diseña y entrena redes neuronales artificiales profundas con TensorFlow y Keras. Técnicas de regularización, dropout y optimización estocástica.",
            "level": "intermediate",
            "duration_hours": 4.0,
            "tags": ["Deep Learning", "TensorFlow", "Keras", "Redes Neuronales"],
            "career_hints": ["ia"],
        },
        {
            "id": "computer-vision",
            "title": "Computer Vision with Deep Learning",
            "url": "https://www.kaggle.com/learn/computer-vision",
            "description": "Construye redes neuronales convolucionales (CNNs) para clasificación y detección de imágenes, usando transfer learning.",
            "level": "intermediate",
            "duration_hours": 4.0,
            "tags": ["Computer Vision", "CNN", "Deep Learning", "Keras"],
            "career_hints": ["ia"],
        },
        {
            "id": "time-series",
            "title": "Time Series Forecasting",
            "url": "https://www.kaggle.com/learn/time-series",
            "description": "Aplica modelos de aprendizaje automático y econometría para pronóstico de series temporales, estacionalidad, tendencias e inventarios.",
            "level": "intermediate",
            "duration_hours": 5.0,
            "tags": ["Time Series", "Forecasting", "Series Temporales", "Pronósticos"],
            "career_hints": ["ia", "industrial"],
        },
        {
            "id": "intro-to-sql",
            "title": "Intro to SQL",
            "url": "https://www.kaggle.com/learn/intro-to-sql",
            "description": "Aprende a consultar bases de datos relacionales en la nube usando SQL y Google BigQuery con conjuntos de datos masivos reales.",
            "level": "beginner",
            "duration_hours": 3.0,
            "tags": ["SQL", "Bases de Datos", "BigQuery", "Consultas"],
            "career_hints": ["sistemas", "software", "industrial", "ia"],
        },
        {
            "id": "advanced-sql",
            "title": "Advanced SQL",
            "url": "https://www.kaggle.com/learn/advanced-sql",
            "description": "Consultas analíticas avanzadas: funciones de ventana (Window Functions), JOINs complejos, particionado y optimización de rendimiento.",
            "level": "advanced",
            "duration_hours": 4.0,
            "tags": ["SQL", "Advanced SQL", "Window Functions", "Optimización"],
            "career_hints": ["sistemas", "software", "ia"],
        },
        {
            "id": "data-cleaning",
            "title": "Data Cleaning",
            "url": "https://www.kaggle.com/learn/data-cleaning",
            "description": "Estrategias para lidiar con datos faltantes, escalado y normalización, análisis sintáctico de fechas y encoding de caracteres.",
            "level": "beginner",
            "duration_hours": 4.0,
            "tags": ["Data Cleaning", "Preprocesamiento", "Calidad de Datos"],
            "career_hints": ["ia", "sistemas", "industrial"],
        },
        {
            "id": "geospatial-analysis",
            "title": "Geospatial Analysis",
            "url": "https://www.kaggle.com/learn/geospatial-analysis",
            "description": "Análisis de datos geográficos y cartográficos interactivos usando GeoPandas y Folium para ruteo y logística.",
            "level": "intermediate",
            "duration_hours": 4.0,
            "tags": ["Geospatial", "GeoPandas", "Logística", "Mapas"],
            "career_hints": ["industrial", "ia", "sistemas"],
        },
        {
            "id": "machine-learning-explainability",
            "title": "Machine Learning Explainability",
            "url": "https://www.kaggle.com/learn/machine-learning-explainability",
            "description": "Comprende y explica las decisiones de tus modelos de IA mediante SHAP values, Permutation Importance y Partial Dependence Plots.",
            "level": "intermediate",
            "duration_hours": 4.0,
            "tags": ["Explainable AI", "SHAP", "Transparencia IA", "Machine Learning"],
            "career_hints": ["ia"],
        },
        {
            "id": "intro-to-ai-ethics",
            "title": "Intro to AI Ethics",
            "url": "https://www.kaggle.com/learn/intro-to-ai-ethics",
            "description": "Descubre cómo mitigar sesgos algorítmicos, garantizar justicia y privacidad en el despliegue de sistemas de inteligencia artificial.",
            "level": "beginner",
            "duration_hours": 3.0,
            "tags": ["AI Ethics", "Ética en IA", "Gobernanza", "Responsabilidad"],
            "career_hints": ["ia", "sistemas"],
        }
    ]

    def fetch_courses(self, limit: Optional[int] = None) -> List[RawCourse]:
        courses: List[RawCourse] = []
        logger.info("Cargando microcursos oficiales de Kaggle Learn...")

        items = self.COURSES_CATALOG
        if limit:
            items = items[:limit]

        for item in items:
            courses.append(
                RawCourse(
                    platform=self.platform_id,
                    external_id=f"kaggle-{item['id']}",
                    title=item["title"],
                    description=item["description"],
                    short_description=item["description"][:250],
                    url=item["url"],
                    image_url="https://www.kaggle.com/static/images/site-logo.svg",
                    language="en",
                    level=item["level"],
                    resource_type="interactive",
                    has_certification=True,
                    duration_hours=item["duration_hours"],
                    instructor_name="Kaggle / Google",
                    category_hint="Inteligencia Artificial & Ciencia de Datos",
                    tags=item["tags"],
                    provider_name="Kaggle",
                    credential_type="completion",
                    is_free_credential=True,
                    has_practical_labs=True,
                    career_hints=item.get("career_hints", ["ia"])
                )
            )

        logger.info("Kaggle Learn: %d cursos procesados con éxito", len(courses))
        return courses
