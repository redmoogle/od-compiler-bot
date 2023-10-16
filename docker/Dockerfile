FROM mcr.microsoft.com/dotnet/sdk:7.0-alpine AS builder

WORKDIR /opendream

COPY ./OpenDream/ .

ARG BULD_CONFIG=Release

RUN dotnet build OpenDreamServer --configuration ${BULD_CONFIG} && \
	dotnet build DMCompiler --configuration ${BULD_CONFIG} && \
    ln -s /opendream/bin/DMCompiler/DMCompiler /usr/bin/ && \
    ln -s /opendream/bin/Content.Server/OpenDreamServer /usr/bin

FROM builder

WORKDIR /app

COPY docker/run.sh .

RUN adduser odcompile -H -D && \
    chown -R odcompile: /app && \
	chown -R odcompile: /opendream/bin

USER odcompile

ENTRYPOINT [ "/bin/sh", "/app/run.sh" ]
