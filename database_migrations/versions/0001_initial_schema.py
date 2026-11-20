"""Local-only baseline: jobs and custom_voices only."""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

# `sqlalchemy.Enum(JobStatus)` luu TEN member (QUEUED, RUNNING...) vao DB chu
# khong phai value ("queued") - khai bao dung nhu vay de khop du lieu cu do
# create_all tao ra.
JOB_STATUS = sa.Enum("QUEUED", "RUNNING", "DONE", "FAILED", name="jobstatus")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "custom_voices" not in tables:
        op.create_table(
            "custom_voices",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("ref_audio_path", sa.String(1024), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )

    if "jobs" not in tables:
        op.create_table(
            "jobs",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("filename", sa.String(255), nullable=False),
            sa.Column("input_path", sa.String(1024), nullable=False),
            sa.Column("output_dir", sa.String(1024), nullable=False),
            sa.Column("status", JOB_STATUS, nullable=False),
            sa.Column("stage", sa.String(64), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )


def downgrade() -> None:
    op.drop_table("jobs")
    op.drop_table("custom_voices")
    JOB_STATUS.drop(op.get_bind(), checkfirst=True)
