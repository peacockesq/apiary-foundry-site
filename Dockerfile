FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY assets /usr/share/nginx/html/assets
COPY about-willie-peacock /usr/share/nginx/html/about-willie-peacock
COPY measurement-engine /usr/share/nginx/html/measurement-engine
COPY growth-os /usr/share/nginx/html/growth-os
COPY five-hives /usr/share/nginx/html/five-hives
COPY paid-media-acquisition /usr/share/nginx/html/paid-media-acquisition
COPY seo-content-marketing /usr/share/nginx/html/seo-content-marketing
COPY conversion-rate-optimization /usr/share/nginx/html/conversion-rate-optimization
COPY lifecycle-crm /usr/share/nginx/html/lifecycle-crm
COPY marketing-measurement-attribution /usr/share/nginx/html/marketing-measurement-attribution
COPY proof /usr/share/nginx/html/proof
COPY trust /usr/share/nginx/html/trust
COPY blog /usr/share/nginx/html/blog
COPY work-with-us /usr/share/nginx/html/work-with-us
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1
