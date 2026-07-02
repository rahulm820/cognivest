# =====================================================================
# Cognivest frontend — development image (Next.js 14 dev server).
#
# Build context is the REPOSITORY ROOT (see docker-compose.yml). Source is
# bind-mounted in dev compose for hot reload; node_modules is kept inside
# the container via an anonymous volume so the host mount does not clobber
# installed dependencies.
# =====================================================================
FROM node:20-slim AS base

ENV NODE_ENV=development

# pnpm is provided via corepack; the version is pinned by the
# "packageManager" field in package.json.
RUN corepack enable

WORKDIR /app

# Install deps first for layer caching. (The scaffold ships no lockfile yet;
# once pnpm-lock.yaml exists it will be picked up automatically.)
COPY frontend/package.json ./
RUN pnpm install

# Copy the rest of the frontend source (overlaid by a bind mount in dev).
COPY frontend/ ./

EXPOSE 3000

CMD ["pnpm", "dev"]
