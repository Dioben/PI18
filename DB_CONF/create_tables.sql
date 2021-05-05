SELECT 'CREATE DATABASE nntracker owner root'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'nntracker')\gexec
