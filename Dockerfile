FROM python:3.9.5

LABEL maintainer="cjr2755"

# Install the webdriver into a folder in the $PATH
# So it is automatically found by the program
COPY geckodriver /usr/bin

# Put all contents into this directory 
WORKDIR /usr/src/app

# Install the nessecary packages
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all remaining files
COPY . .

# Run the program
CMD [ "python", "./bot_driver.py" ]