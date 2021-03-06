"""Add completed uploads

Revision ID: 05bf320ed680
Revises: 065886328b03
Create Date: 2021-02-22 16:42:00.690943

"""
import geoalchemy2
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "05bf320ed680"
down_revision = "065886328b03"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "uploads",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("creator_user_id", sa.BigInteger(), nullable=False),
        sa.Column("credit", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["creator_user_id"], ["users.id"], name=op.f("fk_uploads_creator_user_id_users")),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_uploads")),
    )
    op.create_index(op.f("ix_uploads_creator_user_id"), "uploads", ["creator_user_id"], unique=False)
    op.alter_column("initiated_uploads", "user_id", new_column_name="initiator_user_id")
    op.add_column("users", sa.Column("avatar_key", sa.String(), nullable=True))
    op.create_foreign_key(op.f("fk_users_avatar_key_uploads"), "users", "uploads", ["avatar_key"], ["key"])
    op.execute(
        """
        INSERT INTO uploads (creator_user_id, key, filename)
        SELECT
            id,
            substr(avatar_filename, 1, 64),
            avatar_filename
        FROM users
        WHERE avatar_filename IS NOT NULL"""
    )
    op.execute("UPDATE users SET avatar_key = substr(avatar_filename, 1, 64) WHERE avatar_filename IS NOT NULL")
    op.drop_column("users", "avatar_filename")
    op.create_index(
        op.f("ix_initiated_uploads_initiator_user_id"), "initiated_uploads", ["initiator_user_id"], unique=False
    )
    op.drop_index("ix_initiated_uploads_user_id", table_name="initiated_uploads")
    op.add_column("page_versions", sa.Column("photo_key", sa.String(), nullable=True))
    op.create_foreign_key(
        op.f("fk_page_versions_photo_key_uploads"), "page_versions", "uploads", ["photo_key"], ["key"]
    )


def downgrade():
    op.drop_constraint(op.f("fk_page_versions_photo_key_uploads"), "page_versions", type_="foreignkey")
    op.drop_column("page_versions", "photo_key")
    op.create_index("ix_initiated_uploads_user_id", "initiated_uploads", ["initiator_user_id"], unique=False)
    op.drop_index(op.f("ix_initiated_uploads_initiator_user_id"), table_name="initiated_uploads")
    op.drop_constraint(op.f("fk_users_avatar_key_uploads"), "users", type_="foreignkey")
    op.alter_column("initiated_uploads", "initiator_user_id", new_column_name="user_id")
    op.drop_table("uploads")
    op.add_column("users", sa.Column("avatar_filename", sa.VARCHAR(), autoincrement=False, nullable=True))
