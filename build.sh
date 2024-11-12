#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if pip3 is available, otherwise use pip
if command_exists pip3; then
    PIP=pip3
else
    PIP=pip
fi

# Check if python3 is available, otherwise use python
if command_exists python3; then
    PYTHON=python3
else
    PYTHON=python
fi

# Install Homebrew if not already installed (for macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command_exists brew; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    # Install PostgreSQL using Homebrew
    if ! command_exists pg_config; then
        echo "Installing PostgreSQL..."
        brew install postgresql
    fi
fi

# Function to update PATH with PostgreSQL binaries
update_postgres_path() {
    # Common PostgreSQL installation locations on macOS
    POSTGRES_PATHS=(
        "/opt/homebrew/opt/postgresql@14/bin"  # Homebrew on Apple Silicon
        "/usr/local/opt/postgresql@14/bin"     # Homebrew on Intel
        "/Applications/Postgres.app/Contents/Versions/latest/bin"  # Postgres.app
        "/Library/PostgreSQL/*/bin"            # EnterpriseDB installer
    )

    for pg_path in "${POSTGRES_PATHS[@]}"; do
        if [ -d "$(echo $pg_path)" ]; then
            echo "Adding PostgreSQL binaries to PATH: $pg_path"
            export PATH="$(echo $pg_path):$PATH"
            return 0
        fi
    done
    return 1
}

# Check if pg_config exists, if not try to find PostgreSQL installation
if ! command_exists pg_config; then
    echo "pg_config not found in PATH. Attempting to locate PostgreSQL installation..."
    if ! update_postgres_path; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "Installing PostgreSQL using Homebrew..."
            brew install postgresql
        else
            echo "Error: pg_config not found. Please install PostgreSQL and ensure it's in your PATH."
            exit 1
        fi
    fi
fi

# Verify pg_config is now available
if ! command_exists pg_config; then
    echo "Error: pg_config still not found. Please ensure PostgreSQL is properly installed."
    echo "Current PATH: $PATH"
    exit 1
fi

# Install required packages
echo "Installing required packages..."
$PIP install psycopg2-binary flask-migrate

# Run database migrations
echo "Running database migrations..."
$PYTHON -m flask db upgrade

echo "Build process completed successfully."