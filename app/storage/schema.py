SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS raw_reddit_items (
        source_id TEXT PRIMARY KEY,
        subreddit TEXT NOT NULL,
        item_type TEXT NOT NULL,
        author TEXT NOT NULL,
        title TEXT,
        body TEXT NOT NULL,
        score INTEGER NOT NULL,
        num_comments INTEGER NOT NULL,
        created_utc TEXT NOT NULL,
        permalink TEXT,
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS normalized_reddit_items (
        item_id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL UNIQUE,
        subreddit TEXT NOT NULL,
        item_type TEXT NOT NULL,
        author TEXT NOT NULL,
        text TEXT NOT NULL,
        created_at TEXT NOT NULL,
        url TEXT,
        engagement_score REAL NOT NULL,
        metadata_json TEXT NOT NULL,
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ticker_mentions (
        mention_id TEXT PRIMARY KEY,
        item_id TEXT NOT NULL,
        ticker TEXT NOT NULL,
        company_name TEXT,
        mention_count INTEGER NOT NULL,
        confidence REAL NOT NULL,
        extraction_method TEXT NOT NULL,
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS market_snapshots (
        ticker TEXT NOT NULL,
        as_of_date TEXT NOT NULL,
        close REAL NOT NULL,
        volume INTEGER NOT NULL,
        market_cap REAL,
        return_1d REAL,
        return_3d REAL,
        return_5d REAL,
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (ticker, as_of_date)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_stock_aggregates (
        run_date TEXT NOT NULL,
        ticker TEXT NOT NULL,
        mention_count INTEGER NOT NULL,
        unique_authors INTEGER NOT NULL,
        weighted_sentiment REAL NOT NULL,
        anomaly_score REAL NOT NULL,
        baseline_mentions REAL NOT NULL,
        discussion_count INTEGER NOT NULL,
        source_item_ids_json TEXT NOT NULL,
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (run_date, ticker)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS classifications (
        classification_id TEXT PRIMARY KEY,
        ticker TEXT NOT NULL,
        item_id TEXT,
        discussion_type TEXT NOT NULL,
        confidence REAL NOT NULL,
        summary TEXT NOT NULL,
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS report_rows (
        run_date TEXT NOT NULL,
        ticker TEXT NOT NULL,
        company_name TEXT,
        anomaly_score REAL NOT NULL,
        mention_count INTEGER NOT NULL,
        unique_authors INTEGER NOT NULL,
        weighted_sentiment REAL NOT NULL,
        discussion_type TEXT NOT NULL,
        lead_lag_label TEXT NOT NULL,
        pump_risk_score REAL NOT NULL,
        signal_quality REAL NOT NULL,
        return_1d REAL,
        return_3d REAL,
        short_explanation TEXT NOT NULL,
        suggested_action TEXT NOT NULL,
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (run_date, ticker)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS run_metadata (
        run_id TEXT PRIMARY KEY,
        run_date TEXT NOT NULL,
        stage TEXT NOT NULL,
        status TEXT NOT NULL,
        started_at TEXT NOT NULL,
        ended_at TEXT,
        processed_count INTEGER NOT NULL DEFAULT 0,
        error_message TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_normalized_created_at ON normalized_reddit_items(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_mentions_ticker ON ticker_mentions(ticker)",
    "CREATE INDEX IF NOT EXISTS idx_market_as_of_date ON market_snapshots(as_of_date)",
    "CREATE INDEX IF NOT EXISTS idx_aggregates_run_date ON daily_stock_aggregates(run_date)",
    "CREATE INDEX IF NOT EXISTS idx_run_metadata_run_date ON run_metadata(run_date)",
]
