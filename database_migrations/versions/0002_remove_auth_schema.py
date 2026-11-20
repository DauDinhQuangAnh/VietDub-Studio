import sqlalchemy as sa
from alembic import op

revision = "0002_remove_auth"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "users" in inspector.get_table_names():
        op.drop_table("users")

    jobs_columns = {column["name"] for column in inspector.get_columns("jobs")}
    if "user_id" in jobs_columns:
        with op.batch_alter_table("jobs") as batch_op:
            batch_op.drop_column("user_id")

    voices_columns = {column["name"] for column in inspector.get_columns("custom_voices")}
    if "user_id" in voices_columns:
        with op.batch_alter_table("custom_voices") as batch_op:
            batch_op.drop_column("user_id")


def downgrade() -> None:
    op.add_column("jobs", sa.Column("user_id", sa.String(36), nullable=True))
    op.add_column("custom_voices", sa.Column("user_id", sa.String(36), nullable=True))
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
