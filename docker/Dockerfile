FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS builder

WORKDIR /opendream

COPY ./OpenDream/ .

ARG BULD_CONFIG=Release

ARG TAR_URL=https://github.com/OpenDreamProject/OpenDream/releases/tag/latest

RUN apk add --no-cache wget tar

RUN wget $TAR_URL -O binaries.tar.gz && \
    tar -xzf binaries.tar.gz --strip-components=1 && \
    rm binaries.tar.gz

RUN ln -s /opendream/bin/DMCompiler/DMCompiler /usr/bin/ && \
    ln -s /opendream/bin/Content.Server/OpenDreamServer /usr/bin

FROM builder

WORKDIR /app

COPY docker/run.sh .

RUN adduser odcompile -H -D && \
    chown -R odcompile: /app && \
	chown -R odcompile: /opendream/bin

USER odcompile

ENTRYPOINT [ "/bin/sh", "/app/run.sh" ]
