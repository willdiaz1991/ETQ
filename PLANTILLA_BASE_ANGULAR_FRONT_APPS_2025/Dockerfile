FROM node:24.16.0 AS build
LABEL stage=builder

ENV CI=true \
    PNPM_HOME=/pnpm \
    PATH=/pnpm:$PATH
RUN corepack enable && corepack prepare pnpm@11.5.0 --activate

WORKDIR /front

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN --mount=type=cache,target=/pnpm/store pnpm install --frozen-lockfile

COPY . .

ARG BASE_PATH=/
ARG ENVIRONMENT=LOCAL
RUN case "$ENVIRONMENT" in \
      DEV)   NG_CONFIG=development ;; \
      QA)    NG_CONFIG=qa ;; \
      PROD)  NG_CONFIG=production ;; \
      LOCAL) NG_CONFIG=local ;; \
      DOCKER) NG_CONFIG=docker ;; \
      *)     NG_CONFIG="$ENVIRONMENT" ;; \
    esac && \
    pnpm exec ng build --configuration="$NG_CONFIG" \
      --base-href="$BASE_PATH" --deploy-url="$BASE_PATH"

FROM nginx:stable-alpine

ARG BASE_PATH=/

RUN chgrp -R 0 /etc/nginx /var/cache/nginx /var/run && \
    chmod -R g=u /etc/nginx /var/cache/nginx /var/run && \
    sed -i 's,/var/run/nginx.pid,/tmp/nginx.pid,' /etc/nginx/nginx.conf && \
    sed -i '/^user /d' /etc/nginx/nginx.conf && \
    rm -f /etc/nginx/conf.d/default.conf \
          /usr/share/nginx/html/index.html \
          /usr/share/nginx/html/50x.html

COPY config/nginx.conf /etc/nginx/conf.d/default.conf
RUN sed -i "s,__BASE_PATH__,${BASE_PATH},g" /etc/nginx/conf.d/default.conf

COPY --from=build --chown=1001:0 /front/dist/browser "/usr/share/nginx/html${BASE_PATH}"

EXPOSE 8080
USER 1001

ENTRYPOINT ["nginx", "-g", "daemon off;"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
