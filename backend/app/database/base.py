from app.database.connection import Base
# register models here to ensure they are included in the metadata for db migrations


# Expose a single metadata object
target_metadata = Base.metadata