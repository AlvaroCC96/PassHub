FROM node:20-slim AS base
WORKDIR /app
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
COPY --from=build /app/apps/web/dist /usr/share/nginx/html
COPY infra/docker/nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
