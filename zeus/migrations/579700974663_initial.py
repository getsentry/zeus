"""initial

Revision ID: 579700974663
Revises:
Create Date: 2017-07-14 17:53:51.095520

"""
import zeus
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '579700974663'
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
        'organization',
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('name')
    )
    op.create_table(
        'user',
        sa.Column('email', sa.String(length=128), nullable=False),
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('email')
    )
    op.create_table(
        'author',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=128), nullable=True),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'email', name='unq_author_email')
    )
    op.create_index(op.f('ix_author_organization_id'), 'author', ['organization_id'], unique=False)
    op.create_table(
        'identity',
        sa.Column('user_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('external_id', sa.String(length=64), nullable=False),
        sa.Column('provider', sa.String(length=32), nullable=False),
        sa.Column('config', zeus.db.types.json.JSONEncodedDict(), nullable=False),
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id'),
        sa.UniqueConstraint('user_id', 'provider', name='unq_identity_user')
    )
    op.create_index(op.f('ix_identity_user_id'), 'identity', ['user_id'], unique=False)
    op.create_table(
        'organization_access',
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('user_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['organization_id'],
            ['organization.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
        ), sa.PrimaryKeyConstraint('organization_id', 'user_id')
    )
    op.create_table(
        'repository',
        sa.Column('provider', zeus.db.types.enum.StrEnum(), nullable=False),
        sa.Column('external_id', sa.String(length=64), nullable=True),
        sa.Column('url', sa.String(length=200), nullable=False),
        sa.Column('backend', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('status', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('data', zeus.db.types.json.JSONEncodedDict(), nullable=True),
        sa.Column('last_update', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('last_update_attempt', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'provider', 'external_id', name='unq_external_id')
    )
    op.create_index(
        op.f('ix_repository_organization_id'), 'repository', ['organization_id'], unique=False
    )
    op.create_table(
        'project',
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name', name='unq_project_name')
    )
    op.create_index(
        op.f('ix_project_organization_id'), 'project', ['organization_id'], unique=False
    )
    op.create_index(op.f('ix_project_repository_id'), 'project', ['repository_id'], unique=False)
    op.create_table(
        'repository_access',
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('user_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['repository_id'],
            ['repository.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
        ), sa.PrimaryKeyConstraint('repository_id', 'user_id')
    )
    op.create_index(
        op.f('ix_repository_access_organization_id'),
        'repository_access', ['organization_id'],
        unique=False
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
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['author_id'],
            ['author.id'],
        ),
        sa.ForeignKeyConstraint(
            ['committer_id'],
            ['author.id'],
        ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('sha'),
        sa.UniqueConstraint('repository_id', 'sha', name='unq_revision')
    )
    op.create_index(op.f('ix_revision_author_id'), 'revision', ['author_id'], unique=False)
    op.create_index(op.f('ix_revision_committer_id'), 'revision', ['committer_id'], unique=False)
    op.create_index(
        op.f('ix_revision_organization_id'), 'revision', ['organization_id'], unique=False
    )
    op.create_index(op.f('ix_revision_repository_id'), 'revision', ['repository_id'], unique=False)
    op.create_table(
        'hook',
        sa.Column('token', sa.LargeBinary(length=64), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('project_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_hook_organization_id'), 'hook', ['organization_id'], unique=False)
    op.create_index(op.f('ix_hook_project_id'), 'hook', ['project_id'], unique=False)
    op.create_table(
        'patch',
        sa.Column('parent_revision_sha', sa.String(length=40), nullable=False),
        sa.Column('diff', sa.Text(), nullable=False),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['repository_id', 'parent_revision_sha'],
            ['revision.repository_id', 'revision.sha'],
        ),
        sa.ForeignKeyConstraint(['repository_id'], ['repository.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_repo_sha', 'patch', ['repository_id', 'parent_revision_sha'], unique=False)
    op.create_index(op.f('ix_patch_organization_id'), 'patch', ['organization_id'], unique=False)
    op.create_index(op.f('ix_patch_repository_id'), 'patch', ['repository_id'], unique=False)
    op.create_table(
        'source',
        sa.Column('patch_id', zeus.db.types.guid.GUID(), nullable=True),
        sa.Column('revision_sha', sa.String(length=40), nullable=False),
        sa.Column('data', zeus.db.types.json.JSONEncodedDict(), nullable=True),
        sa.Column('author_id', zeus.db.types.guid.GUID(), nullable=True),
        sa.Column('repository_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['author_id'],
            ['author.id'],
        ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
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
    op.create_index(op.f('ix_source_author_id'), 'source', ['author_id'], unique=False)
    op.create_index(op.f('ix_source_organization_id'), 'source', ['organization_id'], unique=False)
    op.create_index(op.f('ix_source_repository_id'), 'source', ['repository_id'], unique=False)
    op.create_table(
        'build',
        sa.Column('source_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('status', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('result', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('date_started', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('date_finished', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('data', zeus.db.types.json.JSONEncodedDict(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(length=64), nullable=True),
        sa.Column('project_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['source.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'number', name='unq_build_number'),
        sa.UniqueConstraint('project_id', 'provider', 'external_id', name='unq_build_provider')
    )
    op.create_index(op.f('ix_build_organization_id'), 'build', ['organization_id'], unique=False)
    op.create_index(op.f('ix_build_project_id'), 'build', ['project_id'], unique=False)
    op.create_index(op.f('ix_build_source_id'), 'build', ['source_id'], unique=False)
    op.create_table(
        'job',
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('build_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(), nullable=True),
        sa.Column('status', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('result', zeus.db.types.enum.Enum(), nullable=False),
        sa.Column('date_started', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('date_finished', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('data', zeus.db.types.json.JSONEncodedDict(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(length=64), nullable=True),
        sa.Column('project_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['build_id'], ['build.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('build_id', 'number', name='unq_job_number'),
        sa.UniqueConstraint('build_id', 'provider', 'external_id', name='unq_job_provider')
    )
    op.create_index(op.f('ix_job_build_id'), 'job', ['build_id'], unique=False)
    op.create_index(op.f('ix_job_organization_id'), 'job', ['organization_id'], unique=False)
    op.create_index(op.f('ix_job_project_id'), 'job', ['project_id'], unique=False)
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
        sa.Column('project_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['job.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', 'filename'),
        sa.UniqueConstraint('job_id', 'filename', name='unq_job_filname')
    )
    op.create_index(
        op.f('ix_filecoverage_organization_id'), 'filecoverage', ['organization_id'], unique=False
    )
    op.create_index(
        op.f('ix_filecoverage_project_id'), 'filecoverage', ['project_id'], unique=False
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
        sa.Column('project_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['job.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id', 'hash', name='unq_testcase_hash')
    )
    op.create_index(
        op.f('ix_testcase_organization_id'), 'testcase', ['organization_id'], unique=False
    )
    op.create_index(op.f('ix_testcase_project_id'), 'testcase', ['project_id'], unique=False)
    op.create_table(
        'artifact',
        sa.Column('job_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('testcase_id', zeus.db.types.guid.GUID(), nullable=True),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('type', zeus.db.types.enum.Enum(), server_default='0', nullable=False),
        sa.Column('file', zeus.db.types.file.File(), nullable=False),
        sa.Column('project_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('organization_id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column('id', zeus.db.types.guid.GUID(), nullable=False),
        sa.Column(
            'date_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['job_id'], ['job.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['testcase_id'], ['testcase.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_artifact_organization_id'), 'artifact', ['organization_id'], unique=False
    )
    op.create_index(op.f('ix_artifact_project_id'), 'artifact', ['project_id'], unique=False)


def downgrade():
    op.execute('DROP FUNCTION IF EXISTS next_item_value(uuid)')
    op.drop_index(op.f('ix_artifact_project_id'), table_name='artifact')
    op.drop_index(op.f('ix_artifact_organization_id'), table_name='artifact')
    op.drop_table('artifact')
    op.drop_index(op.f('ix_testcase_project_id'), table_name='testcase')
    op.drop_index(op.f('ix_testcase_organization_id'), table_name='testcase')
    op.drop_table('testcase')
    op.drop_index(op.f('ix_filecoverage_project_id'), table_name='filecoverage')
    op.drop_index(op.f('ix_filecoverage_organization_id'), table_name='filecoverage')
    op.drop_table('filecoverage')
    op.drop_index(op.f('ix_job_project_id'), table_name='job')
    op.drop_index(op.f('ix_job_organization_id'), table_name='job')
    op.drop_index(op.f('ix_job_build_id'), table_name='job')
    op.drop_table('job')
    op.drop_index(op.f('ix_build_source_id'), table_name='build')
    op.drop_index(op.f('ix_build_project_id'), table_name='build')
    op.drop_index(op.f('ix_build_organization_id'), table_name='build')
    op.drop_table('build')
    op.drop_index(op.f('ix_source_repository_id'), table_name='source')
    op.drop_index(op.f('ix_source_organization_id'), table_name='source')
    op.drop_index(op.f('ix_source_author_id'), table_name='source')
    op.drop_index('idx_source_repo_sha', table_name='source')
    op.drop_table('source')
    op.drop_index(op.f('ix_patch_repository_id'), table_name='patch')
    op.drop_index(op.f('ix_patch_organization_id'), table_name='patch')
    op.drop_index('idx_repo_sha', table_name='patch')
    op.drop_table('patch')
    op.drop_index(op.f('ix_hook_project_id'), table_name='hook')
    op.drop_index(op.f('ix_hook_organization_id'), table_name='hook')
    op.drop_table('hook')
    op.drop_index(op.f('ix_revision_repository_id'), table_name='revision')
    op.drop_index(op.f('ix_revision_organization_id'), table_name='revision')
    op.drop_index(op.f('ix_revision_committer_id'), table_name='revision')
    op.drop_index(op.f('ix_revision_author_id'), table_name='revision')
    op.drop_table('revision')
    op.drop_index(op.f('ix_repository_access_organization_id'), table_name='repository_access')
    op.drop_table('repository_access')
    op.drop_index(op.f('ix_project_repository_id'), table_name='project')
    op.drop_index(op.f('ix_project_organization_id'), table_name='project')
    op.drop_table('project')
    op.drop_index(op.f('ix_repository_organization_id'), table_name='repository')
    op.drop_table('repository')
    op.drop_table('organization_access')
    op.drop_index(op.f('ix_identity_user_id'), table_name='identity')
    op.drop_table('identity')
    op.drop_index(op.f('ix_author_organization_id'), table_name='author')
    op.drop_table('author')
    op.drop_table('user')
    op.drop_table('organization')
    op.drop_table('itemstat')
    op.drop_table('itemsequence')
    op.drop_table('itemoption')
