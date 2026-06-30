FROM public.ecr.aws/lambda/python:3.11

ARG HANDLER=blockbuster.handlers.backtest_handler.handler

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.yaml ${LAMBDA_TASK_ROOT}/
COPY src/ ${LAMBDA_TASK_ROOT}/src/

ENV PYTHONPATH=${LAMBDA_TASK_ROOT}/src
ENV CONFIG_PATH=${LAMBDA_TASK_ROOT}/config.yaml

CMD ["${HANDLER}"]
