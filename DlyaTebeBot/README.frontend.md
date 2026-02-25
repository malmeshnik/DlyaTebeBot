Frontend Docker / nginx

Build and run the miniapp frontend (production) locally:

1. Build the image and start the container:

```bash
docker compose -f docker-compose.frontend.yml up --build -d
```

2. Open http://localhost:3000

Notes:
- The compose file builds from `frontend/` and serves the `dist` output with nginx.
- If your Vite build outputs to a different folder, update the `Dockerfile` COPY path.
