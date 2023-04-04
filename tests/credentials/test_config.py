import logging
from odin.credentials.config import BackboneProperties
logger = logging.getLogger(__name__)


def test_backbone_props():
    bp = BackboneProperties()
    assert "DEV_POSTGRES_HOST" in bp.keys()
    assert "DEV_POSTGRES_PORT" in bp.keys()
