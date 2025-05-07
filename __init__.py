import logging
import os

logger = logging.getLogger(__name__)

try:
    from .nodes import NODE_CLASS_MAPPINGS
    __all__ = ['NODE_CLASS_MAPPINGS']

except ImportError as e:
    # Tangkap nama modul yang hilang
    msg = str(e)
    if 'No module named' in msg:
        missing = msg.split('No module named')[-1].strip().strip("'")
    else:
        missing = msg.split()[-1].strip("'")
    requirements_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'requirements.txt'
    )
    logger.error(
        f"ERROR: Could not import required library '{missing}'. "
        f"Please install dependencies with:\n"
        f"    pip install -r {requirements_path}"
    )
    NODE_CLASS_MAPPINGS = {}
    __all__ = ['NODE_CLASS_MAPPINGS']
