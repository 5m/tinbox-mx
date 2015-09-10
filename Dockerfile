FROM 5m/python:3.4-pycharm-onbuild

# TODO: Move to docker-compose
CMD ["python", "-m", "mx.cli.command", "import", "-v", "--subscribe"]
