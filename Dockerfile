# Build and run KinanCity-core without requiring a host Maven or Java install.
FROM maven:3.9.16-eclipse-temurin-21 AS build
WORKDIR /src
COPY . .
RUN mvn -B -Dmaven.repo.local=/root/.m2/repository -Dmaven.compiler.proc=full \
    -pl KinanCity-core -am -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /opt/kinancity
COPY --from=build /src/KinanCity-core/target/kinancity-core-2.1.19-SNAPSHOT.jar ./kinancity-core.jar
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod 0755 ./docker-entrypoint.sh

# Defaults are deliberately local and contain no credentials. Override these at runtime.
ENV CAPTCHA_PROVIDER=local \
    KC_CAPTCHA_VALUE=DUMMY_LOCAL_KEY \
    PROXIES= \
    SKIP_PROXY_CHECK=true

ENTRYPOINT ["/opt/kinancity/docker-entrypoint.sh"]
