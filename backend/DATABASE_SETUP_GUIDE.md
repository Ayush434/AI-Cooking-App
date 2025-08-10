# Google Cloud SQL Setup Guide for AI Cooking App

## Overview
This guide will help you connect your AI Cooking App to Google Cloud SQL PostgreSQL database.

## Prerequisites
- Google Cloud Project with billing enabled
- Google Cloud SDK installed (`gcloud` command)
- Python 3.8+ environment

## Step 1: Set Up Google Cloud SQL

### 1.1 Enable Required APIs
```bash
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

### 1.2 Create PostgreSQL Instance
```bash
# Replace YOUR_PROJECT_ID with your actual project ID
export PROJECT_ID="your-project-id-here"

gcloud sql instances create ai-cooking-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=10GB \
    --backup-start-time=02:00 \
    --project=$PROJECT_ID
```

### 1.3 Set Database Password
```bash
gcloud sql users set-password postgres \
    --instance=ai-cooking-db \
    --password=YOUR_SECURE_PASSWORD \
    --project=$PROJECT_ID
```

### 1.4 Create Application Database
```bash
gcloud sql databases create ai_cooking_app \
    --instance=ai-cooking-db \
    --project=$PROJECT_ID
```

### 1.5 Configure Network Access (for local development)
```bash
# Get your external IP
curl ifconfig.me

# Add your IP to authorized networks (replace with your IP)
gcloud sql instances patch ai-cooking-db \
    --authorized-networks=YOUR_EXTERNAL_IP/32 \
    --project=$PROJECT_ID
```

## Step 2: Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-in-production

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=capstone-ai-cooking-app-5692391a2963.json

# Google Cloud SQL Configuration
CLOUD_SQL_PROJECT_ID=your-project-id-here
CLOUD_SQL_REGION=us-central1
CLOUD_SQL_INSTANCE_NAME=ai-cooking-db
CLOUD_SQL_DATABASE_NAME=ai_cooking_app
CLOUD_SQL_USERNAME=postgres
CLOUD_SQL_PASSWORD=your-secure-password

# AI Service API Keys (existing)
HF_ACCESS_TOKEN=your-huggingface-token
```

## Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 4: Initialize Database

```bash
# Run the database initialization script
python init_db.py
```

This will:
- Create all necessary database tables
- Add sample ingredients for testing
- Verify the connection works

## Step 5: Test the Connection

```bash
# Start the Flask application
python run.py
```

Visit `http://localhost:5000/api/recipes/health` to verify the API is working.

## Step 6: Database Migrations (Future Updates)

When you need to update the database schema:

```bash
# Initialize migrations (only once)
flask db init

# Create a migration
flask db migrate -m "Description of changes"

# Apply the migration
flask db upgrade
```

## Alternative: Local Development Database

If you prefer to use a local PostgreSQL database for development:

1. Install PostgreSQL locally
2. Create a database: `createdb ai_cooking_app`
3. Set environment variable: `DATABASE_URL=postgresql://username:password@localhost:5432/ai_cooking_app`
4. Comment out the Cloud SQL variables in `.env`

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Ensure your IP is added to authorized networks
   - Check firewall settings

2. **Authentication Failed**
   - Verify your password is correct
   - Ensure the user exists: `gcloud sql users list --instance=ai-cooking-db`

3. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path and virtual environment

4. **Cloud SQL Connector Issues**
   - Ensure `GOOGLE_APPLICATION_CREDENTIALS` path is correct
   - Verify service account has Cloud SQL Client role

### Useful Commands

```bash
# Check instance status
gcloud sql instances describe ai-cooking-db

# Connect to database directly
gcloud sql connect ai-cooking-db --user=postgres --database=ai_cooking_app

# View logs
gcloud sql instances describe ai-cooking-db --format="value(logConfig.enabled)"
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use strong passwords** for database users
3. **Restrict network access** to specific IPs
4. **Enable SSL** for production environments
5. **Regular backups** are enabled by default

## Cost Optimization

- **Development**: Use `db-f1-micro` tier (included in free tier)
- **Production**: Scale up to `db-n1-standard-1` or higher
- **Storage**: Start with 10GB SSD, auto-increase enabled
- **Backups**: 7-day retention by default

## Next Steps

1. **Integrate with existing endpoints**: Update your recipe routes to save/load from database
2. **Add user authentication**: Implement user registration and login
3. **Enhance recipe storage**: Save AI-generated recipes for future reference
4. **Add search functionality**: Use PostgreSQL full-text search for recipes
5. **Implement caching**: Consider Redis for frequently accessed data

## Support

- [Google Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)