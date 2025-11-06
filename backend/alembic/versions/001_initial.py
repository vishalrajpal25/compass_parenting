"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2025-11-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension (if available)
    try:
        op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    except Exception:
        # PostGIS not available - continue without it
        pass

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)

    # Create families table
    op.create_table(
        'families',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('location', Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='America/Los_Angeles'),
        sa.Column('budget_monthly', sa.Integer(), nullable=True),
        sa.Column('calendar_ics_url', sa.Text(), nullable=True),
        sa.Column('partner_email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_families_owner_id'), 'families', ['owner_id'], unique=False)
    op.create_index(op.f('ix_families_created_at'), 'families', ['created_at'], unique=False)
    op.execute("CREATE INDEX IF NOT EXISTS idx_families_location ON families USING gist (location)")

    # Create providers table
    op.create_table(
        'providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('organization_type', sa.String(length=50), nullable=True),
        sa.Column('website', sa.Text(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('data_source_url', sa.Text(), nullable=True),
        sa.Column('data_source_type', sa.String(length=20), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_providers_name'), 'providers', ['name'], unique=False)
    op.create_index(op.f('ix_providers_created_at'), 'providers', ['created_at'], unique=False)

    # Create venues table
    op.create_table(
        'venues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('location', Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('geohash', sa.String(length=12), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('website', sa.Text(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('wheelchair_accessible', sa.Boolean(), nullable=True),
        sa.Column('parking_available', sa.Boolean(), nullable=True),
        sa.Column('public_transit_accessible', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_venues_geohash'), 'venues', ['geohash'], unique=False)
    op.create_index(op.f('ix_venues_created_at'), 'venues', ['created_at'], unique=False)
    op.execute("CREATE INDEX IF NOT EXISTS idx_venues_location ON venues USING gist (location)")

    # Create child_profiles table
    op.create_table(
        'child_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=False),
        sa.Column('temperament', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('primary_goal', sa.String(length=100), nullable=True),
        sa.Column('secondary_goal', sa.String(length=100), nullable=True),
        sa.Column('tertiary_goal', sa.String(length=100), nullable=True),
        sa.Column('custom_goals', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('constraints', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_activity_types', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_child_profiles_family_id'), 'child_profiles', ['family_id'], unique=False)
    op.create_index(op.f('ix_child_profiles_created_at'), 'child_profiles', ['created_at'], unique=False)
    op.create_index('idx_child_profiles_temperament', 'child_profiles', ['temperament'], postgresql_using='gin', unique=False)

    # Create activities table
    op.create_table(
        'activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('venue_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('activity_type', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('rrule', sa.Text(), nullable=True),
        sa.Column('days_of_week', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('min_age', sa.Integer(), nullable=True),
        sa.Column('max_age', sa.Integer(), nullable=True),
        sa.Column('age_range_text', sa.String(length=100), nullable=True),
        sa.Column('price_cents', sa.Integer(), nullable=True),
        sa.Column('price_text', sa.String(length=100), nullable=True),
        sa.Column('has_scholarship', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('registration_url', sa.Text(), nullable=True),
        sa.Column('registration_deadline', sa.Date(), nullable=True),
        sa.Column('registration_status', sa.String(length=20), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('canon_hash', sa.String(length=64), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('last_verified', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('canon_hash')
    )
    op.create_index(op.f('ix_activities_provider_id'), 'activities', ['provider_id'], unique=False)
    op.create_index(op.f('ix_activities_venue_id'), 'activities', ['venue_id'], unique=False)
    op.create_index(op.f('ix_activities_name'), 'activities', ['name'], unique=False)
    op.create_index(op.f('ix_activities_start_date'), 'activities', ['start_date'], unique=False)
    op.create_index(op.f('ix_activities_canon_hash'), 'activities', ['canon_hash'], unique=False)
    op.create_index(op.f('ix_activities_created_at'), 'activities', ['created_at'], unique=False)
    op.create_index('idx_activities_attributes', 'activities', ['attributes'], postgresql_using='gin', unique=False)

    # Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('child_profile_id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('total_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('fit_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('practical_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('goals_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('score_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tier', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('why_good_fit', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('considerations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('future_benefits', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['child_profile_id'], ['child_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recommendations_family_id'), 'recommendations', ['family_id'], unique=False)
    op.create_index(op.f('ix_recommendations_child_profile_id'), 'recommendations', ['child_profile_id'], unique=False)
    op.create_index(op.f('ix_recommendations_activity_id'), 'recommendations', ['activity_id'], unique=False)
    op.create_index(op.f('ix_recommendations_total_score'), 'recommendations', ['total_score'], unique=False)
    op.create_index(op.f('ix_recommendations_tier'), 'recommendations', ['tier'], unique=False)
    op.create_index(op.f('ix_recommendations_created_at'), 'recommendations', ['created_at'], unique=False)

    # Create scraper_logs table
    op.create_table(
        'scraper_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('scraper_type', sa.String(length=20), nullable=False),
        sa.Column('run_started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('run_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('activities_found', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('activities_passed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('activities_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duplicates_found', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pass_rate', sa.Float(), nullable=True),
        sa.Column('http_status', sa.Integer(), nullable=True),
        sa.Column('errors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('warnings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('validation_failures', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraper_logs_provider_id'), 'scraper_logs', ['provider_id'], unique=False)
    op.create_index(op.f('ix_scraper_logs_run_started_at'), 'scraper_logs', ['run_started_at'], unique=False)
    op.create_index(op.f('ix_scraper_logs_created_at'), 'scraper_logs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('scraper_logs')
    op.drop_table('recommendations')
    op.drop_table('activities')
    op.drop_table('child_profiles')
    op.drop_table('venues')
    op.drop_table('providers')
    op.drop_table('families')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS postgis')

