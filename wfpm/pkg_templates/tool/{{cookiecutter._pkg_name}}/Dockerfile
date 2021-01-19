FROM {{ cookiecutter.docker_base_image }}

LABEL org.opencontainers.image.source https://{{ cookiecutter._repo_server }}/{{ cookiecutter._repo_account }}/{{ cookiecutter._repo_name }}

ENV PATH="/tools:${PATH}"

COPY *.py /tools/

CMD ["/bin/bash"]
