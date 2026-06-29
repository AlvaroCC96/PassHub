FROM node:20-slim AS base
# Not `/app` — the frontend has a real `/app` route, and Vite's dev-server
# static middleware resolves request URLs against the OS filesystem root
# when no project file matches, so a container literally rooted at `/app`
# tries to `read()` its own WORKDIR and crashes with EISDIR.
WORKDIR /workspace
RUN corepack enable

COPY pnpm-workspace.yaml pnpm-lock.yaml package.json tsconfig.base.json ./
COPY packages/shared/package.json packages/shared/package.json
COPY packages/ui/package.json packages/ui/package.json
COPY apps/web/package.json apps/web/package.json
COPY e2e/package.json e2e/package.json
RUN pnpm install --frozen-lockfile

COPY packages packages
COPY apps/web apps/web

# `dev` runs the Vite dev server with HMR — this is the target used by docker-compose.
FROM base AS dev
EXPOSE 5173
CMD ["pnpm", "--filter", "@passhub/web", "dev", "--host"]

FROM base AS build
RUN pnpm --filter @passhub/web build

FROM nginx:1.27-alpine AS runtime
COPY --from=build /workspace/apps/web/dist /usr/share/nginx/html
COPY infra/docker/nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
