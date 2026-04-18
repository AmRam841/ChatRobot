FROM ubuntu:22.04

RUN apt update && apt install -y \
    openssh-server python3 python3-pip && \
    mkdir /var/run/sshd

# Create chat user
RUN useradd -m -s /usr/bin/python3 chatuser
RUN echo "chatuser:chatpass" | chpasswd

# Copy chat script
COPY chat.py /home/chatuser/chat.py
RUN chmod +x /home/chatuser/chat.py && chown chatuser:chatuser /home/chatuser/chat.py

# Force SSH logins for chatuser to run chat.py
RUN echo "Match User chatuser\n  ForceCommand /usr/bin/python3 /home/chatuser/chat.py" >> /etc/ssh/sshd_config

# Fix needed SSH settings
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PermitUserEnvironment no/PermitUserEnvironment yes/' /etc/ssh/sshd_config

# Expose SSH
EXPOSE 22

CMD ["/usr/sbin/sshd","-D"]
