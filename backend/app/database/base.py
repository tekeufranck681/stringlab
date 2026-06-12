from app.database.connection import Base

# Import every model module so its tables register on Base.metadata. Alembic's
# autogenerate compares this metadata against the live database, so any model
# not imported here is invisible to migrations.
from app.modules.catalogue import models as catalogue_models  # noqa: F401
from app.modules.examples import models as examples_models  # noqa: F401
from app.modules.runs import models as runs_models  # noqa: F401

# Expose a single metadata object for Alembic (see alembic/env.py).
target_metadata = Base.metadata
