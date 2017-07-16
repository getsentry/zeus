"""initial

Revision ID: 240364a078d9
Revises:
Create Date: 2017-07-13 14:54:12.129389

"""
import zeus
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '240364a078d9'
down_revision = None
branch_labels = ('default', )
depends_on = None

NEXT_ITEM_VALUE_FUNCTION = """
CREATE OR REPLACE FUNCTION next_item_value(uuid) RETURNS int AS $$
DECLARE
  cur_parent_id ALIAS FOR $1;
  next_value int;
BEGIN
  LOOP
    UPDATE itemsequence SET value = value + 1 WHERE parent_id = cur_parent_id
    RETURNING value INTO next_value;
    IF FOUND THEN
      RETURN next_value;
    END IF;

    BEGIN
        INSERT INTO itemsequence (parent_id, value) VALUES (cur_parent_id, 1)
        RETURNING value INTO next_value;
        RETURN next_value;
    EXCEPTION WHEN unique_violation THEN
        -- do nothing
    END;
  END LOOP;
END;
$$ LANGUAGE plpgsql
"""


def upgrade():
    op.create_table(
        'itemsequence',
        sa.Column('parent_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('value', sa.Integer(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('parent_id', 'value')
    )
    op.execute(NEXT_ITEM_VALUE_FUNCTION)
    op.create_table(
        'api_token',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('access_token', sa.String(length=64), nullable=False),
        sa.Column('refresh_token', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('access_token'), sa.UniqueConstraint('refresh_token')
    )
    op.create_table(
        'itemoption',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('item_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id', 'name', name='unq_itemoption_name')
    )
    op.create_table(
        'itemstat',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('item_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id', 'name', name='unq_itemstat_name')
    )
    op.create_table(
        'repository',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('url', sa.String(length=200), nullable=False),
        sa.Column('backend', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('status', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('data', zeus.db.types.json.JSONEncodedDict(), nullable=True),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('last_update', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('last_update_attempt', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('name'), sa.UniqueConstraint('url')
    )
    op.create_table(
        'user',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('email', sa.String(length=128), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('email')
    )
    op.create_table(
        'api_token_repository_access',
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('api_token_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['api_token_id'],
            ['api_token.id'],
        ),
        sa.ForeignKeyConstraint(
            ['repository_id'],
            ['repository.id'],
        ), sa.PrimaryKeyConstraint('repository_id', 'api_token_id')
    )
    op.create_table(
        'author',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=128), nullable=True),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('repository_id', 'email', name='unq_author_email')
    )
    op.create_index(op.f('ix_author_repository_id'), 'author', ['repository_id'], unique=False)
    op.create_table(
        'hook',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('token', sa.LargeBinary(length=64), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_hook_repository_id'), 'hook', ['repository_id'], unique=False)
    op.create_table(
        'identity',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('user_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('external_id', sa.String(length=64), nullable=False),
        sa.Column('provider', sa.String(length=32), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('config', zeus.db.types.json.JSONEncodedDict(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id'),
        sa.UniqueConstraint('user_id', 'provider', name='unq_identity_user')
    )
    op.create_index(op.f('ix_identity_user_id'), 'identity', ['user_id'], unique=False)
    op.create_table(
        'repository_access',
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('user_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['repository_id'],
            ['repository.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
        ), sa.PrimaryKeyConstraint('repository_id', 'user_id')
    )
    op.create_table(
        'revision',
        sa.Column('sha', sa.String(length=40), nullable=False),
        sa.Column('author_id', zeus.db.types.guid.GUID(), nullable=True),
        sa.Column('committer_id', zeus.db.types.guid.GUID(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('parents', postgresql.ARRAY(sa.String(length=40)), nullable=True),
        sa.Column('branches', postgresql.ARRAY(sa.String(length=128)), nullable=True),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column(
            'date_committed',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['author_id'],
            ['author.id'],
        ),
        sa.ForeignKeyConstraint(
            ['committer_id'],
            ['author.id'],
        ),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('sha'),
        sa.UniqueConstraint('repository_id', 'sha', name='unq_revision')
    )
    op.create_index(op.f('ix_revision_author_id'), 'revision', ['author_id'], unique=False)
    op.create_index(op.f('ix_revision_committer_id'), 'revision', ['committer_id'], unique=False)
    op.create_index(op.f('ix_revision_repository_id'), 'revision', ['repository_id'], unique=False)
    op.create_table(
        'patch',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('parent_revision_sha', sa.String(length=40), nullable=False),
        sa.Column('diff', sa.Text(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['repository_id', 'parent_revision_sha'],
            ['revision.repository_id', 'revision.sha'],
        ),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_repo_sha', 'patch', ['repository_id', 'parent_revision_sha'], unique=False)
    op.create_index(op.f('ix_patch_repository_id'), 'patch', ['repository_id'], unique=False)
    op.create_table(
        'source',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('patch_id', zeus.db.types.guid.GUID(), nullable=True),
        sa.Column('revision_sha', sa.String(length=40), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('data', zeus.db.types.json.JSONEncodedDict(), nullable=True),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['patch_id'],
            ['patch.id'],
        ),
        sa.ForeignKeyConstraint(
            ['repository_id', 'revision_sha'],
            ['revision.repository_id', 'revision.sha'],
        ),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('patch_id'),
        sa.UniqueConstraint(
            'repository_id', 'revision_sha', 'patch_id', name='unq_source_revision'
        )
    )
    op.create_index(
        'idx_source_repo_sha', 'source', ['repository_id', 'revision_sha'], unique=False
    )
    op.create_index(op.f('ix_source_repository_id'), 'source', ['repository_id'], unique=False)
    op.create_table(
        'build',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('source_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('author_id', zeus.db.types.guid.GUID(), nullable=True),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('status', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('result', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('date_started', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('date_finished', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('data', zeus.db.types.json.JSONEncodedDict(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(length=64), nullable=True),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['author_id'],
            ['author.id'],
        ),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['source.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('repository_id', 'number', name='unq_build_number'),
        sa.UniqueConstraint('repository_id', 'provider', 'external_id', name='unq_build_provider')
    )
    op.create_index(op.f('ix_build_author_id'), 'build', ['author_id'], unique=False)
    op.create_index(op.f('ix_build_repository_id'), 'build', ['repository_id'], unique=False)
    op.create_index(op.f('ix_build_source_id'), 'build', ['source_id'], unique=False)
    op.create_table(
        'job',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('build_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('status', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('result', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('date_started', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('date_finished', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('data', zeus.db.types.json.JSONEncodedDict(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(length=64), nullable=True),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['build_id'], ['build.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('build_id', 'number', name='unq_job_number'),
        sa.UniqueConstraint('build_id', 'provider', 'external_id', name='unq_job_provider')
    )
    op.create_index(op.f('ix_job_build_id'), 'job', ['build_id'], unique=False)
    op.create_index(op.f('ix_job_repository_id'), 'job', ['repository_id'], unique=False)
    op.create_table(
        'filecoverage',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('job_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('filename', sa.String(length=256), nullable=False),
        sa.Column('data', sa.Text(), nullable=False),
        sa.Column('lines_covered', sa.Integer(), nullable=False),
        sa.Column('lines_uncovered', sa.Integer(), nullable=False),
        sa.Column('diff_lines_covered', sa.Integer(), nullable=False),
        sa.Column('diff_lines_uncovered', sa.Integer(), nullable=False),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['job.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', 'filename'),
        sa.UniqueConstraint('job_id', 'filename', name='unq_job_filname')
    )
    op.create_index(
        op.f('ix_filecoverage_repository_id'), 'filecoverage', ['repository_id'], unique=False
    )
    op.create_table(
        'testcase',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('job_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('hash', sa.String(length=40), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('result', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['job.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id', 'hash', name='unq_testcase_hash')
    )
    op.create_index(op.f('ix_testcase_repository_id'), 'testcase', ['repository_id'], unique=False)
    op.create_table(
        'artifact',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('job_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('testcase_id', zeus.db.types.guid.GUID(), nullable=True),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('type', zeus.db.types.enum.Enum(), server_default='0', nullable=False),
        sa.Column('file', zeus.db.types.file.File(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['job.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['testcase_id'], ['testcase.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artifact_repository_id'), 'artifact', ['repository_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    op.execute('DROP FUNCTION IF EXISTS next_item_value(uuid)')
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_artifact_repository_id'), table_name='artifact')
    op.drop_table('artifact')
    op.drop_index(op.f('ix_testcase_repository_id'), table_name='testcase')
    op.drop_table('testcase')
    op.drop_index(op.f('ix_filecoverage_repository_id'), table_name='filecoverage')
    op.drop_table('filecoverage')
    op.drop_index(op.f('ix_job_repository_id'), table_name='job')
    op.drop_index(op.f('ix_job_build_id'), table_name='job')
    op.drop_table('job')
    op.drop_index(op.f('ix_build_source_id'), table_name='build')
    op.drop_index(op.f('ix_build_repository_id'), table_name='build')
    op.drop_index(op.f('ix_build_author_id'), table_name='build')
    op.drop_table('build')
    op.drop_index(op.f('ix_source_repository_id'), table_name='source')
    op.drop_index('idx_source_repo_sha', table_name='source')
    op.drop_table('source')
    op.drop_index(op.f('ix_patch_repository_id'), table_name='patch')
    op.drop_index('idx_repo_sha', table_name='patch')
    op.drop_table('patch')
    op.drop_index(op.f('ix_revision_repository_id'), table_name='revision')
    op.drop_index(op.f('ix_revision_committer_id'), table_name='revision')
    op.drop_index(op.f('ix_revision_author_id'), table_name='revision')
    op.drop_table('revision')
    op.drop_table('repository_access')
    op.drop_index(op.f('ix_identity_user_id'), table_name='identity')
    op.drop_table('identity')
    op.drop_index(op.f('ix_hook_repository_id'), table_name='hook')
    op.drop_table('hook')
    op.drop_index(op.f('ix_author_repository_id'), table_name='author')
    op.drop_table('author')
    op.drop_table('api_token_repository_access')
    op.drop_table('user')
    op.drop_table('repository')
    op.drop_table('itemstat')
    op.drop_table('itemsequence')
    op.drop_table('itemoption')
    op.drop_table('api_token')
    # ### end Alembic commands ###
