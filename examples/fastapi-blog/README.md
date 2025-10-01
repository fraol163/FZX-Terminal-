# FastAPI Blog Example

## Generated With
- Command: `build describe 'Build a FastAPI server for a simple blog with user authentication, post creation, and basic CRUD operations'`
- Model: Claude-3-Sonnet (example)
- Time: 4.1 seconds
- Date: 2025-10-01

## What Was Generated
- FastAPI server with authentication
- User and Post models
- CRUD operations
- JWT token authentication
- API documentation

## Run This Example
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## Features Implemented
- ✅ User registration and login
- ✅ JWT token authentication
- ✅ Create, read, update, delete posts
- ✅ User-specific post ownership
- ✅ Automatic API documentation
- ✅ Password hashing
- ✅ Request validation

## API Endpoints
- `POST /register` - Create new user
- `POST /login` - User authentication
- `GET /posts` - List all posts
- `POST /posts` - Create new post (auth required)
- `GET /posts/{id}` - Get specific post
- `PUT /posts/{id}` - Update post (auth required)
- `DELETE /posts/{id}` - Delete post (auth required)

## Notes
This example shows how FZX-Terminal generates production-ready API structure with proper authentication and documentation.