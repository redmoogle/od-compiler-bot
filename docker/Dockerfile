FROM mcr.microsoft.com/dotnet/sdk AS builder

WORKDIR /opendream

COPY ./OpenDream/ .

RUN dotnet build && \
    ln -s /opendream/DMCompiler/bin/Debug/net7.0/DMCompiler /usr/bin/ && \
    ln -s /opendream/bin/Content.Server/OpenDreamServer /usr/bin

FROM builder

WORKDIR /app

COPY docker/run.sh .

RUN useradd odcompile && \
    chown -R odcompile: /app && \
	chown -R odcompile: /opendream/bin

USER odcompile

ENTRYPOINT [ "/bin/bash", "/app/run.sh" ]
