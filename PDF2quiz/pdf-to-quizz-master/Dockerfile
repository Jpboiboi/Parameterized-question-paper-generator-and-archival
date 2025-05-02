# start by pulling the python image
FROM python:3.9-slim

WORKDIR /app

# copy the requirements file into the image
COPY ./requirements.txt /requirements.txt

# switch working directory
WORKDIR /

ENV OPENAI_API_KEY="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"

EXPOSE 8501

# install the dependencies and packages in the requirements file
RUN pip3 install -r requirements.txt

# copy every content from the local file to the image
COPY ./ /

# configure the container to run in an executed manner
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "ui.py", "--server.headless", "true", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]