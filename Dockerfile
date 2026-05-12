FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY assets /usr/share/nginx/html/assets
COPY growth-strategy /usr/share/nginx/html/growth-strategy
COPY acquisition /usr/share/nginx/html/acquisition
COPY conversion /usr/share/nginx/html/conversion
COPY content-seo /usr/share/nginx/html/content-seo
COPY lifecycle /usr/share/nginx/html/lifecycle
COPY measurement-compliance /usr/share/nginx/html/measurement-compliance
COPY about /usr/share/nginx/html/about
COPY case-studies /usr/share/nginx/html/case-studies
COPY work-with-us /usr/share/nginx/html/work-with-us
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1
