"""Add tsvector column for full-text search

Revision ID: e973616e1393
Revises: 265911e4ae85
Create Date: 2025-08-16 17:09:52.208408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e973616e1393'
down_revision: Union[str, Sequence[str], None] = '265911e4ae85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add tsvector column for full-text search (PostgreSQL specific)
    # For SQLite, we'll skip this as it doesn't support tsvector
    connection = op.get_bind()
    
    if connection.dialect.name == 'postgresql':
        # Add search_vector column
        op.add_column(
            'research_documents',
            sa.Column('search_vector', postgresql.TSVECTOR, nullable=True)
        )
        
        # Create GIN index for full-text search
        op.create_index(
            'idx_documents_search_vector',
            'research_documents',
            ['search_vector'],
            postgresql_using='gin'
        )
        
        # Update existing documents to populate search_vector
        op.execute("""
            UPDATE research_documents
            SET search_vector = 
                setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(summary, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(processed_text, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(author, '')), 'D')
        """)
        
        # Create trigger to automatically update search_vector on insert/update
        op.execute("""
            CREATE OR REPLACE FUNCTION documents_search_vector_update() RETURNS trigger AS $$
            BEGIN
                NEW.search_vector :=
                    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                    setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
                    setweight(to_tsvector('english', COALESCE(NEW.processed_text, '')), 'C') ||
                    setweight(to_tsvector('english', COALESCE(NEW.author, '')), 'D');
                RETURN NEW;
            END
            $$ LANGUAGE plpgsql;
        """)
        
        op.execute("""
            CREATE TRIGGER documents_search_vector_trigger
            BEFORE INSERT OR UPDATE ON research_documents
            FOR EACH ROW EXECUTE FUNCTION documents_search_vector_update();
        """)
    else:
        # For SQLite, create a simple FTS5 virtual table for full-text search
        op.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                document_id,
                title,
                processed_text,
                summary,
                author,
                content='research_documents',
                content_rowid='id'
            )
        """)


def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    
    if connection.dialect.name == 'postgresql':
        # Drop trigger and function
        op.execute("DROP TRIGGER IF EXISTS documents_search_vector_trigger ON research_documents")
        op.execute("DROP FUNCTION IF EXISTS documents_search_vector_update()")
        
        # Drop index
        op.drop_index('idx_documents_search_vector', 'research_documents')
        
        # Drop column
        op.drop_column('research_documents', 'search_vector')
    else:
        # Drop SQLite FTS table
        op.execute("DROP TABLE IF EXISTS documents_fts")
